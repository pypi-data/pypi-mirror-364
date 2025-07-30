r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeMetricFlexcache", "VolumeMetricFlexcacheSchema"]
__pdoc__ = {
    "VolumeMetricFlexcacheSchema.resource": False,
    "VolumeMetricFlexcacheSchema.opts": False,
    "VolumeMetricFlexcache": False,
}


class VolumeMetricFlexcacheSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeMetricFlexcache object"""

    bandwidth_savings = Size(data_key="bandwidth_savings", allow_none=True)
    r""" Bandwidth savings denoting the amount of data served locally by the cache, in bytes.

Example: 4096 """

    cache_miss_percent = Size(data_key="cache_miss_percent", allow_none=True)
    r""" Cache miss percentage.

Example: 20 """

    duration = marshmallow_fields.Str(data_key="duration", allow_none=True)
    r""" The duration over which this sample is calculated. The time durations are represented in the ISO-8601 standard format. Samples can be calculated over the following durations:


Valid choices:

* PT15S
* PT5M
* PT30M
* PT2H
* PT1D """

    status = marshmallow_fields.Str(data_key="status", allow_none=True)
    r""" Errors associated with the sample. For example, if the aggregation of data over multiple nodes fails, then any partial errors might return "ok" on success or "error" on an internal uncategorized failure. Whenever a sample collection is missed but done at a later time, it is back filled to the previous 15 second timestamp and tagged with "backfilled_data". "Inconsistent_ delta_time" is encountered when the time between two collections is not the same for all nodes. Therefore, the aggregated value might be over or under inflated. "Negative_delta" is returned when an expected monotonically increasing value has decreased in value. "Inconsistent_old_data" is returned when one or more nodes do not have the latest data.

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
        return VolumeMetricFlexcache

    gettable_fields = [
        "bandwidth_savings",
        "cache_miss_percent",
        "duration",
        "status",
        "timestamp",
    ]
    """bandwidth_savings,cache_miss_percent,duration,status,timestamp,"""

    patchable_fields = [
        "bandwidth_savings",
        "cache_miss_percent",
    ]
    """bandwidth_savings,cache_miss_percent,"""

    postable_fields = [
        "bandwidth_savings",
        "cache_miss_percent",
    ]
    """bandwidth_savings,cache_miss_percent,"""


class VolumeMetricFlexcache(Resource):

    _schema = VolumeMetricFlexcacheSchema
