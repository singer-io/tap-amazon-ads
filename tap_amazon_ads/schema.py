import os
import json
import singer
from typing import Dict, List, Tuple
from singer import metadata
from tap_amazon_ads.streams import STREAMS
from tap_amazon_ads.exceptions import AmazonAdsForbiddenError

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


def _load_schema(stream_name: str) -> Dict:
    """
    Load the raw JSON schema for a single stream from disk.
    """
    schema_path = get_abs_path(f"schemas/{stream_name}.json")
    with open(schema_path) as file:
        return json.load(file)


def _build_metadata(stream_obj, schema: Dict) -> List:
    """
    Build Singer catalog metadata for a stream from its resolved schema.
    Returns a metadata list suitable for a catalog entry.
    """
    mdata = metadata.new()
    mdata = metadata.get_standard_metadata(
        schema=schema,
        key_properties=getattr(stream_obj, "key_properties"),
        valid_replication_keys=(getattr(stream_obj, "replication_keys") or []),
        replication_method=getattr(stream_obj, "replication_method"),
    )
    mdata = metadata.to_map(mdata)

    # Explicitly mark replication key fields as automatic inclusion.
    for field_name in (getattr(stream_obj, "replication_keys") or []):
        if field_name in schema.get("properties", {}):
            mdata = metadata.write(
                mdata, ("properties", field_name), "inclusion", "automatic"
            )

    parent_tap_stream_id = getattr(stream_obj, "parent", None)
    if parent_tap_stream_id:
        mdata = metadata.write(mdata, (), "parent-tap-stream-id", parent_tap_stream_id)

    return metadata.to_list(mdata)


def _validate_stream_access(client, stream_name: str, stream_obj) -> bool:
    """
    Probe whether the client credentials have read access to a parent stream.
    Child streams are skipped (they are validated implicitly via parent exclusion).
    Returns True if accessible or if the stream is a child; False on 403 Forbidden.
    """
    instance = stream_obj(client=client)
    if instance.parent:
        return True  # child access is governed by the parent check
    try:
        instance.check_access()
        return True
    except AmazonAdsForbiddenError:
        LOGGER.warning(
            "Stream '%s' does not have read permission, excluding from catalog.",
            stream_name,
        )
        return False


def _prune_inaccessible_children(schemas: Dict, field_metadata: Dict) -> None:
    """
    Remove child streams from the catalog whose parent stream was excluded.
    Mutates schemas and field_metadata in place.
    """
    for name, stream_cls in list(STREAMS.items()):
        if name in schemas and stream_cls.parent and stream_cls.parent not in schemas:
            LOGGER.warning(
                "Stream '%s' excluded from catalog because its parent stream '%s' is not accessible.",
                name, stream_cls.parent,
            )
            schemas.pop(name)
            field_metadata.pop(name)


def get_schemas(client) -> Tuple[Dict, Dict]:
    """
    Build catalog schemas and metadata for all streams.
    If a client is provided, streams that the credentials cannot access (HTTP 403)
    are excluded from the returned catalog along with any of their child streams.
    Raises AmazonAdsForbiddenError if no parent streams are accessible.
    Pass None to skip access checks (e.g. in unit tests or when running without credentials).
    """
    schemas = {}
    field_metadata = {}

    refs = load_schema_references()
    for stream_name, stream_obj in STREAMS.items():
        raw_schema = _load_schema(stream_name)
        schemas[stream_name] = raw_schema
        resolved_schema = singer.resolve_schema_references(raw_schema, refs)
        field_metadata[stream_name] = _build_metadata(stream_obj, resolved_schema)

    if client:
        error_list = [
            stream_name
            for stream_name, stream_obj in STREAMS.items()
            if stream_name in schemas
            and not _validate_stream_access(client, stream_name, stream_obj)
        ]
        for stream_name in error_list:
            schemas.pop(stream_name, None)
            field_metadata.pop(stream_name, None)

        _prune_inaccessible_children(schemas, field_metadata)

        if error_list:
            total_parent_streams = len([s for s in STREAMS.values() if not s.parent])
            if len(error_list) == total_parent_streams:
                raise AmazonAdsForbiddenError(
                    "HTTP-error-code: 403, Error: The account credentials supplied do not have 'read' access to any "
                    "of the streams supported by the tap. Data collection cannot be initiated due to lack of permissions."
                )
            LOGGER.warning(
                "The account credentials supplied do not have 'read' access to the following stream(s): %s. "
                "These streams have been excluded from the catalog.",
                ", ".join(error_list),
            )

    return schemas, field_metadata
