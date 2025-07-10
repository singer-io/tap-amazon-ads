from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsCampaigns(IncrementalStream):
    tap_stream_id = "sponsored_brands_campaigns"
    key_properties = ["campaignId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "campaigns"
    path = "sb/v4/campaigns/list"
    children = ["sponsored_brands_bid_recommendations", "sponsored_brands_campaigns_budget_rules"]
    http_method = "POST"
    api_version = 4
    accept_header = f"application/vnd.sbcampaignresource.v{api_version}+json"
    content_type = f"application/vnd.sbcampaignresource.v{api_version}+json"

    def update_data_payload(self, parent_obj: Dict = None) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        super().update_data_payload(parent_obj)
        self.data_payload["includeExtendedDataFields"] = True

