from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Invoices(IncrementalStream):
    tap_stream_id = "invoices"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["invoiceDate"]
    data_key = "invoiceSummaries"
    path = "invoices"
    http_method = "GET"
    api_version = 1.1
    content_type = f"application/vnd.invoices.v{api_version}+json"

