from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredDisplayBudgetRulesCampaigns(FullTableStream):
    tap_stream_id = "sponsored_display_budget_rules_campaigns"
    key_properties = ["campaignId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "associatedCampaigns"
    parent = "sponsored_display_budget_rules"
    path = "sd/budgetRules/{}/campaigns"
    http_method = "GET"
    page_size = 30
    pagination_in = "params"

    def update_params(self, parent_obj: Dict = None, **kwargs):
        """Update params for the stream"""
        kwargs["pageSize"] = self.page_size
        super().update_params(**kwargs)

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        """Prepare URL endpoint for child streams."""
        return f"{self.client.base_url}/{self.path.format(parent_obj['ruleId'])}"

