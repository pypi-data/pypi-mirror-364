r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupSpace", "ConsistencyGroupSpaceSchema"]
__pdoc__ = {
    "ConsistencyGroupSpaceSchema.resource": False,
    "ConsistencyGroupSpaceSchema.opts": False,
    "ConsistencyGroupSpace": False,
}


class ConsistencyGroupSpaceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupSpace object"""

    available = Size(data_key="available", allow_none=True)
    r""" The amount of space available in the consistency group, in bytes.<br/>


Example: 5737418 """

    size = Size(data_key="size", allow_none=True)
    r""" The total provisioned size of the consistency group, in bytes.<br/>


Example: 1073741824 """

    used = Size(data_key="used", allow_none=True)
    r""" The amount of space consumed in the consistency group, in bytes.<br/>


Example: 5737418 """

    @property
    def resource(self):
        return ConsistencyGroupSpace

    gettable_fields = [
        "available",
        "size",
        "used",
    ]
    """available,size,used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ConsistencyGroupSpace(Resource):

    _schema = ConsistencyGroupSpaceSchema
