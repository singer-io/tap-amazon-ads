import os
import json
import singer
from typing import Dict, Tuple
from singer import metadata
from tap_amazon_ads.streams import STREAMS

LOGGER = singer.get_logger()


def get_abs_path(path: str) -> str:
    """
    Get the absolute path for the schema files.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schema_references() -> Dict:
    """
    Load the schema files from the schema folder and return the schema references.
    """
    shared_schema_path = get_abs_path("schemas/shared")

    shared_file_names = []
    if os.path.exists(shared_schema_path):
        shared_file_names = [
            f
            for f in os.listdir(shared_schema_path)
            if os.path.isfile(os.path.join(shared_schema_path, f))
        ]

    refs = {}
    for shared_schema_file in shared_file_names:
        with open(os.path.join(shared_schema_path, shared_schema_file)) as data_file:
            refs["shared/" + shared_schema_file] = json.load(data_file)

    return refs


def get_schemas() -> Tuple[Dict, Dict]:
    """
    Load schemas and build Singer catalog metadata for all streams.
    Returns raw schemas and metadata dicts keyed by stream name.
    Access checks are the caller's responsibility (see discover()).
    """
    schemas = {}
    field_metadata = {}

    refs = load_schema_references()
    for stream_name, stream_obj in STREAMS.items():
        schema_path = get_abs_path(f"schemas/{stream_name}.json")
        with open(schema_path) as file:
            raw_schema = json.load(file)
        schemas[stream_name] = raw_schema

        resolved_schema = singer.resolve_schema_references(raw_schema, refs)

        mdata = metadata.new()
        mdata = metadata.get_standard_metadata(
            schema=resolved_schema,
            key_properties=getattr(stream_obj, "key_properties"),
            valid_replication_keys=(getattr(stream_obj, "replication_keys") or []),
            replication_method=getattr(stream_obj, "replication_method"),
        )
        mdata = metadata.to_map(mdata)

        for field_name in (getattr(stream_obj, "replication_keys") or []):
            if field_name in resolved_schema.get("properties", {}):
                mdata = metadata.write(
                    mdata, ("properties", field_name), "inclusion", "automatic"
                )

        parent_tap_stream_id = getattr(stream_obj, "parent", None)
        if parent_tap_stream_id:
            mdata = metadata.write(mdata, (), "parent-tap-stream-id", parent_tap_stream_id)

        field_metadata[stream_name] = metadata.to_list(mdata)

    return schemas, field_metadata
