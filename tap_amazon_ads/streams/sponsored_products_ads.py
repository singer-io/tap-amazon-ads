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
