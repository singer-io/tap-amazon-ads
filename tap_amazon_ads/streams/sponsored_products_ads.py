from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredProductsAds(IncrementalStream):
    tap_stream_id = "sponsored_products_ads"
    key_properties = ["adId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "productAds"
    path = "sp/productAds/list"
    http_method = "POST"
    api_version = 3
    accept_header = f"application/vnd.spProductAd.v{api_version}+json"
    content_type = f"application/vnd.spProductAd.v{api_version}+json"
    pagination_in = "body"

    def update_data_payload(self, parent_obj: Dict = None, **kwargs) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        kwargs["includeExtendedDataFields"] = True
        super().update_data_payload(parent_obj, **kwargs)

