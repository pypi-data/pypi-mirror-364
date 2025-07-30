r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["StorageBridgeLastReboot", "StorageBridgeLastRebootSchema"]
__pdoc__ = {
    "StorageBridgeLastRebootSchema.resource": False,
    "StorageBridgeLastRebootSchema.opts": False,
    "StorageBridgeLastReboot": False,
}


class StorageBridgeLastRebootSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the StorageBridgeLastReboot object"""

    reason = marshmallow_fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason", allow_none=True)
    r""" The error message and code explaining why the bridge rebooted. """

    time = ImpreciseDateTime(data_key="time", allow_none=True)
    r""" The time field of the storage_bridge_last_reboot.

Example: 2020-12-09T05:47:58.000+0000 """

    @property
    def resource(self):
        return StorageBridgeLastReboot

    gettable_fields = [
        "reason",
        "time",
    ]
    """reason,time,"""

    patchable_fields = [
        "time",
    ]
    """time,"""

    postable_fields = [
        "time",
    ]
    """time,"""


class StorageBridgeLastReboot(Resource):

    _schema = StorageBridgeLastRebootSchema
