from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredProductsCampaigns(IncrementalStream):
    tap_stream_id = "sponsored_products_campaigns"
    key_properties = ["campaignId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "campaigns"
    path = "sp/campaigns/list"
