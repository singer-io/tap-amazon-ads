from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredProductsBudgetRules(IncrementalStream):
    tap_stream_id = "sponsored_products_budget_rules"
    key_properties = ["ruleId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    data_key = "budgetRulesForAdvertiserResponse"
    path = "sp/budgetRules"
    http_method = "GET"
    page_size = 30
    pagination_in = "params"

    def update_params(self, parent_obj: Dict = None, **kwargs):
        """Update params for the stream"""
        kwargs["pageSize"] = self.page_size
        super().update_params(**kwargs)

