import unittest
from unittest.mock import patch, MagicMock, mock_open
from singer.catalog import Catalog, CatalogEntry
from tap_amazon_ads.discover import discover
from tap_amazon_ads.schema import get_schemas
from tap_amazon_ads.streams import STREAMS
from tap_amazon_ads.exceptions import AmazonAdsForbiddenError


class TestGetSchemas(unittest.TestCase):
    """Unit tests for tap_amazon_ads.schema.get_schemas()"""

    def test_returns_all_streams(self):
        """get_schemas() should return an entry for every stream in STREAMS."""
        schemas, field_metadata = get_schemas()
        self.assertEqual(set(schemas.keys()), set(STREAMS.keys()))
        self.assertEqual(set(field_metadata.keys()), set(STREAMS.keys()))

    def test_schema_properties_are_dicts(self):
        """Every schema returned should have a 'properties' dict."""
        schemas, _ = get_schemas()
        for stream_name, schema in schemas.items():
            with self.subTest(stream=stream_name):
                self.assertIn("properties", schema, f"{stream_name} schema missing 'properties'")
                self.assertIsInstance(schema["properties"], dict)

    def test_incremental_streams_have_replication_key_in_metadata(self):
        """All incremental streams should mark their replication key as 'automatic' in metadata."""
        _, field_metadata = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            rk = getattr(stream_cls, "replication_keys", [])
            if not rk:
                continue
            mdata_list = field_metadata[stream_name]
            automatic_fields = [
                entry["breadcrumb"][1]
                for entry in mdata_list
                if len(entry["breadcrumb"]) == 2
                and entry["breadcrumb"][0] == "properties"
                and entry["metadata"].get("inclusion") == "automatic"
            ]
            with self.subTest(stream=stream_name):
                self.assertIn(
                    rk[0],
                    automatic_fields,
                    f"{stream_name}: replication key '{rk[0]}' not marked automatic",
                )

    def test_primary_keys_in_metadata(self):
        """Every stream should have its key_properties recorded in root metadata."""
        _, field_metadata = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            expected_keys = list(getattr(stream_cls, "key_properties", []))
            mdata_list = field_metadata[stream_name]
            root_entry = next(
                (e for e in mdata_list if not e["breadcrumb"]), None
            )
            with self.subTest(stream=stream_name):
                self.assertIsNotNone(root_entry, f"{stream_name}: no root metadata entry")
                actual_keys = root_entry["metadata"].get("table-key-properties", [])
                self.assertEqual(
                    sorted(actual_keys),
                    sorted(expected_keys),
                    f"{stream_name}: key_properties mismatch",
                )

    def test_replication_method_in_metadata(self):
        """Every stream should have its replication method recorded in root metadata."""
        _, field_metadata = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            expected_method = getattr(stream_cls, "replication_method")
            mdata_list = field_metadata[stream_name]
            root_entry = next(
                (e for e in mdata_list if not e["breadcrumb"]), None
            )
            with self.subTest(stream=stream_name):
                self.assertIsNotNone(root_entry)
                actual_method = root_entry["metadata"].get("forced-replication-method")
                self.assertEqual(actual_method, expected_method)

    def test_all_streams_selected_by_default(self):
        """All streams should have selected=True in root metadata (auto-selected)."""
        _, field_metadata = get_schemas()
        for stream_name in STREAMS:
            mdata_list = field_metadata[stream_name]
            root_entry = next(
                (e for e in mdata_list if not e["breadcrumb"]), None
            )
            with self.subTest(stream=stream_name):
                self.assertIsNotNone(root_entry)
                self.assertTrue(
                    root_entry["metadata"].get("selected"),
                    f"{stream_name}: expected selected=True in metadata",
                )

    def test_replication_key_present_in_schema_properties(self):
        """For every incremental stream, the replication key must exist as a schema property."""
        schemas, _ = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            rk = getattr(stream_cls, "replication_keys", [])
            if not rk:
                continue
            with self.subTest(stream=stream_name):
                self.assertIn(
                    rk[0],
                    schemas[stream_name]["properties"],
                    f"{stream_name}: replication key '{rk[0]}' not in schema properties",
                )

    def test_replication_key_has_date_time_format(self):
        """Every replication key field in the schema must have format=date-time."""
        schemas, _ = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            rk = getattr(stream_cls, "replication_keys", [])
            if not rk:
                continue
            field_def = schemas[stream_name]["properties"].get(rk[0], {})
            with self.subTest(stream=stream_name):
                self.assertEqual(
                    field_def.get("format"),
                    "date-time",
                    f"{stream_name}: replication key '{rk[0]}' missing format:date-time",
                )

    def test_primary_key_fields_exist_in_schema_properties(self):
        """Every key_property must be a property in the schema."""
        schemas, _ = get_schemas()
        for stream_name, stream_cls in STREAMS.items():
            keys = getattr(stream_cls, "key_properties", [])
            props = schemas[stream_name].get("properties", {})
            for key in keys:
                with self.subTest(stream=stream_name, key=key):
                    self.assertIn(
                        key,
                        props,
                        f"{stream_name}: key_property '{key}' not in schema properties",
                    )


