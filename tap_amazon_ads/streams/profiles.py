from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Profiles(FullTableStream):
    tap_stream_id = "profiles"
    key_properties = ["profileId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "v2/profiles"
    http_method = "GET"

