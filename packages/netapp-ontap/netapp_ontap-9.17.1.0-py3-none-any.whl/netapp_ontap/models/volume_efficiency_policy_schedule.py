r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeEfficiencyPolicySchedule", "VolumeEfficiencyPolicyScheduleSchema"]
__pdoc__ = {
    "VolumeEfficiencyPolicyScheduleSchema.resource": False,
    "VolumeEfficiencyPolicyScheduleSchema.opts": False,
    "VolumeEfficiencyPolicySchedule": False,
}


class VolumeEfficiencyPolicyScheduleSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeEfficiencyPolicySchedule object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Schedule at which volume efficiency policies are captured on the SVM. Some common schedules already defined in the system are hourly, daily, weekly, at 5 minute intervals, and at 8 hour intervals. Volume efficiency policies with custom schedules can be referenced. """

    @property
    def resource(self):
        return VolumeEfficiencyPolicySchedule

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


class VolumeEfficiencyPolicySchedule(Resource):

    _schema = VolumeEfficiencyPolicyScheduleSchema
