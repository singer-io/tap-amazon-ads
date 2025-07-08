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
    schema_version = "application/vnd.spPortfolio.v"
    prefer = True
    prefer_value = 'return=representation'

    # @property
    # def headers(self):
    #     schema_version = 'application/vnd.spPortfolio.v' + str(self.api_version) + '+json'
    #     headers = {"Accept": schema_version, "Content-Type": schema_version}
    #     prefer_value = 'return=representation'
    #     if self.prefer:
    #         headers.update({"Prefer": prefer_value})
    #     return headers
