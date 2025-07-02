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
