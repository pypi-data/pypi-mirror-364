r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["StoragePoolSpareAllocationUnit", "StoragePoolSpareAllocationUnitSchema"]
__pdoc__ = {
    "StoragePoolSpareAllocationUnitSchema.resource": False,
    "StoragePoolSpareAllocationUnitSchema.opts": False,
    "StoragePoolSpareAllocationUnit": False,
}


class StoragePoolSpareAllocationUnitSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the StoragePoolSpareAllocationUnit object"""

    available_size = Size(data_key="available_size", allow_none=True)
    r""" The usable capacity of this set of allocation units. """

    count = Size(data_key="count", allow_none=True)
    r""" The number of spare allocation units on this node. """

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the storage_pool_spare_allocation_unit. """

    size = Size(data_key="size", allow_none=True)
    r""" Size of each allocation unit. """

    syncmirror_pool = marshmallow_fields.Str(data_key="syncmirror_pool", allow_none=True)
    r""" The RAID SyncMirror Pool to which this allocation unit is assigned.

Valid choices:

* pool0
* pool1 """

    @property
    def resource(self):
        return StoragePoolSpareAllocationUnit

    gettable_fields = [
        "available_size",
        "count",
        "node.links",
        "node.name",
        "node.uuid",
        "size",
        "syncmirror_pool",
    ]
    """available_size,count,node.links,node.name,node.uuid,size,syncmirror_pool,"""

    patchable_fields = [
        "count",
        "node.name",
        "node.uuid",
    ]
    """count,node.name,node.uuid,"""

    postable_fields = [
        "count",
        "node.name",
        "node.uuid",
    ]
    """count,node.name,node.uuid,"""


class StoragePoolSpareAllocationUnit(Resource):

    _schema = StoragePoolSpareAllocationUnitSchema
