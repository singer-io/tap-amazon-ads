from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsAdGroups(IncrementalStream):
    tap_stream_id = "sponsored_brands_ad_groups"
    key_properties = ["adGroupId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["lastUpdateDate"]
    data_key = "adGroups"
    path = "sb/v4/adGroups/list"
    http_method = "POST"
    api_version = 4
    accept_header = f"application/vnd.sbadgroupresource.v{api_version}+json"
    content_type = f"application/vnd.sbadgroupresource.v{api_version}+json"
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
        Example: flatten lastUpdateDate from extendedData.
        """
        extended_data = record.get("extendedData", {})
        record["lastUpdateDate"] = extended_data.get("lastUpdateDate")
        return record
