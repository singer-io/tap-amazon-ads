from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Iterator
import json
from singer import (
    Transformer,
    get_bookmark,
    get_logger,
    metrics,
    write_bookmark,
    write_record,
    write_schema,
    metadata
)

LOGGER = get_logger()


class BaseStream(ABC):
    """
    A Base Class providing structure and boilerplate for generic streams
    and required attributes for any kind of stream
    ~~~
    Provides:
     - Basic Attributes (stream_name,replication_method,key_properties)
     - Helper methods for catalog generation
     - `sync` and `get_records` method for performing sync
    """

    url_endpoint = ""
    path = ""
    page_size = 100
    next_page_key = "nextToken"
    children = []
    parent = ""
    data_key = ""
    parent_bookmark_key = ""
    content_type  = "application/json"
    accept_header = "application/json"
    api_version = None
    prefer = False
    prefer_value = ""
    pagination_in = None

    def __init__(self, client=None, catalog=None) -> None:
        self.client = client
        self.catalog = catalog
        self.schema = catalog.schema.to_dict()
        self.metadata = metadata.to_map(catalog.metadata)
        self.child_to_sync = []
        self.params = {}
        self.data_payload = dict()

    @property
    @abstractmethod
    def tap_stream_id(self) -> str:
        """Unique identifier for the stream.

        This is allowed to be different from the name of the stream, in
        order to allow for sources that have duplicate stream names.
        """

    @property
    @abstractmethod
    def replication_method(self) -> str:
        """Defines the sync mode of a stream."""

    @property
    @abstractmethod
    def replication_keys(self) -> str:
        """Defines the replication key for incremental sync mode of a
        stream."""

    @property
    @abstractmethod
    def key_properties(self) -> Tuple[str, str]:
        """List of key properties for stream."""

    @property
    @abstractmethod
    def http_method(self) -> str:
        """Defines the http method for the stream."""

    @property
    def headers(self):
        """
            Constructs and returns the HTTP headers for API requests.
            This property dynamically builds the headers based on the current
            `api_version`, `schema_version`, and optionally a `prefer` setting.
            - If `api_version` is set, it appends the version and '+json' to the
            `schema_version` string for the Accept and Content-Type headers.
            - If `prefer` is enabled, it adds the Prefer header with the given value.
            Returns:
                dict: A dictionary of HTTP headers to be used in the API request.
        """
        headers = {"Accept": self.accept_header, "Content-Type": self.content_type}
        if self.prefer:
            headers.update({"Prefer": self.prefer_value})
        return headers

    def is_selected(self):
        return metadata.get(self.metadata, (), "selected")

    @abstractmethod
    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        """
        Performs a replication sync for the stream.
        ~~~
        Args:
         - state (dict): represents the state file for the tap.
         - transformer (object): A Object of the singer.transformer class.
         - parent_obj (dict): The parent object for the stream.

        Returns:
         - bool: The return value. True for success, False otherwise.

        Docs:
         - https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md
        """


    def get_records(self) -> Iterator:
        """Interacts with api client interaction and pagination."""
        next_page = 1
        while next_page:
            response = self.client.make_request(
                self.http_method, self.url_endpoint, self.params, self.headers, body=json.dumps(self.data_payload), path=self.path
            )

            if isinstance(response, list):
                raw_records = response
                next_page = None
            elif isinstance(response, dict):
                raw_records = response.get(self.data_key, [])
                next_page = self.update_pagination_key(response)
            else:
                raise TypeError("Unexpected response type. Expected dict or list.")
            yield from raw_records

    def write_schema(self) -> None:
        """
        Write a schema message.
        """
        try:
            write_schema(self.tap_stream_id, self.schema, self.key_properties)
        except OSError as err:
            LOGGER.error(
                "OS Error while writing schema for: {}".format(self.tap_stream_id)
            )
            raise err

    def update_params(self, parent_obj: Dict = None, **kwargs) -> None:
        """
        Update params for the stream
        """
        self.params.update(kwargs)

    def modify_object(self, record: Dict, parent_record: Dict = None) -> Dict:
        """
        Modify the record before writing to the stream
        """
        return record

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        """
        Get the URL endpoint for the stream
        """
        return self.url_endpoint or f"{self.client.base_url}/{self.path}"

    def update_data_payload(self, parent_obj: Dict = None, **kwargs) -> Dict:
        """
        Constructs the JSON body payload for the API request.
        """
        self.data_payload.update(kwargs)

    def get_dot_path_value(self, record: dict, dotted_path: str, default=None):
        """
        Safely retrieve a nested value from a dictionary using a dotted key path.
        """
        keys = dotted_path.split(".")
        value = record
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def update_pagination_key(self, response):
        """
        Extracts and updates the pagination key from the API response.
        This method parses the given response to retrieve the pagination token (e.g., 'nextCursor', 'nextToken')
        and updates the internal state to be used for the next paginated request.
        """
        next_page = response.get(self.next_page_key)
        if self.pagination_in == "params" and next_page:
            self.params[self.next_page_key] = next_page
        elif self.pagination_in == "body" and next_page:
            self.data_payload[self.next_page_key] = next_page
        else:
            next_page = None
        return next_page

class IncrementalStream(BaseStream):
    """Base Class for Incremental Stream."""
    def get_bookmark(self, state: dict, stream: str, key: Any = None) -> int:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""
        return get_bookmark(
            state,
            stream,
            key or self.replication_keys[0],
            self.client.config["start_date"],
        )

    def write_bookmark(self, state: dict, stream: str, key: Any = None, value: Any = None) -> Dict:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""
        if not (key or self.replication_keys):
            return state

        current_bookmark = get_bookmark(state, stream, key or self.replication_keys[0], self.client.config["start_date"])
        value = max(current_bookmark, value)
        return write_bookmark(
            state, stream, key or self.replication_keys[0], value
        )


    def sync(self,state: Dict,transformer: Transformer,parent_obj: Dict = None,) -> Dict:
        """Implementation for `type: Incremental` stream."""
        bookmark_date = self.get_bookmark(state, self.tap_stream_id)
        current_max_bookmark_date = bookmark_date
        self.url_endpoint = self.get_url_endpoint(parent_obj)
        self.update_data_payload(parent_obj=parent_obj)
        self.update_params(parent_obj=parent_obj)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                record = self.modify_object(record, parent_obj)
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )

                record_timestamp = self.get_dot_path_value(transformed_record, self.replication_keys[0])
                if record_timestamp >= bookmark_date:
                    if self.is_selected():
                        write_record(self.tap_stream_id, transformed_record)
                        counter.increment()

                    current_max_bookmark_date = max(
                        current_max_bookmark_date, record_timestamp
                    )

                    for child in self.child_to_sync:
                        child.sync(state=state, transformer=transformer, parent_obj=record)

            state = self.write_bookmark(state, self.tap_stream_id, value=current_max_bookmark_date)
            return counter.value, state


class FullTableStream(BaseStream):
    """Base Class for Incremental Stream."""

    def sync(self, state: Dict, transformer: Transformer, parent_obj: Dict = None) -> Dict:
        """Abstract implementation for `type: Fulltable` stream."""
        self.url_endpoint = self.get_url_endpoint(parent_obj)
        self.update_data_payload(parent_obj=parent_obj)
        self.update_params(parent_obj=parent_obj)
        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )
                if self.is_selected:
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()

                for child in self.child_to_sync:
                    child.sync(state=state, transformer=transformer, parent_obj=record)

            return counter.value, state

