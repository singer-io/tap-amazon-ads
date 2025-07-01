from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsNegativeTargets(FullTableStream):
    tap_stream_id = "sponsored_brands_negative_targets"
    key_properties = ["targetId"]
    replication_method = "FULL_TABLE"
    data_key = "negativeTargets"
    path = "sb/negativeTargets/list"
