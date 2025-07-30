r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
Retrieves historical performance and capacity metrics for a consistency group.
## Examples
### Retrieving historical performance and space metrics for a consistency group for the past day
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupMetrics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            ConsistencyGroupMetrics.get_collection("{uuid}", interval="1d", fields="**")
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    ConsistencyGroupMetrics(
        {
            "timestamp": "2023-02-23T03:17:45+00:00",
            "used_space": 1810432,
            "throughput": {"read": 0, "total": 0, "other": 0, "write": 0},
            "iops": {"read": 0, "total": 0, "other": 0, "write": 0},
            "status": "ok",
            "available_space": 862216192,
            "size": 864026624,
            "latency": {"read": 0, "total": 0, "other": 0, "write": 0},
            "duration": "PT15S",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/5069acd5-b325-11ed-a958-005056ac6b54/metrics/2023-02-23T03%3A17%3A45Z?fields=**"
                }
            },
        }
    ),
    ConsistencyGroupMetrics(
        {
            "timestamp": "2023-02-23T02:18:00+00:00",
            "used_space": 0,
            "throughput": {"read": 0, "total": 0, "other": 0, "write": 0},
            "iops": {"read": 0, "total": 0, "other": 0, "write": 0},
            "status": "partial_no_data",
            "available_space": 0,
            "size": 0,
            "latency": {"read": 0, "total": 0, "other": 0, "write": 0},
            "duration": "PT15S",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/5069acd5-b325-11ed-a958-005056ac6b54/metrics/2023-02-23T02%3A18%3A00Z?fields=**"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving historical metrics within a time range defined by timestamp
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroupMetrics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            ConsistencyGroupMetrics.get_collection(
                "{uuid}",
                fields="**",
                timestamp="2023-02-23T03:36:45Z..2023-02-23T03:36:30Z",
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    ConsistencyGroupMetrics(
        {
            "timestamp": "2023-02-23T03:36:45+00:00",
            "used_space": 1843200,
            "throughput": {"read": 0, "total": 0, "other": 0, "write": 0},
            "iops": {"read": 0, "total": 0, "other": 0, "write": 0},
            "status": "ok",
            "available_space": 862183424,
            "size": 864026624,
            "latency": {"read": 0, "total": 0, "other": 0, "write": 0},
            "duration": "PT15S",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/5069acd5-b325-11ed-a958-005056ac6b54/metrics/2023-02-23T03%3A36%3A45Z?fields=**"
                }
            },
        }
    ),
    ConsistencyGroupMetrics(
        {
            "timestamp": "2023-02-23T03:36:30+00:00",
            "used_space": 1843200,
            "throughput": {"read": 0, "total": 0, "other": 0, "write": 0},
            "iops": {"read": 0, "total": 0, "other": 0, "write": 0},
            "status": "ok",
            "available_space": 862183424,
            "size": 864026624,
            "latency": {"read": 0, "total": 0, "other": 0, "write": 0},
            "duration": "PT15S",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/5069acd5-b325-11ed-a958-005056ac6b54/metrics/2023-02-23T03%3A36%3A30Z?fields=**"
                }
            },
        }
    ),
]

```
</div>
</div>
"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

from marshmallow import fields as marshmallow_fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size
from netapp_ontap.raw_resource import RawResource

from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["ConsistencyGroupMetrics", "ConsistencyGroupMetricsSchema"]
__pdoc__ = {
    "ConsistencyGroupMetricsSchema.resource": False,
    "ConsistencyGroupMetricsSchema.opts": False,
}


class ConsistencyGroupMetricsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupMetrics object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the consistency_group_metrics."""

    available_space = Size(
        data_key="available_space",
        allow_none=True,
    )
    r""" The total space available in the consistency group, in bytes.

Example: 4096"""

    duration = marshmallow_fields.Str(
        data_key="duration",
        validate=enum_validation(['PT15S', 'PT4M', 'PT30M', 'PT2H', 'P1D', 'PT5M']),
        allow_none=True,
    )
    r""" The duration over which this sample is calculated. The time durations are represented in the ISO-8601 standard format. Samples can be calculated over the following durations:


Valid choices:

* PT15S
* PT4M
* PT30M
* PT2H
* P1D
* PT5M"""

    iops = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", data_key="iops", unknown=EXCLUDE, allow_none=True)
    r""" The iops field of the consistency_group_metrics."""

    latency = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", data_key="latency", unknown=EXCLUDE, allow_none=True)
    r""" The latency field of the consistency_group_metrics."""

    size = Size(
        data_key="size",
        allow_none=True,
    )
    r""" The total size of the consistency group, in bytes.

Example: 4096"""

    status = marshmallow_fields.Str(
        data_key="status",
        validate=enum_validation(['ok', 'error', 'partial_no_data', 'partial_no_uuid', 'partial_no_response', 'partial_other_error', 'negative_delta', 'backfilled_data', 'inconsistent_delta_time', 'inconsistent_old_data']),
        allow_none=True,
    )
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
* inconsistent_old_data"""

    throughput = marshmallow_fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", data_key="throughput", unknown=EXCLUDE, allow_none=True)
    r""" The throughput field of the consistency_group_metrics."""

    timestamp = ImpreciseDateTime(
        data_key="timestamp",
        allow_none=True,
    )
    r""" The timestamp of the performance and capacity data.

Example: 2017-01-25T11:20:13.000+0000"""

    used_space = Size(
        data_key="used_space",
        allow_none=True,
    )
    r""" The total space used in the consistency group, in bytes.

Example: 4096"""

    @property
    def resource(self):
        return ConsistencyGroupMetrics

    gettable_fields = [
        "links",
        "available_space",
        "duration",
        "iops.other",
        "iops.read",
        "iops.total",
        "iops.write",
        "latency.other",
        "latency.read",
        "latency.total",
        "latency.write",
        "size",
        "status",
        "throughput.other",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
        "used_space",
    ]
    """links,available_space,duration,iops.other,iops.read,iops.total,iops.write,latency.other,latency.read,latency.total,latency.write,size,status,throughput.other,throughput.read,throughput.total,throughput.write,timestamp,used_space,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

class ConsistencyGroupMetrics(Resource):
    r""" Performance and capacity numbers, such as, IOPS, latency, throughput, used space, and available space. """

    _schema = ConsistencyGroupMetricsSchema
    _path = "/api/application/consistency-groups/{consistency_group[uuid]}/metrics"
    _keys = ["consistency_group.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves historical performance and capacity metrics for a consistency group.
### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/metrics`](#docs-application-application_consistency-groups_{consistency_group.uuid}_metrics)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ConsistencyGroupMetrics resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def fast_get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["RawResource"]:
        """Returns a list of RawResources that represent ConsistencyGroupMetrics resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves historical performance and capacity metrics for a consistency group.
### Learn more
* [`DOC /application/consistency-groups/{consistency_group.uuid}/metrics`](#docs-application-application_consistency-groups_{consistency_group.uuid}_metrics)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






