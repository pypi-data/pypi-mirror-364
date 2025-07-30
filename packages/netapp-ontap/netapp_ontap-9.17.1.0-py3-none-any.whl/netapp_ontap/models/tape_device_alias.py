r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["TapeDeviceAlias", "TapeDeviceAliasSchema"]
__pdoc__ = {
    "TapeDeviceAliasSchema.resource": False,
    "TapeDeviceAliasSchema.opts": False,
    "TapeDeviceAlias": False,
}


class TapeDeviceAliasSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the TapeDeviceAlias object"""

    mapping = marshmallow_fields.Str(data_key="mapping", allow_none=True)
    r""" This field will no longer be supported in a future release. Use aliases.mapping instead.

Example: SN[10WT000933] """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" This field will no longer be supported in a future release. Use aliases.name instead.

Example: st6 """

    @property
    def resource(self):
        return TapeDeviceAlias

    gettable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""

    patchable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""

    postable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""


class TapeDeviceAlias(Resource):

    _schema = TapeDeviceAliasSchema
