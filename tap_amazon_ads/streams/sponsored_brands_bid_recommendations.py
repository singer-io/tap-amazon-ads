from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsBidRecommendations(FullTableStream):
    tap_stream_id = "sponsored_brands_bid_recommendations"
    key_properties = ["recommendationId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    path = "sb/recommendations/bids"
    http_method = "POST"
