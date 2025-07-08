from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredDisplayCampaigns(IncrementalStream):
    tap_stream_id = "sponsored_display_campaigns"
    key_properties = ["campaignId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdatedDate"]
    path = "sd/campaigns/extended"
    http_method = "GET"
