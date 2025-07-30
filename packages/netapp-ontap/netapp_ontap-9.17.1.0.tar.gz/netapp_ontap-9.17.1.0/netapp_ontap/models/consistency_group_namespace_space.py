r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupNamespaceSpace", "ConsistencyGroupNamespaceSpaceSchema"]
__pdoc__ = {
    "ConsistencyGroupNamespaceSpaceSchema.resource": False,
    "ConsistencyGroupNamespaceSpaceSchema.opts": False,
    "ConsistencyGroupNamespaceSpace": False,
}


class ConsistencyGroupNamespaceSpaceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupNamespaceSpace object"""

    block_size = Size(data_key="block_size", allow_none=True)
    r""" The size of blocks in the namespace, in bytes.<br/>
Valid in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone.
 Valid in POST. """

    guarantee = marshmallow_fields.Nested("netapp_ontap.models.consistency_group_namespace_space_guarantee.ConsistencyGroupNamespaceSpaceGuaranteeSchema", unknown=EXCLUDE, data_key="guarantee", allow_none=True)
    r""" Properties that request and report the space guarantee for the NVMe namespace. """

    size = Size(data_key="size", allow_none=True)
    r""" The total provisioned size of the NVMe namespace. Valid in POST and PATCH. The NVMe namespace size can be increased but not reduced using the REST interface.<br/>
The maximum and minimum sizes listed here are the absolute maximum and absolute minimum sizes, in bytes. The maximum size is variable with respect to large NVMe namespace support in ONTAP. If large namespaces are supported, the maximum size is 128 TB (140737488355328 bytes) and if not supported, the maximum size is just under 16 TB (17557557870592 bytes). The minimum size supported is always 4096 bytes.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation.


Example: 1073741824 """

    used = Size(data_key="used", allow_none=True)
    r""" The amount of space consumed by the main data stream of the NVMe namespace.<br/>
This value is the total space consumed in the volume by the NVMe namespace, including filesystem overhead, but excluding prefix and suffix streams. Due to internal filesystem overhead and the many ways NVMe filesystems and applications utilize blocks within a namespace, this value does not necessarily reflect actual consumption/availability from the perspective of the filesystem or application. Without specific knowledge of how the namespace blocks are utilized outside of ONTAP, this property should not be used as an indicator for an out-of-space condition.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation. """

    @property
    def resource(self):
        return ConsistencyGroupNamespaceSpace

    gettable_fields = [
        "block_size",
        "guarantee",
        "size",
        "used",
    ]
    """block_size,guarantee,size,used,"""

    patchable_fields = [
        "guarantee",
        "size",
    ]
    """guarantee,size,"""

    postable_fields = [
        "block_size",
        "guarantee",
        "size",
    ]
    """block_size,guarantee,size,"""


class ConsistencyGroupNamespaceSpace(Resource):

    _schema = ConsistencyGroupNamespaceSpaceSchema
