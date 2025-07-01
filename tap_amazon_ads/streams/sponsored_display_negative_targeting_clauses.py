from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayNegativeTargetingClauses(IncrementalStream):
    tap_stream_id = "sponsored_display_negative_targeting_clauses"
    key_properties = ["targetId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    path = "sd/negativeTargets/extended"
