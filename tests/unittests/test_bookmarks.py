import unittest
from unittest.mock import patch, MagicMock, call
from singer import get_bookmark
from tap_amazon_ads.streams.abstracts import IncrementalStream


# ---------------------------------------------------------------------------
# Minimal concrete subclass used across all bookmark tests
# ---------------------------------------------------------------------------

class _Stream(IncrementalStream):
    tap_stream_id = "test_stream"
    key_properties = ["id"]
    replication_keys = ["lastUpdateDateTime"]
    replication_method = "INCREMENTAL"
    http_method = "POST"
    data_key = "items"
    path = "items/list"
    pagination_in = "body"


def _make_stream(config=None):
    """Factory: returns a fully wired _Stream instance with mock client/catalog."""
    patcher = patch("tap_amazon_ads.streams.abstracts.metadata.to_map")
    mock_to_map = patcher.start()
    mock_to_map.return_value = {(): {"selected": True}}

    client = MagicMock()
    client.config = config or {"start_date": "2024-01-01T00:00:00Z"}
    client.base_url = "https://advertising.amazon.com"

    catalog = MagicMock()
    catalog.schema.to_dict.return_value = {
        "properties": {
            "id": {"type": ["null", "string"]},
            "lastUpdateDateTime": {"type": ["null", "string"], "format": "date-time"},
        }
    }
    catalog.metadata = []

    stream = _Stream(client=client, catalog=catalog)
    stream.child_to_sync = []
    patcher.stop()
    return stream


# ---------------------------------------------------------------------------
# get_bookmark tests
# ---------------------------------------------------------------------------

class TestGetBookmark(unittest.TestCase):
    """Tests for IncrementalStream.get_bookmark()"""

    def setUp(self):
        self.stream = _make_stream()

    def test_returns_existing_bookmark(self):
        """Returns the stored bookmark value when present in state."""
        state = {
            "bookmarks": {
                "test_stream": {"lastUpdateDateTime": "2025-06-01T00:00:00Z"}
            }
        }
        result = self.stream.get_bookmark(state, "test_stream")
        self.assertEqual(result, "2025-06-01T00:00:00Z")

    def test_falls_back_to_start_date_when_no_bookmark(self):
        """Falls back to config start_date when the stream has no bookmark."""
        state = {}
        result = self.stream.get_bookmark(state, "test_stream")
        self.assertEqual(result, "2024-01-01T00:00:00Z")

    def test_explicit_key_overrides_replication_key(self):
        """When a custom key is passed, it is used instead of replication_keys[0]."""
        state = {
            "bookmarks": {
                "test_stream": {
                    "custom_key": "2025-03-15T00:00:00Z",
                    "lastUpdateDateTime": "2024-01-01T00:00:00Z",
                }
            }
        }
        result = self.stream.get_bookmark(state, "test_stream", key="custom_key")
        self.assertEqual(result, "2025-03-15T00:00:00Z")

    def test_falls_back_to_start_date_for_unknown_stream(self):
        """An unknown stream name returns start_date as fallback."""
        state = {"bookmarks": {"other_stream": {"lastUpdateDateTime": "2025-01-01T00:00:00Z"}}}
        result = self.stream.get_bookmark(state, "test_stream")
        self.assertEqual(result, "2024-01-01T00:00:00Z")


# ---------------------------------------------------------------------------
# write_bookmark tests
# ---------------------------------------------------------------------------

class TestWriteBookmark(unittest.TestCase):
    """Tests for IncrementalStream.write_bookmark()"""

    def setUp(self):
        self.stream = _make_stream()

    def test_writes_bookmark_when_value_is_greater(self):
        """New value greater than existing bookmark is persisted."""
        state = {
            "bookmarks": {
                "test_stream": {"lastUpdateDateTime": "2024-06-01T00:00:00Z"}
            }
        }
        new_state = self.stream.write_bookmark(
            state, "test_stream", value="2025-01-01T00:00:00Z"
        )
        bookmark = new_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2025-01-01T00:00:00Z")

    def test_does_not_regress_bookmark_to_older_value(self):
        """A value older than the existing bookmark keeps the existing bookmark."""
        state = {
            "bookmarks": {
                "test_stream": {"lastUpdateDateTime": "2025-01-01T00:00:00Z"}
            }
        }
        new_state = self.stream.write_bookmark(
            state, "test_stream", value="2024-01-01T00:00:00Z"
        )
        bookmark = new_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2025-01-01T00:00:00Z")

    def test_writes_bookmark_when_no_prior_bookmark(self):
        """Bookmark is written correctly when no prior bookmark exists."""
        state = {}
        new_state = self.stream.write_bookmark(
            state, "test_stream", value="2025-03-01T00:00:00Z"
        )
        bookmark = new_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2025-03-01T00:00:00Z")

    def test_write_bookmark_returns_state_unchanged_when_no_replication_keys(self):
        """Returns state unmodified when stream has no replication keys and no key arg."""
        stream = _make_stream()
        stream.replication_keys = []
        state = {"bookmarks": {}}
        result = stream.write_bookmark(state, "test_stream", value="2025-01-01T00:00:00Z")
        self.assertEqual(result, {"bookmarks": {}})

    def test_writes_with_explicit_key(self):
        """Bookmark is written under the explicitly provided key."""
        state = {}
        new_state = self.stream.write_bookmark(
            state, "test_stream", key="custom_key", value="2025-07-01T00:00:00Z"
        )
        bookmark = new_state["bookmarks"]["test_stream"]["custom_key"]
        self.assertEqual(bookmark, "2025-07-01T00:00:00Z")


