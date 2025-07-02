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
