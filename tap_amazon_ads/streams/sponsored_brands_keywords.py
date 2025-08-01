from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsKeywords(FullTableStream):
    tap_stream_id = "sponsored_brands_keywords"
    key_properties = ["keywordId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "sb/keywords"
    http_method = "GET"
    api_version = 3.2
    accept_header = f"application/vnd.sbkeyword.v{api_version}+json"

