r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NodeStatistics", "NodeStatisticsSchema"]
__pdoc__ = {
    "NodeStatisticsSchema.resource": False,
    "NodeStatisticsSchema.opts": False,
    "NodeStatistics": False,
}


class NodeStatisticsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NodeStatistics object"""

    processor_utilization_base = Size(data_key="processor_utilization_base", allow_none=True)
    r""" Base counter for CPU Utilization.

Example: 12345123 """

    processor_utilization_raw = Size(data_key="processor_utilization_raw", allow_none=True)
    r""" Raw CPU utilization for the node. The change in this value over time should be divided by corresponding change in processor_utilization_base, then multiplied by 100 to calculate the percentage CPU utilization for the node. For example: ((processor_utilization_raw_t2 - processor_utilization_raw_t1) / (processor_utilization_base_t2 - processor_utilization_base_t1)) * 100.


Example: 13 """

    status = marshmallow_fields.Str(data_key="status", allow_none=True)
    r""" Errors associated with the sample. For example, if the aggregation of data over multiple nodes fails, then any partial errors might return "ok" on success or "error" on an internal uncategorized failure. Whenever a sample collection is missed but done at a later time, it is back filled to the previous 15 second timestamp and tagged with "backfilled_data". "inconsistent_delta_time" is encountered when the time between two collections is not the same for all nodes. Therefore, the aggregated value might be over or under inflated. "Negative_delta" is returned when an expected monotonically increasing value has decreased in value. "inconsistent_old_data" is returned when one or more nodes do not have the latest data.

Valid choices:

* ok
* error
* partial_no_data
* partial_no_uuid
* partial_no_response
* partial_other_error
* negative_delta
* backfilled_data
* inconsistent_delta_time
* inconsistent_old_data """

    timestamp = ImpreciseDateTime(data_key="timestamp", allow_none=True)
    r""" The timestamp of the performance data.

Example: 2017-01-25T11:20:13.000+0000 """

    @property
    def resource(self):
        return NodeStatistics

    gettable_fields = [
        "processor_utilization_base",
        "processor_utilization_raw",
        "status",
        "timestamp",
    ]
    """processor_utilization_base,processor_utilization_raw,status,timestamp,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeStatistics(Resource):

    _schema = NodeStatisticsSchema
