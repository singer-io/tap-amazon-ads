"""Test tap discovery mode and metadata."""
from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.discovery_test import DiscoveryTest


class Amazon_AdsDiscoveryTest(DiscoveryTest, Amazon_AdsBaseTest):
    """Test tap discovery mode and metadata conforms to standards."""

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_discovery_test"

    def streams_to_test(self):
        return self.expected_stream_names()