# ---------------------------------------------------------------------------
# modify_object / extendedData promotion tests
# ---------------------------------------------------------------------------

class TestModifyObject(unittest.TestCase):
    """Tests for BaseStream.modify_object() — the extendedData promotion logic."""

    def setUp(self):
        self.stream = _make_stream()

    def test_promotes_replication_key_from_extended_data(self):
        """modify_object promotes the replication key from extendedData to top level."""
        record = {
            "id": "1",
            "extendedData": {"lastUpdateDateTime": "2025-05-01T00:00:00Z"},
        }
        result = self.stream.modify_object(record)
        self.assertEqual(result["lastUpdateDateTime"], "2025-05-01T00:00:00Z")

    def test_does_not_overwrite_existing_top_level_value(self):
        """If the key is already present at top level AND in extendedData, extendedData wins."""
        record = {
            "id": "1",
            "lastUpdateDateTime": "2024-01-01T00:00:00Z",
            "extendedData": {"lastUpdateDateTime": "2025-05-01T00:00:00Z"},
        }
        result = self.stream.modify_object(record)
        self.assertEqual(result["lastUpdateDateTime"], "2025-05-01T00:00:00Z")

    def test_leaves_record_unchanged_when_extended_data_absent(self):
        """When extendedData is absent, the record is returned unmodified."""
        record = {"id": "1", "name": "test"}
        result = self.stream.modify_object(record)
        self.assertNotIn("lastUpdateDateTime", result)
        self.assertEqual(result, {"id": "1", "name": "test"})

    def test_leaves_record_unchanged_when_key_not_in_extended_data(self):
        """When the replication key is not in extendedData, the record is unmodified."""
        record = {"id": "1", "extendedData": {"someOtherField": "value"}}
        result = self.stream.modify_object(record)
        self.assertNotIn("lastUpdateDateTime", result)

    def test_handles_non_dict_extended_data_gracefully(self):
        """If extendedData is not a dict, modify_object does not crash."""
        record = {"id": "1", "extendedData": None}
        result = self.stream.modify_object(record)
        self.assertNotIn("lastUpdateDateTime", result)

    def test_no_op_for_full_table_stream(self):
        """A stream with empty replication_keys leaves the record unchanged."""
        stream = _make_stream()
        stream.replication_keys = []
        record = {"id": "1", "extendedData": {"lastUpdateDateTime": "2025-01-01T00:00:00Z"}}
        result = stream.modify_object(record)
        self.assertNotIn("lastUpdateDateTime", result)


# ---------------------------------------------------------------------------
# Bookmark state across sync runs (integration-style unit test)
# ---------------------------------------------------------------------------

class TestBookmarkAdvancesAfterSync(unittest.TestCase):
    """
    Verifies that after a sync run the bookmark is set to the maximum
    replication key value seen in the records — simulating the bookmark
    advancing correctly across runs.
    """

    def _run_sync(self, records, initial_bookmark):
        """Helper: run a sync with a mocked get_records and return final state."""
        import singer
        stream = _make_stream(config={"start_date": "2024-01-01T00:00:00Z"})
        stream.url_endpoint = "https://advertising.amazon.com/sp/campaigns/list"

        state = {
            "bookmarks": {
                "test_stream": {"lastUpdateDateTime": initial_bookmark}
            }
        }

        with patch.object(stream, "get_records", return_value=iter(records)), \
             patch("tap_amazon_ads.streams.abstracts.write_record"), \
             patch("tap_amazon_ads.streams.abstracts.metrics.record_counter") as mock_counter:

            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_counter.return_value = mock_ctx

            with singer.Transformer() as transformer:
                _, final_state = stream.sync(state=state, transformer=transformer)

        return final_state

    def test_bookmark_advances_to_max_record_date(self):
        """After sync, bookmark should be the maximum replication key in the records."""
        records = [
            {"id": "1", "lastUpdateDateTime": "2025-01-10T00:00:00Z"},
            {"id": "2", "lastUpdateDateTime": "2025-03-15T00:00:00Z"},
            {"id": "3", "lastUpdateDateTime": "2025-02-01T00:00:00Z"},
        ]
        final_state = self._run_sync(records, "2025-01-01T00:00:00Z")
        bookmark = final_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2025-03-15T00:00:00Z")

    def test_bookmark_does_not_regress_when_all_records_are_older(self):
        """If all records are older than the bookmark, bookmark stays unchanged."""
        records = [
            {"id": "1", "lastUpdateDateTime": "2023-06-01T00:00:00Z"},
        ]
        final_state = self._run_sync(records, "2025-01-01T00:00:00Z")
        bookmark = final_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2025-01-01T00:00:00Z")

    def test_bookmark_stays_at_start_date_when_no_records(self):
        """With no records, bookmark remains at start_date."""
        final_state = self._run_sync([], "2024-01-01T00:00:00Z")
        bookmark = final_state["bookmarks"]["test_stream"]["lastUpdateDateTime"]
        self.assertEqual(bookmark, "2024-01-01T00:00:00Z")
