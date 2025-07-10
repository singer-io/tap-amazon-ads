from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsAdCreatives(IncrementalStream):
    tap_stream_id = "sponsored_brands_ad_creatives"
    key_properties = ["adId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdateTime"]
    data_key = "creatives"
    path = "sb/ads/creatives/list"
    parent = "sponsored_brands_ads"
    bookmark_value = None
    http_method = "POST"
    api_version = 4
    accept_header = f"application/vnd.sbAdCreativeResource.v{api_version}+json"
    content_type = f"application/vnd.sbAdCreativeResource.v{api_version}+json"

    def get_bookmark(self, state: Dict, key: Any = None) -> int:
        """
        Return initial bookmark value only for the child stream.
        """
        if not self.bookmark_value:
            self.bookmark_value = super().get_bookmark(state, key)

        return self.bookmark_value

    def update_data_payload(self, parent_obj: Dict = None) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        super().update_data_payload(parent_obj)
        self.data_payload["adId"] = parent_obj.get("adId", None)
