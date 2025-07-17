from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsBidRecommendations(FullTableStream):
    tap_stream_id = "sponsored_brands_bid_recommendations"
    key_properties = ["recommendationId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "keywordsBidsRecommendationSuccessResults"
    parent = "sponsored_brands_campaigns"
    path = "sb/recommendations/bids"
    http_method = "POST"
    api_version = 3
    accept_header = f"application/vnd.sbbidsrecommendation.v{api_version}+json"

    def update_data_payload(self, parent_obj = None):
        """Constructs the JSON body payload for the Stream API request ."""
        super().update_data_payload(parent_obj)
        data = {
            "campaignId": parent_obj.get("campaignId")
            }
        self.data_payload.update(data)

