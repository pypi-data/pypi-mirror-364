r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FabricZoneset", "FabricZonesetSchema"]
__pdoc__ = {
    "FabricZonesetSchema.resource": False,
    "FabricZonesetSchema.opts": False,
    "FabricZoneset": False,
}


class FabricZonesetSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FabricZoneset object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the Fibre Channel zoneset.


Example: zoneset1 """

    @property
    def resource(self):
        return FabricZoneset

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FabricZoneset(Resource):

    _schema = FabricZonesetSchema
