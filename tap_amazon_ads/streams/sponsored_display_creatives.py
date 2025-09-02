from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredDisplayCreatives(FullTableStream):
    tap_stream_id = "sponsored_display_creatives"
    key_properties = ["creativeId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "sd/creatives"
    parent = "sponsored_display_ad_groups"
    http_method = "GET"

    def update_params(self, parent_obj: Dict = None, **kwargs):
        """Update params for the stream"""
        kwargs["adGroupIdFilter"] = parent_obj.get("adGroupId")
        super().update_params(**kwargs)

