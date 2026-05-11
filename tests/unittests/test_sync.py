import unittest
from unittest.mock import patch, MagicMock, call
import singer
from tap_amazon_ads.streams.abstracts import IncrementalStream, FullTableStream
from tap_amazon_ads.sync import sync, update_currently_syncing, write_schema


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _mock_catalog_entry(stream_name, selected=True):
    entry = MagicMock()
    entry.stream = stream_name
    entry.tap_stream_id = stream_name
    entry.schema = MagicMock()
    entry.schema.to_dict.return_value = {
        "properties": {
            "id": {"type": ["null", "string"]},
            "lastUpdateDateTime": {"type": ["null", "string"], "format": "date-time"},
        }
    }
    entry.metadata = [
        {"breadcrumb": [], "metadata": {"selected": selected, "table-key-properties": ["id"]}}
    ]
    return entry


def _mock_catalog(stream_names):
    catalog = MagicMock()
    entries = {name: _mock_catalog_entry(name) for name in stream_names}
    catalog.get_selected_streams.return_value = [entries[n] for n in stream_names]
    catalog.get_stream.side_effect = lambda name: entries.get(name, _mock_catalog_entry(name))
    return catalog


def _make_incremental_stream_cls():
    """Return a lightweight IncrementalStream subclass for use in sync tests."""

    class ConcreteIncremental(IncrementalStream):
        tap_stream_id = "test_incremental"
        key_properties = ["id"]
        replication_keys = ["lastUpdateDateTime"]
        replication_method = "INCREMENTAL"
        http_method = "POST"
        data_key = "items"
        path = "items/list"
        pagination_in = "body"
        parent = ""
        children = []

    return ConcreteIncremental


def _make_full_table_stream_cls():
    class ConcreteFull(FullTableStream):
        tap_stream_id = "test_full"
        key_properties = ["id"]
        replication_keys = []
        replication_method = "FULL_TABLE"
        http_method = "GET"
        data_key = "items"
        path = "items"
        pagination_in = None
        parent = ""
        children = []

    return ConcreteFull


# ---------------------------------------------------------------------------
# update_currently_syncing tests
# ---------------------------------------------------------------------------

class TestUpdateCurrentlySyncing(unittest.TestCase):

    @patch("tap_amazon_ads.sync.singer.write_state")
    def test_sets_currently_syncing(self, mock_write):
        state = {}
        update_currently_syncing(state, "my_stream")
        self.assertEqual(state.get("currently_syncing"), "my_stream")
        mock_write.assert_called_once_with(state)

    @patch("tap_amazon_ads.sync.singer.write_state")
    def test_clears_currently_syncing_when_none(self, mock_write):
        state = {"currently_syncing": "my_stream"}
        update_currently_syncing(state, None)
        self.assertNotIn("currently_syncing", state)
        mock_write.assert_called_once_with(state)

    @patch("tap_amazon_ads.sync.singer.write_state")
    def test_write_state_called_on_set(self, mock_write):
        state = {}
        update_currently_syncing(state, "stream_a")
        mock_write.assert_called_once()

    @patch("tap_amazon_ads.sync.singer.write_state")
    def test_write_state_called_on_clear(self, mock_write):
        state = {"currently_syncing": "stream_a"}
        update_currently_syncing(state, None)
        mock_write.assert_called_once()


# ---------------------------------------------------------------------------
# IncrementalStream.sync tests
# ---------------------------------------------------------------------------

