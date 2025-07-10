from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsNegativeKeywords(FullTableStream):
    tap_stream_id = "sponsored_brands_negative_keywords"
    key_properties = ["keywordId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "sb/negativeKeywords"
    http_method = "GET"
    api_version = 3.2
    accept_header = f"application/vnd.sbnegativekeyword.v{api_version}+json"

