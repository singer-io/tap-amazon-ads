from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayTargetings(IncrementalStream):
    tap_stream_id = "sponsored_display_targetings"
    key_properties = ["targetId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    path = "sd/targets/extended"
    http_method = "GET"

