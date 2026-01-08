
from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.interrupted_sync_test import InterruptedSyncTest


class Amazon_AdsInterruptedSyncTest(InterruptedSyncTest,Amazon_AdsBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_interrupted_sync_test"

    def streams_to_test(self):
        streams_to_exclude = {
            #this needs to check as primary key is missing
            'sponsored_brands_store_assets',
            # No data available for streams
            'sponsored_brands_negative_keywords',
            'sponsored_display_brand_safety_list','sponsored_display_negative_targeting_clauses','sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations','sponsored_brands_campaigns_budget_rules', 'sponsored_brands_ad_groups', 'sponsored_brands_keywords',
            'sponsored_brands_negative_targets', 'sponsored_brands_product_targets','sponsored_brands_ads',
            'sponsored_brands_ad_creatives', 'sponsored_brands_budget_rules_campaigns','sponsored_products_campaigns',
            'sponsored_products_ad_groups','sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices'}
        # return self.expected_stream_names().difference(streams_to_exclude)
        return {'portfolios', 'sponsored_display_ad_groups'}


    def manipulate_state(self):
        return {
            "currently_syncing": "portfolios",
            "bookmarks": {
            "portfolios": { "lastUpdateDateTime" : "2025-07-03T10:53:24.882000Z"},
            # "sponsored_display_campaigns": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            "sponsored_display_ad_groups": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            # "sponsored_display_product_ads": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            # "sponsored_display_targetings": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            # "sponsored_display_budget_rules": { "lastUpdateDate" : "2020-01-01T00:00:00Z"},
            # "sponsored_brands_budget_rules": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
            # "sponsored_products_budget_rules": { "lastUpdatedDate" : "2020-01-01T00:00:00Z"},
        }
    }
