import os
import json
import singer
from typing import Dict, Tuple
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


def get_schemas(client=None) -> Tuple[Dict, Dict]:
    """
    Load the schema references, prepare metadata for each streams and return schema and metadata for the catalog.
    If a client is provided, each parent stream's access is verified; streams the credentials cannot read
    are excluded from the returned catalog along with any of their child streams.
    """
    schemas = {}
    field_metadata = {}
    error_list = []

    refs = load_schema_references()
    for stream_name, stream_obj in STREAMS.items():
        schema_path = get_abs_path("schemas/{}.json".format(stream_name))
        with open(schema_path) as file:
            schema = json.load(file)

        schemas[stream_name] = schema
        schema = singer.resolve_schema_references(schema, refs)

        mdata = metadata.new()
        mdata = metadata.get_standard_metadata(
            schema=schema,
            key_properties=getattr(stream_obj, "key_properties"),
            valid_replication_keys=(getattr(stream_obj, "replication_keys") or []),
            replication_method=getattr(stream_obj, "replication_method"),
        )
        mdata = metadata.to_map(mdata)

        automatic_keys = getattr(stream_obj, "replication_keys") or []
        for field_name in schema["properties"].keys():
            if field_name in automatic_keys:
                mdata = metadata.write(
                    mdata, ("properties", field_name), "inclusion", "automatic"
                )

        parent_tap_stream_id = getattr(stream_obj, "parent", None)
        if parent_tap_stream_id:
            mdata = metadata.write(mdata, (), 'parent-tap-stream-id', parent_tap_stream_id)

        mdata = metadata.write(mdata, (), 'selected', True)
        mdata = metadata.to_list(mdata)
        field_metadata[stream_name] = mdata

        if client:
            try:
                # Call check_access only for parent (top-level) streams.
                # If the credentials lack read permission, AmazonAdsForbiddenError is raised
                # by the client and the stream is excluded from the catalog.
                instance = stream_obj(client=client)
                if not instance.parent:
                    instance.check_access()
            except AmazonAdsForbiddenError:
                LOGGER.warning(
                    "Stream '%s' does not have read permission, excluding from catalog.",
                    stream_name,
                )
                schemas.pop(stream_name, None)
                field_metadata.pop(stream_name, None)
                error_list.append(stream_name)

    if client:
        # Remove child streams whose parent was excluded.
        for name, stream_cls in list(STREAMS.items()):
            if name in schemas and stream_cls.parent and stream_cls.parent not in schemas:
                LOGGER.warning(
                    "Stream '%s' excluded from catalog because its parent stream '%s' is not accessible.",
                    name, stream_cls.parent,
                )
                schemas.pop(name, None)
                field_metadata.pop(name, None)

        if error_list:
            total_parent_streams = len([s for s in STREAMS.values() if not s.parent])
            streams_name = ", ".join(error_list)
            if len(error_list) == total_parent_streams:
                raise AmazonAdsForbiddenError(
                    "HTTP-error-code: 403, Error: The account credentials supplied do not have 'read' access to any "
                    "of the streams supported by the tap. Data collection cannot be initiated due to lack of permissions."
                )
            LOGGER.warning(
                "The account credentials supplied do not have 'read' access to the following stream(s): %s. "
                "These streams have been excluded from the catalog.",
                streams_name,
            )

    return schemas, field_metadata

