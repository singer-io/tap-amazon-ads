from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsAdGroups(IncrementalStream):
    tap_stream_id = "sponsored_brands_ad_groups"
    key_properties = ["adGroupId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "adGroups"
    path = "sb/v4/adGroups/list"
