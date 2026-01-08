from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest





class Amazon_AdsAllFields(AllFieldsTest, Amazon_AdsBaseTest):
    """Ensure running the tap with all streams and fields selected results in
    the replication of all fields."""
    
    MISSING_FIELDS = {
        "sponsored_display_campaigns": {"portfolioId",},
        "profiles": {"dailyBudget"},
        "sponsored_display_product_ads": {"asin", "sku"}
    }

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_all_fields_test"

    def streams_to_test(self):
        streams_to_exclude = {
            # No data available for streams
            'sponsored_display_brand_safety_list','sponsored_display_negative_targeting_clauses','sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations','sponsored_brands_campaigns_budget_rules', 'sponsored_brands_ad_groups', 'sponsored_brands_keywords',
            'sponsored_brands_negative_targets', 'sponsored_brands_product_targets','sponsored_brands_ads',
            'sponsored_brands_ad_creatives', 'sponsored_brands_budget_rules_campaigns','sponsored_products_campaigns',
            'sponsored_products_ad_groups','sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices', 'sponsored_brands_negative_keywords'}
        return self.expected_stream_names().difference(streams_to_exclude)
