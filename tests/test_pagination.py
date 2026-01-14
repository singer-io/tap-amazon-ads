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
        streams_to_exclude = {
            # No data available for streams
            'sponsored_brands_negative_keywords',
            'sponsored_display_brand_safety_list', 'sponsored_display_negative_targeting_clauses', 'sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations', 'sponsored_brands_campaigns_budget_rules', 'sponsored_brands_ad_groups', 'sponsored_brands_keywords',
            'sponsored_brands_negative_targets', 'sponsored_brands_product_targets', 'sponsored_brands_ads',
            'sponsored_brands_ad_creatives', 'sponsored_brands_budget_rules_campaigns', 'sponsored_products_campaigns',
            'sponsored_products_ad_groups', 'sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices'
            # Streams having only 1 data point
            'sponsored_display_creatives', 'sponsored_display_campaigns', 'sponsored_brands_store_assets',
            'sponsored_display_budget_rules_campaigns','sponsored_products_budget_rules', 'sponsored_display_ad_groups',
            'sponsored_display_targetings', 'sponsored_brands_budget_rules', 'sponsored_display_campaigns_budget_rules',
            'sponsored_display_product_ads', 'sponsored_display_creatives', 'invoices'}
        return self.expected_stream_names().difference(streams_to_exclude)

    def get_properties(self, original: bool = True):
        """Configuration with reduced page_size to test pagination logic."""
        return {
            "start_date": self.start_date,
            "page_size": 2
        }

    def expected_page_size(self, stream):
        """
        Return the expected page size for pagination testing.

        Overrides the default API_LIMIT to use the configured page_size.
        This allows pagination testing with smaller datasets by setting
        a lower page limit than the API default (100).
        """
        return 2
