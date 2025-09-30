from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsStoreAssets(FullTableStream):
    tap_stream_id = "sponsored_brands_store_assets"
    key_properties = ["assetID"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "stores/assets"
    http_method = "GET"
    api_version = 3
    accept_header = f"application/vnd.mediaasset.v{api_version}+json"

