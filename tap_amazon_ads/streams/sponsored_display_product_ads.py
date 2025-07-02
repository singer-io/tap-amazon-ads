from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayProductAds(IncrementalStream):
    tap_stream_id = "sponsored_display_product_ads"
    key_properties = ["adId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdateDate"]
    path = "sd/productAds/extended"
