r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SvmMigrationTimeMetrics", "SvmMigrationTimeMetricsSchema"]
__pdoc__ = {
    "SvmMigrationTimeMetricsSchema.resource": False,
    "SvmMigrationTimeMetricsSchema.opts": False,
    "SvmMigrationTimeMetrics": False,
}


class SvmMigrationTimeMetricsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SvmMigrationTimeMetrics object"""

    cutover_complete_time = ImpreciseDateTime(data_key="cutover_complete_time", allow_none=True)
    r""" Cutover end time

Example: 2020-12-03T03:30:19.000+0000 """

    cutover_start_time = ImpreciseDateTime(data_key="cutover_start_time", allow_none=True)
    r""" Cutover start time

Example: 2020-12-03T02:20:19.000+0000 """

    cutover_trigger_time = ImpreciseDateTime(data_key="cutover_trigger_time", allow_none=True)
    r""" Cutover trigger time

Example: 2020-12-03T03:15:19.000+0000 """

    end_time = ImpreciseDateTime(data_key="end_time", allow_none=True)
    r""" Migration end time

Example: 2020-12-03T03:36:19.000+0000 """

    last_pause_time = ImpreciseDateTime(data_key="last_pause_time", allow_none=True)
    r""" Last migration pause time

Example: 2020-12-03T02:50:19.000+0000 """

    last_post_ponr_retry_time = ImpreciseDateTime(data_key="last_post_ponr_retry_time", allow_none=True)
    r""" Last post point of no return retry time

Example: 2020-12-03T03:30:19.000+0000 """

    last_resume_time = ImpreciseDateTime(data_key="last_resume_time", allow_none=True)
    r""" Last migration resume time

Example: 2020-12-03T02:54:19.000+0000 """

    start_time = ImpreciseDateTime(data_key="start_time", allow_none=True)
    r""" Migration start time

Example: 2020-12-03T02:36:19.000+0000 """

    @property
    def resource(self):
        return SvmMigrationTimeMetrics

    gettable_fields = [
        "cutover_complete_time",
        "cutover_start_time",
        "cutover_trigger_time",
        "end_time",
        "last_pause_time",
        "last_post_ponr_retry_time",
        "last_resume_time",
        "start_time",
    ]
    """cutover_complete_time,cutover_start_time,cutover_trigger_time,end_time,last_pause_time,last_post_ponr_retry_time,last_resume_time,start_time,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SvmMigrationTimeMetrics(Resource):

    _schema = SvmMigrationTimeMetricsSchema
