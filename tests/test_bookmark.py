from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class Amazon_AdsBookMarkTest(BookmarkTest, Amazon_AdsBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "portfolios": { "lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_display_budget_rules": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_amazon_ads_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {
            # No data available for streams
            'sponsored_brands_negative_keywords',
            'sponsored_display_brand_safety_list', 'sponsored_display_negative_targeting_clauses', 'sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations', 'sponsored_brands_campaigns_budget_rules', 'sponsored_brands_ad_groups', 'sponsored_brands_keywords',
            'sponsored_brands_negative_targets', 'sponsored_brands_product_targets', 'sponsored_brands_ads',
            'sponsored_brands_ad_creatives', 'sponsored_brands_budget_rules_campaigns', 'sponsored_products_campaigns',
            'sponsored_products_ad_groups', 'sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices', 'sponsored_display_product_ads', 'sponsored_display_targetings', 'sponsored_display_campaigns_budget_rules',
            'sponsored_display_ad_groups', 'sponsored_display_campaigns', 'sponsored_brands_budget_rules',
            'sponsored_products_budget_rules', 'sponsored_display_creatives', 'sponsored_brands_store_assets',
            'profiles', 'sponsored_display_budget_rules_campaigns'}
        return self.expected_stream_names().difference(streams_to_exclude)

    def calculate_new_bookmarks(self):
        """Calculates new bookmarks by looking through sync 1 data to determine
        a bookmark that will sync 2 records in sync 2 (plus any necessary look
        back data)"""
        new_bookmarks = {
            "portfolios": { "lastUpdateDateTime" : "2025-07-03T10:58:02.00Z"},
            "sponsored_display_budget_rules": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
        }

        return new_bookmarks
