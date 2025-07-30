r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPaths", "StorageSwitchPathsSchema"]
__pdoc__ = {
    "StorageSwitchPathsSchema.resource": False,
    "StorageSwitchPathsSchema.opts": False,
    "StorageSwitchPaths": False,
}


class StorageSwitchPathsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the StorageSwitchPaths object"""

    adapter = marshmallow_fields.Nested("netapp_ontap.models.storage_switch_paths_adapter.StorageSwitchPathsAdapterSchema", unknown=EXCLUDE, data_key="adapter", allow_none=True)
    r""" The adapter field of the storage_switch_paths. """

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the storage_switch_paths. """

    port = marshmallow_fields.Nested("netapp_ontap.models.storage_switch_paths_port.StorageSwitchPathsPortSchema", unknown=EXCLUDE, data_key="port", allow_none=True)
    r""" The port field of the storage_switch_paths. """

    @property
    def resource(self):
        return StorageSwitchPaths

    gettable_fields = [
        "adapter",
        "node.links",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.links,node.name,node.uuid,port,"""

    patchable_fields = [
        "adapter",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.name,node.uuid,port,"""

    postable_fields = [
        "adapter",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.name,node.uuid,port,"""


class StorageSwitchPaths(Resource):

    _schema = StorageSwitchPathsSchema
