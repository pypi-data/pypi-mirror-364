r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["StorageBridgePathsTargetPort", "StorageBridgePathsTargetPortSchema"]
__pdoc__ = {
    "StorageBridgePathsTargetPortSchema.resource": False,
    "StorageBridgePathsTargetPortSchema.opts": False,
    "StorageBridgePathsTargetPort": False,
}


class StorageBridgePathsTargetPortSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the StorageBridgePathsTargetPort object"""

    id = marshmallow_fields.Str(data_key="id", allow_none=True)
    r""" Target side switch port id

Example: 100050eb1a238892 """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Target side switch port name

Example: rtp-fc03-41kk11:6 """

    wwn = marshmallow_fields.Str(data_key="wwn", allow_none=True)
    r""" Target side switch port world wide name

Example: 2100001086a54100 """

    @property
    def resource(self):
        return StorageBridgePathsTargetPort

    gettable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""

    patchable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""

    postable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""


class StorageBridgePathsTargetPort(Resource):

    _schema = StorageBridgePathsTargetPortSchema
