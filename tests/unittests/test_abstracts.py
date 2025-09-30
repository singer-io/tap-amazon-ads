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