class TestDiscover(unittest.TestCase):
    """Unit tests for tap_amazon_ads.discover.discover()"""

    def test_discover_returns_catalog(self):
        """discover() should return a singer Catalog object."""
        catalog = discover()
        self.assertIsInstance(catalog, Catalog)

    def test_discover_catalog_contains_all_streams(self):
        """The catalog should contain an entry for every stream in STREAMS."""
        catalog = discover()
        catalog_stream_names = {entry.stream for entry in catalog.streams}
        self.assertEqual(catalog_stream_names, set(STREAMS.keys()))

    def test_catalog_entry_has_key_properties(self):
        """Every catalog entry must have non-empty key_properties."""
        catalog = discover()
        for entry in catalog.streams:
            with self.subTest(stream=entry.stream):
                self.assertIsNotNone(entry.key_properties)
                self.assertGreater(
                    len(entry.key_properties),
                    0,
                    f"{entry.stream}: key_properties should not be empty",
                )

    def test_catalog_entry_has_schema(self):
        """Every catalog entry must have a schema with properties."""
        catalog = discover()
        for entry in catalog.streams:
            with self.subTest(stream=entry.stream):
                schema_dict = entry.schema.to_dict()
                self.assertIn("properties", schema_dict)

    def test_catalog_entry_has_metadata(self):
        """Every catalog entry must have metadata."""
        catalog = discover()
        for entry in catalog.streams:
            with self.subTest(stream=entry.stream):
                self.assertIsNotNone(entry.metadata)
                self.assertGreater(len(entry.metadata), 0)

    def test_catalog_tap_stream_id_matches_stream(self):
        """tap_stream_id must match the stream name for every entry."""
        catalog = discover()
        for entry in catalog.streams:
            with self.subTest(stream=entry.stream):
                self.assertEqual(entry.stream, entry.tap_stream_id)

    def test_discover_raises_on_bad_schema(self):
        """discover() must propagate errors if a schema file can't be loaded."""
        bad_schemas = {"broken_stream": "not-a-dict"}
        bad_metadata = {"broken_stream": []}
        with patch("tap_amazon_ads.discover.get_schemas", return_value=(bad_schemas, bad_metadata)):
            with self.assertRaises(Exception):
                discover()

    def test_key_properties_match_stream_class(self):
        """key_properties in catalog must match the stream class definition."""
        catalog = discover()
        for entry in catalog.streams:
            stream_cls = STREAMS[entry.stream]
            expected = sorted(getattr(stream_cls, "key_properties", []))
            actual = sorted(entry.key_properties or [])
            with self.subTest(stream=entry.stream):
                self.assertEqual(actual, expected)


# ---------------------------------------------------------------------------
# Helpers for access-check unit tests
# ---------------------------------------------------------------------------

