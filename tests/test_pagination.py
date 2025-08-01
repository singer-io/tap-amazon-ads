from tap_tester.base_suite_tests.pagination_test import PaginationTest
from base import Amazon_AdsBaseTest

class Amazon_AdsPaginationTest(PaginationTest, Amazon_AdsBaseTest):
    """
    Ensure tap can replicate multiple pages of data for streams that use pagination.
    """

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_pagination_test"

    def streams_to_test(self):
        streams_to_exclude = {}
        return self.expected_stream_names().difference(streams_to_exclude)
