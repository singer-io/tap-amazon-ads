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
    http_method = "POST"
    api_version = 3
    accept_header = f"application/vnd.spPortfolio.v{api_version}+json"
    content_type = f"application/vnd.spPortfolio.v{api_version}+json"
    prefer = True
    prefer_value = 'return=representation'

    def update_data_payload(self, parent_obj: Dict = None) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        super().update_data_payload(parent_obj)
        self.data_payload["includeExtendedDataFields"] = True
