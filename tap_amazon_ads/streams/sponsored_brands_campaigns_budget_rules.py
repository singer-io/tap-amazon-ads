from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsCampaignsBudgetRules(IncrementalStream):
    tap_stream_id = "sponsored_brands_campaigns_budget_rules"
    key_properties = ["ruleId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    data_key = "associatedRules"
    path = "sb/campaigns/{}/budgetRules"
    parent = "sponsored_brands_campaigns"
    http_method = "GET"

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        """Prepare URL endpoint for child streams."""
        return f"{self.client.base_url}/{self.path.format(parent_obj['campaignId'])}"

