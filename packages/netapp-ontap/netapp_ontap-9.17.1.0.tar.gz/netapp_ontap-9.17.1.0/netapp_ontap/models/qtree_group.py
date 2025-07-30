r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["QtreeGroup", "QtreeGroupSchema"]
__pdoc__ = {
    "QtreeGroupSchema.resource": False,
    "QtreeGroupSchema.opts": False,
    "QtreeGroup": False,
}


class QtreeGroupSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the QtreeGroup object"""

    id = marshmallow_fields.Str(data_key="id", allow_none=True)
    r""" The numeric ID of the group that owns the qtree. Valid in POST or PATCH.

Example: 20001 """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Alphanumeric group name of group that owns the qtree. Valid in POST or PATCH.

Example: unix_group1 """

    @property
    def resource(self):
        return QtreeGroup

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class QtreeGroup(Resource):

    _schema = QtreeGroupSchema
