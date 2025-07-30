r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["PortMetricsResponseRecords", "PortMetricsResponseRecordsSchema"]
__pdoc__ = {
    "PortMetricsResponseRecordsSchema.resource": False,
    "PortMetricsResponseRecordsSchema.opts": False,
    "PortMetricsResponseRecords": False,
}


class PortMetricsResponseRecordsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the PortMetricsResponseRecords object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the port_metrics_response_records. """

    duration = marshmallow_fields.Str(data_key="duration", allow_none=True)
    r""" The duration over which this sample is calculated. The time durations are represented in the ISO-8601 standard format. Samples can be calculated over the following durations:


Valid choices:

* PT15S
* PT4M
* PT30M
* PT2H
* P1D
* PT5M """

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

    throughput = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type_rwt.PerformanceMetricIoTypeRwtSchema", unknown=EXCLUDE, data_key="throughput", allow_none=True)
    r""" The throughput field of the port_metrics_response_records. """

    timestamp = ImpreciseDateTime(data_key="timestamp", allow_none=True)
    r""" The timestamp of the performance data.

Example: 2017-01-25T11:20:13.000+0000 """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" Port UUID

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return PortMetricsResponseRecords

    gettable_fields = [
        "links",
        "duration",
        "status",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
        "uuid",
    ]
    """links,duration,status,throughput.read,throughput.total,throughput.write,timestamp,uuid,"""

    patchable_fields = [
        "duration",
        "status",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
    ]
    """duration,status,throughput.read,throughput.total,throughput.write,timestamp,"""

    postable_fields = [
        "duration",
        "status",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
    ]
    """duration,status,throughput.read,throughput.total,throughput.write,timestamp,"""


class PortMetricsResponseRecords(Resource):

    _schema = PortMetricsResponseRecordsSchema
