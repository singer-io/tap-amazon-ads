import copy
import os
import unittest
from datetime import datetime as dt
from datetime import timedelta

import dateutil.parser
import pytz
from tap_tester import connections, menagerie, runner
from tap_tester.logger import LOGGER
from tap_tester.base_suite_tests.base_case import BaseCase


class Amazon_AdsBaseTest(BaseCase):
    """Setup expectations for test sub classes.

    Metadata describing streams. A bunch of shared methods that are used
    in tap-tester tests. Shared tap-specific methods (as needed).
    """
    start_date = "2019-01-01T00:00:00Z"

    @staticmethod
    def tap_name():
        """The name of the tap."""
        return "tap-amazon_ads"

    @staticmethod
    def get_type():
        """The name of the tap."""
        return "platform.amazon_ads"

    @classmethod
    def expected_metadata(cls):
        """The expected streams and metadata about the streams."""
        return {
            "profiles": {
                cls.PRIMARY_KEYS: { "profileId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "portfolios": {
                cls.PRIMARY_KEYS: { "portfolioId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_campaigns": {
                cls.PRIMARY_KEYS: { "campaignId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdatedDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_ad_groups": {
                cls.PRIMARY_KEYS: { "adGroupId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdatedDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_product_ads": {
                cls.PRIMARY_KEYS: { "adId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdateDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_targetings": {
                cls.PRIMARY_KEYS: { "targetId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdateDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_budget_rules": {
                cls.PRIMARY_KEYS: { "ruleId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdateDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_brand_safety_list": {
                cls.PRIMARY_KEYS: { "requestId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_negative_targeting_clauses": {
                cls.PRIMARY_KEYS: { "targetId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdatedDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_display_creatives": {
                cls.PRIMARY_KEYS: { "creativeId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_campaigns": {
                cls.PRIMARY_KEYS: { "campaignId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_ad_groups": {
                cls.PRIMARY_KEYS: { "adGroupId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_keywords": {
                cls.PRIMARY_KEYS: { "keywordId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_negative_keywords": {
                cls.PRIMARY_KEYS: { "keywordId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_bid_recommendations": {
                cls.PRIMARY_KEYS: { "recommendationId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_negative_targets": {
                cls.PRIMARY_KEYS: { "targetId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_product_targets": {
                cls.PRIMARY_KEYS: { "targetId" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_store_assets": {
                cls.PRIMARY_KEYS: { "assetID" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_ad_creatives": {
                cls.PRIMARY_KEYS: { "adId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_brands_budget_rules": {
                cls.PRIMARY_KEYS: { "ruleId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdatedDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_campaigns": {
                cls.PRIMARY_KEYS: { "campaignId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_ad_groups": {
                cls.PRIMARY_KEYS: { "adGroupId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_keywords": {
                cls.PRIMARY_KEYS: { "keywordId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_negative_keywords": {
                cls.PRIMARY_KEYS: { "keywordId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_ads": {
                cls.PRIMARY_KEYS: { "adId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "extendedData.lastUpdateDateTime" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "sponsored_products_budget_rules": {
                cls.PRIMARY_KEYS: { "ruleId" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "lastUpdatedDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "invoices": {
                cls.PRIMARY_KEYS: { "id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "invoiceDate" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            }
        }

    @staticmethod
    def get_credentials():
        """Authentication information for the test account."""
        credentials_dict = {}
        creds = {'client_id': 'TAP_AMAZON_ADS_CLIENT_ID', 'client_secret': 'TAP_AMAZON_ADS_CLIENT_SECRET', 'refresh_token': 'TAP_AMAZON_ADS_REFRESH_TOKEN'}

        for cred in creds:
            credentials_dict[cred] = os.getenv(creds[cred])

        return credentials_dict

    def get_properties(self, original: bool = True):
        """Configuration of properties required for the tap."""
        return_value = {
            "start_date": "2022-07-01T00:00:00Z"
        }
        if original:
            return return_value

        return_value["start_date"] = self.start_date
        return return_value
