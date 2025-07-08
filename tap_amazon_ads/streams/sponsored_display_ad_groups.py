from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayAdGroups(IncrementalStream):
    tap_stream_id = "sponsored_display_ad_groups"
    key_properties = ["adGroupId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    path = "sd/adGroups/extended"
    http_method = "GET"
