from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class Amazon_AdsBookMarkTest(BookmarkTest, Amazon_AdsBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "portfolios": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_display_campaigns": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_ad_groups": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_product_ads": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_targetings": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_budget_rules": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_negative_targeting_clauses": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "sponsored_brands_campaigns": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_brands_ad_groups": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_brands_ad_creatives": { "lastUpdateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_brands_budget_rules": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "sponsored_products_campaigns": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_products_ad_groups": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_products_keywords": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_products_negative_keywords": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_products_ads": { "extendedData.lastUpdateDateTime" : "2020-01-01T00:00:00Z"},
            "sponsored_products_budget_rules": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "invoices": { "invoiceDate" : "2020-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_amazon_ads_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {}
        return self.expected_stream_names().difference(streams_to_exclude)
