from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredDisplayBrandSafetyList(FullTableStream):
    tap_stream_id = "sponsored_display_brand_safety_list"
    key_properties = ["requestId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "requestStatusList"
    path = "sd/brandSafety/status"
    http_method = "GET"

