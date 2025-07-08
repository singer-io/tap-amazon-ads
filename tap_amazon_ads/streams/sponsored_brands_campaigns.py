from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsCampaigns(IncrementalStream):
    tap_stream_id = "sponsored_brands_campaigns"
    key_properties = ["campaignId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "campaigns"
    path = "sb/v4/campaigns/list"
    http_method = "POST"
    api_version = 4
    schema_version = "application/vnd.sbcampaignresource.v"