class TestIncrementalStreamSync(unittest.TestCase):
    """Tests for IncrementalStream.sync() behaviour."""

    def _make_stream(self, records, config=None):
        with patch("tap_amazon_ads.streams.abstracts.metadata.to_map") as mock_to_map:
            mock_to_map.return_value = {(): {"selected": True}}
            client = MagicMock()
            client.config = config or {"start_date": "2024-01-01T00:00:00Z"}
            client.base_url = "https://advertising.amazon.com"
            catalog_entry = _mock_catalog_entry("test_incremental")
            StreamCls = _make_incremental_stream_cls()
            stream = StreamCls(client=client, catalog=catalog_entry)
            stream.child_to_sync = []
            stream.url_endpoint = "https://advertising.amazon.com/items/list"

        with patch.object(stream, "get_records", return_value=iter(records)):
            return stream

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_syncs_records_newer_than_bookmark(self, mock_counter, mock_write_record):
        """Only records >= bookmark should be written."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        records = [
            {"id": "1", "lastUpdateDateTime": "2024-06-01T00:00:00Z"},  # after bookmark
            {"id": "2", "lastUpdateDateTime": "2023-12-01T00:00:00Z"},  # before bookmark
        ]
        state = {"bookmarks": {"test_incremental": {"lastUpdateDateTime": "2024-01-01T00:00:00Z"}}}
        stream = self._make_stream(records)

        with patch.object(stream, "get_records", return_value=iter(records)), \
             singer.Transformer() as transformer:
            stream.sync(state=state, transformer=transformer)

        # Only record 1 is newer than the bookmark
        self.assertEqual(mock_write_record.call_count, 1)
        written_record = mock_write_record.call_args[0][1]
        self.assertEqual(written_record["id"], "1")

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_bookmark_advances_after_sync(self, mock_counter, mock_write_record):
        """After sync the bookmark should advance to the max record date."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        records = [
            {"id": "1", "lastUpdateDateTime": "2025-03-01T00:00:00Z"},
            {"id": "2", "lastUpdateDateTime": "2025-06-15T00:00:00Z"},
        ]
        state = {"bookmarks": {"test_incremental": {"lastUpdateDateTime": "2025-01-01T00:00:00Z"}}}
        stream = self._make_stream(records)

        with patch.object(stream, "get_records", return_value=iter(records)), \
             singer.Transformer() as transformer:
            _, final_state = stream.sync(state=state, transformer=transformer)

        bk = final_state["bookmarks"]["test_incremental"]["lastUpdateDateTime"]
        self.assertEqual(bk, "2025-06-15T00:00:00Z")

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_zero_records_returns_zero_count(self, mock_counter, mock_write_record):
        """A sync with no records should return 0 and not write any records."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_ctx.value = 0
        mock_counter.return_value = mock_ctx

        state = {}
        stream = self._make_stream([])

        with patch.object(stream, "get_records", return_value=iter([])), \
             singer.Transformer() as transformer:
            count, _ = stream.sync(state=state, transformer=transformer)

        mock_write_record.assert_not_called()
        self.assertEqual(count, 0)

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_child_sync_called_for_each_parent_record(self, mock_counter, mock_write_record):
        """child.sync() must be called once per qualifying parent record."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        records = [
            {"id": "1", "lastUpdateDateTime": "2025-01-01T00:00:00Z"},
            {"id": "2", "lastUpdateDateTime": "2025-02-01T00:00:00Z"},
        ]
        state = {"bookmarks": {"test_incremental": {"lastUpdateDateTime": "2024-01-01T00:00:00Z"}}}
        stream = self._make_stream(records)

        mock_child = MagicMock()
        stream.child_to_sync = [mock_child]

        with patch.object(stream, "get_records", return_value=iter(records)), \
             singer.Transformer() as transformer:
            stream.sync(state=state, transformer=transformer)

        self.assertEqual(mock_child.sync.call_count, 2)

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_modify_object_called_for_each_record(self, mock_counter, mock_write_record):
        """modify_object should be invoked for every record during sync."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        records = [
            {"id": "1", "lastUpdateDateTime": "2025-01-01T00:00:00Z"},
            {"id": "2", "lastUpdateDateTime": "2025-02-01T00:00:00Z"},
        ]
        state = {}
        stream = self._make_stream(records)

        with patch.object(stream, "get_records", return_value=iter(records)), \
             patch.object(stream, "modify_object", wraps=stream.modify_object) as mock_modify, \
             singer.Transformer() as transformer:
            stream.sync(state=state, transformer=transformer)

        self.assertEqual(mock_modify.call_count, 2)


# ---------------------------------------------------------------------------
# FullTableStream.sync tests
# ---------------------------------------------------------------------------

class TestFullTableStreamSync(unittest.TestCase):
    """Tests for FullTableStream.sync() behaviour."""

    def _make_stream(self, records):
        with patch("tap_amazon_ads.streams.abstracts.metadata.to_map") as mock_to_map:
            mock_to_map.return_value = {(): {"selected": True}}
            client = MagicMock()
            client.config = {"start_date": "2024-01-01T00:00:00Z"}
            client.base_url = "https://advertising.amazon.com"
            catalog_entry = _mock_catalog_entry("test_full")
            StreamCls = _make_full_table_stream_cls()
            stream = StreamCls(client=client, catalog=catalog_entry)
            stream.child_to_sync = []
            stream.url_endpoint = "https://advertising.amazon.com/items"
        return stream

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_all_records_written(self, mock_counter, mock_write_record):
        """Full table sync writes every record regardless of timestamp."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        records = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        stream = self._make_stream(records)

        with patch.object(stream, "get_records", return_value=iter(records)), \
             singer.Transformer() as transformer:
            stream.sync(state={}, transformer=transformer)

        self.assertEqual(mock_write_record.call_count, 3)

    @patch("tap_amazon_ads.streams.abstracts.write_record")
    @patch("tap_amazon_ads.streams.abstracts.metrics.record_counter")
    def test_does_not_update_state(self, mock_counter, mock_write_record):
        """Full table sync returns unmodified state (no bookmarking)."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_ctx

        initial_state = {"bookmarks": {"other_stream": {"field": "value"}}}
        records = [{"id": "1"}]
        stream = self._make_stream(records)

        with patch.object(stream, "get_records", return_value=iter(records)), \
             singer.Transformer() as transformer:
            _, final_state = stream.sync(state=initial_state, transformer=transformer)

        # Full table streams must not add any new bookmark keys
        self.assertEqual(final_state.get("bookmarks", {}), {"other_stream": {"field": "value"}})


# ---------------------------------------------------------------------------
# sync() orchestration tests
# ---------------------------------------------------------------------------

class TestSyncOrchestration(unittest.TestCase):
    """Tests for the top-level sync() function in tap_amazon_ads.sync."""

    def _base_config(self):
        return {"start_date": "2024-01-01T00:00:00Z"}

    @patch("tap_amazon_ads.sync.singer.write_state")
    @patch("tap_amazon_ads.sync.update_currently_syncing")
    @patch("tap_amazon_ads.sync.write_schema")
    @patch("tap_amazon_ads.sync.STREAMS")
    def test_sync_iterates_selected_streams(
        self, mock_streams, mock_write_schema, mock_update_sync, mock_write_state
    ):
        """sync() should call stream.sync() for every selected, non-child stream."""
        mock_stream_instance = MagicMock()
        mock_stream_instance.parent = ""
        mock_stream_instance.sync.return_value = (5, {})
        mock_stream_cls = MagicMock(return_value=mock_stream_instance)
        mock_streams.__contains__.side_effect = lambda item: True
        mock_streams.__getitem__.side_effect = lambda key: mock_stream_cls

        catalog = _mock_catalog(["test_stream"])
        client = MagicMock()
        state = {}

        with patch("tap_amazon_ads.sync.singer.Transformer"):
            sync(client, self._base_config(), catalog, state)

        mock_stream_instance.sync.assert_called_once()

    @patch("tap_amazon_ads.sync.singer.write_state")
    @patch("tap_amazon_ads.sync.update_currently_syncing")
    @patch("tap_amazon_ads.sync.write_schema")
    @patch("tap_amazon_ads.sync.STREAMS")
    def test_sync_skips_child_streams_at_top_level(
        self, mock_streams, mock_write_schema, mock_update_sync, mock_write_state
    ):
        """Child streams (parent != '') must not be synced directly at the top level."""
        # parent_stream has no parent; child_stream is a child of parent_stream
        parent_instance = MagicMock()
        parent_instance.parent = ""
        parent_instance.sync.return_value = (3, {})

        child_instance = MagicMock()
        child_instance.parent = "parent_stream"

        def _stream_factory(key):
            return MagicMock(return_value=(parent_instance if key == "parent_stream" else child_instance))

        mock_streams.__contains__.side_effect = lambda item: item in ("parent_stream", "child_stream")
        mock_streams.__getitem__.side_effect = lambda key: _stream_factory(key)

        catalog = _mock_catalog(["parent_stream", "child_stream"])
        client = MagicMock()
        state = {}

        with patch("tap_amazon_ads.sync.singer.Transformer"):
            sync(client, self._base_config(), catalog, state)

        # Only parent is synced directly
        parent_instance.sync.assert_called_once()
        child_instance.sync.assert_not_called()

    @patch("tap_amazon_ads.sync.singer.write_state")
    @patch("tap_amazon_ads.sync.update_currently_syncing")
    @patch("tap_amazon_ads.sync.write_schema")
    @patch("tap_amazon_ads.sync.STREAMS")
    def test_currently_syncing_set_and_cleared(
        self, mock_streams, mock_write_schema, mock_update_sync, mock_write_state
    ):
        """update_currently_syncing must be called once before and once after each stream."""
        mock_stream_instance = MagicMock()
        mock_stream_instance.parent = ""
        mock_stream_instance.sync.return_value = (0, {})
        mock_streams.__contains__.side_effect = lambda item: True
        mock_streams.__getitem__.side_effect = lambda key: MagicMock(return_value=mock_stream_instance)

        catalog = _mock_catalog(["my_stream"])
        client = MagicMock()
        state = {}

        with patch("tap_amazon_ads.sync.singer.Transformer"):
            sync(client, self._base_config(), catalog, state)

        # Called once to set ("my_stream") and once to clear (None)
        calls = mock_update_sync.call_args_list
        stream_names = [c[0][1] for c in calls]
        self.assertIn("my_stream", stream_names)
        self.assertIn(None, stream_names)


# ---------------------------------------------------------------------------
# get_records / pagination tests
# ---------------------------------------------------------------------------

class TestGetRecords(unittest.TestCase):
    """Tests for BaseStream.get_records() pagination behaviour."""

    def _make_stream(self):
        with patch("tap_amazon_ads.streams.abstracts.metadata.to_map") as mock_to_map:
            mock_to_map.return_value = {(): {"selected": True}}
            client = MagicMock()
            client.config = {"start_date": "2024-01-01T00:00:00Z"}
            client.base_url = "https://advertising.amazon.com"
            catalog_entry = _mock_catalog_entry("test_incremental")
            StreamCls = _make_incremental_stream_cls()
            stream = StreamCls(client=client, catalog=catalog_entry)
            stream.child_to_sync = []
            stream.url_endpoint = "https://advertising.amazon.com/items"
        return stream

    def test_single_page_list_response(self):
        """A list response is returned directly and pagination stops."""
        stream = self._make_stream()
        stream.client.make_request.return_value = [{"id": "1"}, {"id": "2"}]
        records = list(stream.get_records())
        self.assertEqual(len(records), 2)
        self.assertEqual(stream.client.make_request.call_count, 1)

    def test_dict_response_extracts_data_key(self):
        """A dict response extracts items under data_key and stops when no nextToken."""
        stream = self._make_stream()
        stream.client.make_request.return_value = {"items": [{"id": "A"}, {"id": "B"}]}
        records = list(stream.get_records())
        self.assertEqual(len(records), 2)

    def test_paginated_dict_response(self):
        """Pagination continues while nextToken is present; stops when absent."""
        stream = self._make_stream()
        stream.pagination_in = "body"
        stream.next_page_key = "nextToken"

        page1 = {"items": [{"id": "1"}, {"id": "2"}], "nextToken": "tok123"}
        page2 = {"items": [{"id": "3"}]}

        stream.client.make_request.side_effect = [page1, page2]
        records = list(stream.get_records())

        self.assertEqual(len(records), 3)
        self.assertEqual(stream.client.make_request.call_count, 2)
        # The second page request must have included the token in the payload
        second_call_kwargs = stream.client.make_request.call_args_list[1]
        self.assertIn("tok123", str(second_call_kwargs))

    def test_unexpected_response_type_raises(self):
        """A response that is neither list nor dict raises TypeError."""
        stream = self._make_stream()
        stream.client.make_request.return_value = "unexpected string"
        with self.assertRaises(TypeError):
            list(stream.get_records())

    def test_empty_data_key_returns_no_records(self):
        """If the data key is missing from the response, no records are yielded."""
        stream = self._make_stream()
        stream.client.make_request.return_value = {"other_key": [{"id": "1"}]}
        records = list(stream.get_records())
        self.assertEqual(records, [])
