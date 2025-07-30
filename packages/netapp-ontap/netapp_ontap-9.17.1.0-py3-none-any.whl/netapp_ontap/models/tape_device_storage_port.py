r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["TapeDeviceStoragePort", "TapeDeviceStoragePortSchema"]
__pdoc__ = {
    "TapeDeviceStoragePortSchema.resource": False,
    "TapeDeviceStoragePortSchema.opts": False,
    "TapeDeviceStoragePort": False,
}


class TapeDeviceStoragePortSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the TapeDeviceStoragePort object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Initiator port.

Example: 2b """

    @property
    def resource(self):
        return TapeDeviceStoragePort

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class TapeDeviceStoragePort(Resource):

    _schema = TapeDeviceStoragePortSchema
