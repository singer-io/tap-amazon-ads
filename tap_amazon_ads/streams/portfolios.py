from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Portfolios(IncrementalStream):
    tap_stream_id = "portfolios"
    key_properties = ["portfolioId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdateDateTime"]
    data_key = "portfolios"
    path = "portfolios/list"
    http_method = "POST"
    api_version = 3
    accept_header = f"application/vnd.spPortfolio.v{api_version}+json"
    content_type = f"application/vnd.spPortfolio.v{api_version}+json"
    prefer = True
    prefer_value = "return=representation"
    pagination_in = "body"

    def update_data_payload(self, parent_obj: Dict = None, **kwargs) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        kwargs["includeExtendedDataFields"] = True
        super().update_data_payload(parent_obj, **kwargs)

    def modify_object(self, record: Dict, parent_record: Dict = None) -> Dict:
        """
        Modify the record for all incremental streams.
        Example: flatten lastUpdateDateTime from extendedData.
        """
        extended_data = record.get("extendedData", {})
        record["lastUpdateDateTime"] = extended_data.get("lastUpdateDateTime")
        return record
