from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_amazon_ads.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SponsoredBrandsAds(IncrementalStream):
    tap_stream_id = "sponsored_brands_ads"
    key_properties = ["adId"]
    replication_method = "INCREMENTAL"
    replication_keys = ["extendedData.lastUpdateDate"]
    data_key = "ads"
    path = "sb/v4/ads/list"
    children = ["sponsored_brands_ad_creatives"]
    http_method = "POST"
    api_version = 4
    accept_header = f"application/vnd.sbadresource.v{api_version}+json"
    content_type = f"application/vnd.sbadresource.v{api_version}+json"

    def get_bookmark(self, state: Dict, stream: str, key: Any = None) -> int:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""

        min_parent_bookmark = super().get_bookmark(state, stream) if self.is_selected() else None
        for child in self.child_to_sync:
            if child.is_selected():
                bookmark_key = f"{self.tap_stream_id}_{self.replication_keys[0]}"
                child_bookmark = super().get_bookmark(state, child.tap_stream_id, key=bookmark_key)
                if min_parent_bookmark:
                    min_parent_bookmark = min(min_parent_bookmark, child_bookmark)
                else:
                    min_parent_bookmark = child_bookmark

        return min_parent_bookmark

    def write_bookmark(self, state: Dict, stream: str, key: Any = None, value: Any = None) -> Dict:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""
        if self.is_selected():
            super().write_bookmark(state, stream, value=value)

        for child in self.child_to_sync:
            if child.is_selected():
                bookmark_key = f"{self.tap_stream_id}_{self.replication_keys[0]}"
                super().write_bookmark(state, child.tap_stream_id, key=bookmark_key, value=value)
        return state
