r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeApplication", "VolumeApplicationSchema"]
__pdoc__ = {
    "VolumeApplicationSchema.resource": False,
    "VolumeApplicationSchema.opts": False,
    "VolumeApplication": False,
}


class VolumeApplicationSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeApplication object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Name of the application to which the volume belongs. Available only when the volume is part of an application. """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" UUID of the application to which the volume belongs. Available only when the volume is part of an application.

Example: 1cd8a442-86d1-11e0-ae1d-123478563412 """

    @property
    def resource(self):
        return VolumeApplication

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeApplication(Resource):

    _schema = VolumeApplicationSchema
