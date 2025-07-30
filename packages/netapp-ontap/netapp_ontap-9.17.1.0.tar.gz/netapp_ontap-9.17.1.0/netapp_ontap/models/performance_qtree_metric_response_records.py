r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["PerformanceQtreeMetricResponseRecords", "PerformanceQtreeMetricResponseRecordsSchema"]
__pdoc__ = {
    "PerformanceQtreeMetricResponseRecordsSchema.resource": False,
    "PerformanceQtreeMetricResponseRecordsSchema.opts": False,
    "PerformanceQtreeMetricResponseRecords": False,
}


class PerformanceQtreeMetricResponseRecordsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the PerformanceQtreeMetricResponseRecords object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the performance_qtree_metric_response_records. """

    duration = marshmallow_fields.Str(data_key="duration", allow_none=True)
    r""" The duration over which this sample is calculated. The time durations are represented in the ISO-8601 standard format. Samples can be calculated over the following durations:


Valid choices:

* PT4M
* PT30M
* PT2H
* P1D
* PT5M """

    iops = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", unknown=EXCLUDE, data_key="iops", allow_none=True)
    r""" The iops field of the performance_qtree_metric_response_records. """

    latency = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", unknown=EXCLUDE, data_key="latency", allow_none=True)
    r""" The latency field of the performance_qtree_metric_response_records. """

    qtree = marshmallow_fields.Nested("netapp_ontap.resources.qtree.QtreeSchema", unknown=EXCLUDE, data_key="qtree", allow_none=True)
    r""" The qtree field of the performance_qtree_metric_response_records. """

    status = marshmallow_fields.Str(data_key="status", allow_none=True)
    r""" Errors associated with the sample. For example, if the aggregation of data over multiple nodes fails, then any partial errors might return "ok" on success or "error" on an internal uncategorized failure. Whenever a sample collection is missed but done at a later time, it is back filled to the previous 15 second timestamp and tagged with "backfilled_data". "Inconsistent_ delta_time" is encountered when the time between two collections is not the same for all nodes. Therefore, the aggregated value might be over or under inflated. "Negative_delta" is returned when an expected monotonically increasing value has decreased in value. "Inconsistent_old_data" is returned when one or more nodes do not have the latest data.

Valid choices:

* ok
* error
* partial_no_data
* partial_no_response
* partial_other_error
* negative_delta
* not_found
* backfilled_data
* inconsistent_delta_time
* inconsistent_old_data
* partial_no_uuid """

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm", allow_none=True)
    r""" The svm field of the performance_qtree_metric_response_records. """

    throughput = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", unknown=EXCLUDE, data_key="throughput", allow_none=True)
    r""" The throughput field of the performance_qtree_metric_response_records. """

    timestamp = ImpreciseDateTime(data_key="timestamp", allow_none=True)
    r""" The timestamp of the performance data.

Example: 2017-01-25T11:20:13.000+0000 """

    volume = marshmallow_fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume", allow_none=True)
    r""" The volume field of the performance_qtree_metric_response_records. """

    @property
    def resource(self):
        return PerformanceQtreeMetricResponseRecords

    gettable_fields = [
        "links",
        "duration",
        "iops.other",
        "iops.read",
        "iops.total",
        "iops.write",
        "latency.other",
        "latency.read",
        "latency.total",
        "latency.write",
        "qtree.links",
        "qtree.id",
        "qtree.name",
        "status",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "throughput.other",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,duration,iops.other,iops.read,iops.total,iops.write,latency.other,latency.read,latency.total,latency.write,qtree.links,qtree.id,qtree.name,status,svm.links,svm.name,svm.uuid,throughput.other,throughput.read,throughput.total,throughput.write,timestamp,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "duration",
        "iops.other",
        "iops.read",
        "iops.total",
        "iops.write",
        "latency.other",
        "latency.read",
        "latency.total",
        "latency.write",
        "qtree.id",
        "qtree.name",
        "svm.name",
        "svm.uuid",
        "throughput.other",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "volume.name",
        "volume.uuid",
    ]
    """duration,iops.other,iops.read,iops.total,iops.write,latency.other,latency.read,latency.total,latency.write,qtree.id,qtree.name,svm.name,svm.uuid,throughput.other,throughput.read,throughput.total,throughput.write,volume.name,volume.uuid,"""

    postable_fields = [
        "duration",
        "iops.other",
        "iops.read",
        "iops.total",
        "iops.write",
        "latency.other",
        "latency.read",
        "latency.total",
        "latency.write",
        "qtree.id",
        "qtree.name",
        "svm.name",
        "svm.uuid",
        "throughput.other",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "volume.name",
        "volume.uuid",
    ]
    """duration,iops.other,iops.read,iops.total,iops.write,latency.other,latency.read,latency.total,latency.write,qtree.id,qtree.name,svm.name,svm.uuid,throughput.other,throughput.read,throughput.total,throughput.write,volume.name,volume.uuid,"""


class PerformanceQtreeMetricResponseRecords(Resource):

    _schema = PerformanceQtreeMetricResponseRecordsSchema
