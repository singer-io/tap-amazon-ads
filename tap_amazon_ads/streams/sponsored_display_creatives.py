from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredDisplayCreatives(FullTableStream):
    tap_stream_id = "sponsored_display_creatives"
    key_properties = ["creativeId"]
    replication_method = "FULL_TABLE"
    path = "sd/creatives"
