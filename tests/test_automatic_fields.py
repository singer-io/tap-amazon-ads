"""Test that with no fields selected for a stream automatic fields are still
replicated."""
from base import Amazon_AdsBaseTest
from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest


class Amazon_AdsAutomaticFields(MinimumSelectionTest, Amazon_AdsBaseTest):
    """Test that with no fields selected for a stream automatic fields are
    still replicated."""

    @staticmethod
    def name():
        return "tap_tester_amazon_ads_automatic_fields_test"

    def streams_to_test(self):
        streams_to_exclude = {
            # No data available for streams
            'sponsored_display_brand_safety_list','sponsored_display_negative_targeting_clauses','sponsored_brands_campaigns',
            'sponsored_brands_bid_recommendations','sponsored_brands_campaigns_budget_rules', 'sponsored_brands_ad_groups', 'sponsored_brands_keywords',
            'sponsored_brands_negative_targets', 'sponsored_brands_product_targets','sponsored_brands_ads',
            'sponsored_brands_ad_creatives', 'sponsored_brands_budget_rules_campaigns','sponsored_products_campaigns',
            'sponsored_products_ad_groups','sponsored_products_keywords', 'sponsored_products_negative_keywords',
            'sponsored_products_ads', 'invoices'}
        return self.expected_stream_names().difference(streams_to_exclude)
