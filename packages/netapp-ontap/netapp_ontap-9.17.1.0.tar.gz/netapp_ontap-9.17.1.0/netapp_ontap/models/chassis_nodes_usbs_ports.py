r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ChassisNodesUsbsPorts", "ChassisNodesUsbsPortsSchema"]
__pdoc__ = {
    "ChassisNodesUsbsPortsSchema.resource": False,
    "ChassisNodesUsbsPortsSchema.opts": False,
    "ChassisNodesUsbsPorts": False,
}


class ChassisNodesUsbsPortsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ChassisNodesUsbsPorts object"""

    connected = marshmallow_fields.Boolean(data_key="connected", allow_none=True)
    r""" Indicates whether or not the USB port has a device connected to it. """

    @property
    def resource(self):
        return ChassisNodesUsbsPorts

    gettable_fields = [
        "connected",
    ]
    """connected,"""

    patchable_fields = [
        "connected",
    ]
    """connected,"""

    postable_fields = [
        "connected",
    ]
    """connected,"""


class ChassisNodesUsbsPorts(Resource):

    _schema = ChassisNodesUsbsPortsSchema
