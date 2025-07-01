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
    path = "sd/budgetRules"
