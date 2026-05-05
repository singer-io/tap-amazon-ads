import unittest
from unittest.mock import patch, MagicMock
from tap_amazon_ads.streams.abstracts import IncrementalStream


# Create a concrete subclass of IncrementalStream for testing
class ConcreteStream(IncrementalStream):
    @property
    def key_properties(self):
        return ["id"]

    @property
    def replication_keys(self):
        return ["lastUpdateDateTime"]

    @property
    def replication_method(self):
        return "INCREMENTAL"

    @property
    def tap_stream_id(self):
        return "parent_stream"

    @property
    def http_method(self):
        return "POST"

    def update_params(self, parent_obj=None, **kwargs):
        """Simulate a stream that passes pageSize via params."""
        kwargs["pageSize"] = self.page_size
        super().update_params(**kwargs)

class TestIncrementalStream(unittest.TestCase):
    """
    Unit tests for the IncrementalStream class.
    """
    def setUp(self):
        """Create a mock instance of ConcreteStream"""
        # Start patching 'to_map'
        patcher = patch("tap_amazon_ads.streams.abstracts.metadata.to_map")
        self.mock_to_map = patcher.start()
        self.addCleanup(patcher.stop)  # Ensures patch is removed after test

        self.mock_to_map.return_value = {"metadata_key": "metadata_value"}

        # Create a mock client
        self.client = MagicMock()
        self.client.config = {"start_date": "2024-01-01T00:00:00Z"}

        # Mock catalog
        mock_catalog = MagicMock()
        mock_catalog.schema.to_dict.return_value = {"key": "value"}
        mock_catalog.metadata = "mock_metadata"

        # Stream under test
        self.stream = ConcreteStream(client=self.client, catalog=mock_catalog)
        self.stream.child_to_sync = []

    @patch("tap_amazon_ads.streams.abstracts.IncrementalStream.get_bookmark", return_value = 'Mocked')
    def test_get_bookmark_called(self, mock_get_bookmark):
        """
        Test that the `get_bookmark` method is called with the correct parameters.
        """
        state = {}
        result = self.stream.get_bookmark(state, self.stream.tap_stream_id)
        # Assertions
        mock_get_bookmark.assert_called_once_with(state, "parent_stream")
        self.assertEqual(result, 'Mocked')

    def test_get_bookmark_returns_value(self):
        """
        Test that `get_bookmark` returns the expected bookmark value.
        """
        state = {
            "bookmarks": {
                "parent_stream": {"lastUpdateDateTime": "2025-01-01T00:00:00Z"}
            }
        }
        result = self.stream.get_bookmark(state, self.stream.tap_stream_id, self.stream.replication_keys[0])
        self.assertEqual(result, "2025-01-01T00:00:00Z")

    def test_page_size_default_without_config(self):
        """When config lacks page_size, default remains the class value (100)."""
        # ConcreteStream inherits BaseStream default page_size=100
        self.assertEqual(self.stream.page_size, 100)

    def test_page_size_with_config_override(self):
        """When config provides page_size, it should override the default."""
        self.client.config["page_size"] = 999
        # Recreate stream to apply new config during __init__
        mock_catalog = MagicMock()
        mock_catalog.schema.to_dict.return_value = {"key": "value"}
        mock_catalog.metadata = "mock_metadata"
        stream = ConcreteStream(client=self.client, catalog=mock_catalog)
        self.assertEqual(stream.page_size, 999)

    def test_mock_stream_custom_default_without_config(self):
        """A mock stream with its own class page_size should keep it if no config."""
        class ConcreteStream30(ConcreteStream):
            page_size = 30
        mock_catalog = MagicMock()
        mock_catalog.schema.to_dict.return_value = {"key": "value"}
        mock_catalog.metadata = "mock_metadata"
        stream = ConcreteStream30(client=self.client, catalog=mock_catalog)
        self.assertEqual(stream.page_size, 30)

    def test_mock_stream_custom_default_with_config_override(self):
        """Config page_size overrides even when mock stream has a custom default."""
        class ConcreteStream30(ConcreteStream):
            page_size = 30
        self.client.config["page_size"] = 50
        mock_catalog = MagicMock()
        mock_catalog.schema.to_dict.return_value = {"key": "value"}
        mock_catalog.metadata = "mock_metadata"
        stream = ConcreteStream30(client=self.client, catalog=mock_catalog)
        self.assertEqual(stream.page_size, 50)

    def test_update_params_sets_pageSize(self):
        """A mock stream that sends pageSize should honor default and config."""
        # Default (no config override) uses custom default 30
        class ConcreteStream30(ConcreteStream):
            page_size = 30
        mock_catalog = MagicMock()
        mock_catalog.schema.to_dict.return_value = {"key": "value"}
        mock_catalog.metadata = "mock_metadata"
        stream = ConcreteStream30(client=self.client, catalog=mock_catalog)
        stream.update_params()
        self.assertEqual(stream.params.get("pageSize"), 30)

        # With config override uses configured value
        self.client.config["page_size"] = 47
        stream = ConcreteStream30(client=self.client, catalog=mock_catalog)
        stream.update_params()
        self.assertEqual(stream.params.get("pageSize"), 47)

