from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsProductTargets(FullTableStream):
    tap_stream_id = "sponsored_brands_product_targets"
    key_properties = ["targetId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "sb/targets/list"
    http_method = "POST"
