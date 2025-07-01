from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Portfolios(IncrementalStream):
    tap_stream_id = "portfolios"
    key_properties = ["portfolioId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDateTime"]
    data_key = "portfolios"
    path = "portfolios/list"
