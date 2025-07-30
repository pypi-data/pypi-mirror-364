r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["DiskStats", "DiskStatsSchema"]
__pdoc__ = {
    "DiskStatsSchema.resource": False,
    "DiskStatsSchema.opts": False,
    "DiskStats": False,
}


class DiskStatsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the DiskStats object"""

    average_latency = Size(data_key="average_latency", allow_none=True)
    r""" Average I/O latency across all active paths, in milliseconds.

Example: 3 """

    iops_total = Size(data_key="iops_total", allow_none=True)
    r""" Total I/O operations per second read and written to this disk across all active paths.

Example: 12854 """

    path_error_count = Size(data_key="path_error_count", allow_none=True)
    r""" Disk path error count; failed I/O operations.

Example: 0 """

    power_on_hours = Size(data_key="power_on_hours", allow_none=True)
    r""" Hours powered on.

Example: 21016 """

    throughput = Size(data_key="throughput", allow_none=True)
    r""" Total disk throughput per second across all active paths, in bytes.

Example: 1957888 """

    @property
    def resource(self):
        return DiskStats

    gettable_fields = [
        "average_latency",
        "iops_total",
        "path_error_count",
        "power_on_hours",
        "throughput",
    ]
    """average_latency,iops_total,path_error_count,power_on_hours,throughput,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class DiskStats(Resource):

    _schema = DiskStatsSchema