def _make_stream_cls(parent="", check_access_raises=None):
    """
    Build a minimal mock stream *class* that get_schemas can iterate over and
    instantiate.

    Class-level attributes (parent, replication_keys, …) are consumed by
    get_schemas before instantiation; the instance returned by calling the
    class controls the check_access behaviour.
    """
    cls = MagicMock()
    cls.parent = parent
    cls.replication_keys = []
    cls.key_properties = ["id"]
    cls.replication_method = "FULL_TABLE"

    instance = cls.return_value
    instance.parent = parent
    if check_access_raises is not None:
        instance.check_access.side_effect = check_access_raises
    else:
        instance.check_access.return_value = None  # success – no exception raised
    return cls


class TestGetSchemasAccessCheck(unittest.TestCase):
    """Unit tests for the access-check logic added to get_schemas()."""

    def setUp(self):
        self.client = MagicMock()

        self._patchers = [
            patch("tap_amazon_ads.schema.load_schema_references", return_value={}),
            patch(
                "tap_amazon_ads.schema.singer.resolve_schema_references",
                side_effect=lambda schema, refs: schema,
            ),
            patch("builtins.open", mock_open(read_data='{"properties": {}}')),
            patch("tap_amazon_ads.schema.metadata.new", return_value={}),
            patch("tap_amazon_ads.schema.metadata.get_standard_metadata", return_value=[]),
            patch("tap_amazon_ads.schema.metadata.to_map", return_value={}),
            patch("tap_amazon_ads.schema.metadata.write", return_value={}),
            patch("tap_amazon_ads.schema.metadata.to_list", return_value=[]),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    def _run(self, streams_dict):
        with patch("tap_amazon_ads.schema.STREAMS", streams_dict):
            return get_schemas(self.client)

    # ------------------------------------------------------------------
    # Basic inclusion / exclusion
    # ------------------------------------------------------------------

    def test_all_accessible_streams_included(self):
        """All parent streams that pass check_access appear in the returned schemas."""
        campaigns_cls = _make_stream_cls(parent="")
        ads_cls = _make_stream_cls(parent="campaigns")  # child – skipped

        schemas, mdata = self._run({"campaigns": campaigns_cls, "ads": ads_cls})

        self.assertIn("campaigns", schemas)
        self.assertIn("ads", schemas)
        self.assertEqual(len(schemas), 2)

    def test_check_access_called_only_for_parent_streams(self):
        """check_access must be invoked for parent streams and skipped for child streams."""
        campaigns_cls = _make_stream_cls(parent="")
        ads_cls = _make_stream_cls(parent="campaigns")

        self._run({"campaigns": campaigns_cls, "ads": ads_cls})

        campaigns_cls.return_value.check_access.assert_called_once()
        ads_cls.return_value.check_access.assert_not_called()

    def test_forbidden_parent_stream_excluded_from_catalog(self):
        """A parent stream that raises AmazonAdsForbiddenError is removed from
        both schemas and field_metadata."""
        ok_cls = _make_stream_cls(parent="")
        forbidden_cls = _make_stream_cls(
            parent="", check_access_raises=AmazonAdsForbiddenError("403")
        )

        schemas, mdata = self._run({"ok_stream": ok_cls, "forbidden_stream": forbidden_cls})

        self.assertIn("ok_stream", schemas)
        self.assertNotIn("forbidden_stream", schemas)
        self.assertNotIn("forbidden_stream", mdata)

    # ------------------------------------------------------------------
    # Orphan-child pruning
    # ------------------------------------------------------------------

    def test_children_excluded_when_parent_is_forbidden(self):
        """Child streams of a 403-excluded parent are removed by orphan pruning."""
        campaigns_cls = _make_stream_cls(
            parent="", check_access_raises=AmazonAdsForbiddenError("403")
        )
        ads_cls = _make_stream_cls(parent="campaigns")
        keywords_cls = _make_stream_cls(parent="campaigns")
        ok_cls = _make_stream_cls(parent="")

        schemas, _ = self._run(
            {
                "campaigns": campaigns_cls,
                "ads": ads_cls,
                "keywords": keywords_cls,
                "ok_stream": ok_cls,
            }
        )

        self.assertNotIn("campaigns", schemas)
        self.assertNotIn("ads", schemas)
        self.assertNotIn("keywords", schemas)
        self.assertIn("ok_stream", schemas)

    def test_grandchild_excluded_via_single_pass_pruning(self):
        """Orphan pruning cascades: grandchildren are removed when their parent is pruned."""
        campaigns_cls = _make_stream_cls(
            parent="", check_access_raises=AmazonAdsForbiddenError("403")
        )
        ads_cls = _make_stream_cls(parent="campaigns")
        creatives_cls = _make_stream_cls(parent="ads")  # grandchild
        ok_cls = _make_stream_cls(parent="")

        schemas, _ = self._run(
            {
                "campaigns": campaigns_cls,
                "ads": ads_cls,
                "creatives": creatives_cls,
                "ok_stream": ok_cls,
            }
        )

        self.assertNotIn("campaigns", schemas)
        self.assertNotIn("ads", schemas)
        self.assertNotIn("creatives", schemas)
        self.assertIn("ok_stream", schemas)

    def test_child_not_pruned_when_parent_accessible(self):
        """Children are kept in the catalog when their parent passes access check."""
        campaigns_cls = _make_stream_cls(parent="")
        ads_cls = _make_stream_cls(parent="campaigns")

        schemas, _ = self._run({"campaigns": campaigns_cls, "ads": ads_cls})

        self.assertIn("campaigns", schemas)
        self.assertIn("ads", schemas)

    # ------------------------------------------------------------------
    # Error propagation
    # ------------------------------------------------------------------

    def test_all_parent_streams_forbidden_raises_error(self):
        """When every parent stream is unauthorised, AmazonAdsForbiddenError is raised."""
        forbidden_cls = _make_stream_cls(
            parent="", check_access_raises=AmazonAdsForbiddenError("403")
        )

        with self.assertRaises(AmazonAdsForbiddenError):
            self._run({"campaigns": forbidden_cls})

    def test_partial_403_does_not_raise(self):
        """When some (but not all) parent streams fail, no exception is raised and
        only the authorised streams are returned."""
        ok_cls = _make_stream_cls(parent="")
        forbidden_cls = _make_stream_cls(
            parent="", check_access_raises=AmazonAdsForbiddenError("403")
        )

        # Must not raise
        schemas, _ = self._run({"ok_stream": ok_cls, "forbidden_stream": forbidden_cls})

        self.assertIn("ok_stream", schemas)
        self.assertNotIn("forbidden_stream", schemas)

    # ------------------------------------------------------------------
    # No-client path (backward compatibility)
    # ------------------------------------------------------------------

    def test_no_client_skips_access_check(self):
        """Calling get_schemas() without a client must not invoke check_access."""
        stream_cls = _make_stream_cls(parent="")

        with patch("tap_amazon_ads.schema.STREAMS", {"some_stream": stream_cls}):
            schemas, _ = get_schemas()  # no client

        stream_cls.return_value.check_access.assert_not_called()
        self.assertIn("some_stream", schemas)


class TestDiscoverWithAccessCheck(unittest.TestCase):
    """Unit tests for discover() when a client is provided."""

    def test_discover_with_client_excludes_forbidden_streams(self):
        """discover(client) must exclude streams returned from get_schemas for which
        access was denied."""
        mock_client = MagicMock()
        allowed_schemas = {"profiles": {"properties": {"profileId": {"type": "string"}}}}
        allowed_metadata = {"profiles": [{"breadcrumb": [], "metadata": {"table-key-properties": ["profileId"]}}]}

        with patch(
            "tap_amazon_ads.discover.get_schemas",
            return_value=(allowed_schemas, allowed_metadata),
        ) as mock_get_schemas:
            catalog = discover(mock_client)

        mock_get_schemas.assert_called_once_with(mock_client)
        catalog_stream_names = {e.stream for e in catalog.streams}
        self.assertEqual(catalog_stream_names, {"profiles"})

    def test_discover_without_client_calls_get_schemas_with_none(self):
        """discover() called without a client passes None to get_schemas."""
        with patch(
            "tap_amazon_ads.discover.get_schemas",
            return_value=({}, {}),
        ) as mock_get_schemas:
            discover()

        mock_get_schemas.assert_called_once_with(None)
