from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayBudgetRules(IncrementalStream):
    tap_stream_id = "sponsored_display_budget_rules"
    key_properties = ["ruleId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdateDate"]
    data_key = "budgetRulesForAdvertiserResponse"
    children = ["sponsored_brands_budget_rules_campaigns"]
    path = "sd/budgetRules"
    http_method = "GET"
    page_size = 30

    def update_params(self, parent_obj: Dict = None, **kwargs):
        """Update params for the stream"""
        kwargs["pageSize"] = self.page_size
        super().update_params(**kwargs)

