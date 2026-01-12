from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.start_date_test import StartDateTest



class Amazon_AdsStartDateTest(StartDateTest, Amazon_AdsBaseTest):
    """Instantiate start date according to the desired data set and run the
    test."""

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_start_date_test"

    def streams_to_test(self):
        streams_to_exclude = {
            # No data available for streams
            'sponsored_brands_store_assets',
            'sponsored_brands_negative_keywords',
            'sponsored_display_brand_safety_list',
            'sponsored_display_negative_targeting_clauses',
            'sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations',
            'sponsored_brands_campaigns_budget_rules',
            'sponsored_brands_ad_groups',
            'sponsored_brands_keywords',
            'sponsored_brands_negative_targets',
            'sponsored_brands_product_targets',
            'sponsored_brands_ads',
            'sponsored_brands_ad_creatives',
            'sponsored_brands_budget_rules_campaigns',
            'sponsored_products_campaigns',
            'sponsored_products_ad_groups',
            'sponsored_products_keywords',
            'sponsored_products_negative_keywords',
            'sponsored_products_ads',
            'invoices',
            'sponsored_brands_budget_rules',
            'sponsored_products_budget_rules',
            'sponsored_display_campaigns',
            'sponsored_display_product_ads',
            'sponsored_display_ad_groups',
            'sponsored_display_targetings',
            'sponsored_display_campaigns_budget_rules',
            'sponsored_display_creatives',
            'profiles',
            'portfolios',
            'sponsored_display_budget_rules_campaigns',
            'sponsored_display_budget_rules_campaigns',
        }
        return self.expected_stream_names().difference(streams_to_exclude)

    @property
    def start_date_1(self):
        return "2019-03-25T00:00:00Z"
    @property
    def start_date_2(self):
        # Include a specific time component because we don't have data at
        # midnight for this date. Providing a timestamp ensures the
        # start-date logic initializes after available records and keeps
        # the test deterministic.
        return "2025-07-16T05:24:30.00Z"
