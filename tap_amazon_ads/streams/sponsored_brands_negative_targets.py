from typing import Dict, Iterator, List
from singer import get_logger
from tap_amazon_ads.streams.abstracts import FullTableStream

LOGGER = get_logger()


class SponsoredBrandsNegativeTargets(FullTableStream):
    tap_stream_id = "sponsored_brands_negative_targets"
    key_properties = ["targetId"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "negativeTargets"
    path = "sb/negativeTargets/list"
    http_method = "POST"
    api_version = 3.2
    accept_header = f"application/vnd.sblistnegativetargetsresponse.v{api_version}+json"

    def update_data_payload(self, parent_obj: Dict = None) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        `filters` is a required field
        `filterType` Enum values:["CREATIVE_TYPE", "TARGETING_STATE", "CAMPAIGN_ID", "AD_GROUP_ID"]
        """
        super().update_data_payload(parent_obj)
        # need to confirm how would we like to select the filterType from enums
        self.data_payload["filters"] = [{"filterType": "CREATIVE_TYPE","values": ["productCollection"]}]
