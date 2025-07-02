from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredProductsNegativeKeywords(IncrementalStream):
    tap_stream_id = "sponsored_products_negative_keywords"
    key_properties = ["keywordId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "negativeKeywords"
    path = "sp/negativeKeywords/list"
