from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsKeywords(FullTableStream):
    tap_stream_id = "sponsored_brands_keywords"
    key_properties = ["keywordId"]
    replication_method = "FULL_TABLE"
    path = "sb/keywords"
