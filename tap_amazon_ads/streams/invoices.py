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
    next_page_key = "nextCursor"
    pagination_in = "params"

    def update_pagination_key(self, response):
        """
        Extracts and updates the pagination key from the API response.
        This method parses the given response to retrieve the pagination token (e.g., 'nextCursor', 'nextToken')
        and updates the internal state to be used for the next paginated request.
        """
        next_page = response.get(self.next_page_key)
        if self.pagination_in == "params" and next_page:
            self.params["cursor"] = next_page
        else:
            next_page = None
        return next_page

