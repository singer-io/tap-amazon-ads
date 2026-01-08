
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
            # full table 
            'profiles',
            'sponsored_brands_bid_recommendations',
            'sponsored_brands_budget_rules_campaigns',
            'sponsored_brands_keywords',
            'sponsored_brands_negative_keywords',
            'sponsored_brands_negative_targets',
            'sponsored_brands_product_targets',
            'sponsored_brands_store_assets',
            'sponsored_display_brand_safety_list',
            'sponsored_display_budget_rules_campaigns',
            'sponsored_display_creatives',
            # No data available for streams
            'sponsored_display_negative_targeting_clauses','sponsored_brands_campaigns',
            'sponsored_brands_ad_groups','sponsored_brands_campaigns_budget_rules',
            'sponsored_brands_ads',
            'sponsored_brands_ad_creatives','sponsored_products_campaigns',
            'sponsored_products_ad_groups','sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices', 'portfolios','sponsored_display_campaigns', 'sponsored_display_product_ads',
            'sponsored_display_targetings', 'sponsored_brands_budget_rules', 'sponsored_products_budget_rules',
            'sponsored_display_campaigns_budget_rules'
        }
        return self.expected_stream_names().difference(streams_to_exclude)


    def manipulate_state(self):
        return {
            "currently_syncing": "sponsored_display_ad_groups",
            "bookmarks": {
            "sponsored_display_ad_groups": { "lastUpdatedDate" : "2025-07-03T10:53:24.00Z"},
            "sponsored_display_budget_rules": { "lastUpdatedDate" : "2025-07-16T05:24:22.224000Z"},
        }
    }
