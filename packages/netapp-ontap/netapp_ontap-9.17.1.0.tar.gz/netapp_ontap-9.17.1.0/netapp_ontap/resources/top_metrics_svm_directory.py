r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
You can use this API to retrieve a list of directories with the most I/O activity for FlexVol and FlexGroup volumes belonging to a specified SVM, within the past several seconds. To obtain this list, only the volumes which have the activity tracking feature enabled are considered. </br>
This API is used to provide insight into I/O activity and supports ordering by I/O activity types, namely `iops` and `throughput` metrics. Use the `top_metric` parameter to specify which type of I/O activity to filter for. This API supports returning only one I/O activity type per request.</br>
## Enabling and disabling activity tracking feature
The following APIs can be used to enable, disable, and retrieve the activity tracking state for a FlexVol or a FlexGroup volume.

* PATCH  /api/storage/volumes/{uuid} -d '{"activity_tracking.state":"on"}'
* PATCH  /api/storage/volumes/{uuid} -d '{"activity_tracking.state":"off"}'
* GET    /api/storage/volumes/{uuid}/?fields=activity_tracking
## Excluded volumes list
Optionally, the API returns an excluded list of activity tracking-enabled volumes, which were not accounted for when obtaining the list of clients with the most I/O activity for the SVM. This excluded list contains both the volume information and the reason for exclusion. </br>
## Approximate accounting and error bars
When too many directories have recent activity, some directories might be dropped from the list. In this situation, the spread of values in the `error` field increases, indicating that there are larger error bars on the value for `iops` or `throughput`. As the list becomes increasingly more approximate due to dropped entries, some of the directories that would have otherwise been included might not be present in the final list returned by the API.
## Failure to return list of directories with most I/O activity
The API can sometimes fail to return the list of directories with the most I/O activity, due to the following reasons:

* The volumes belonging to the SVM do not have the activity tracking feature enabled.
* The volumes belonging to the SVM have not had any recent NFS/CIFS client traffic.
* The NFS/CIFS client operations are being served by the client-side filesystem cache.
* The NFS/CIFS client operations are being buffered by the client operating system.
* On rare occasions, the incoming traffic pattern is not suitable to obtain the list of directories with the most I/O activity.
## Failure to return pathnames
The API can sometimes fail to obtain filesystem pathnames for certain directories, either due to internal transient errors or if those directories have been recently deleted.
In such cases, instead of the pathname, the API will return "{<volume_instance_uuid>.<fileid>}" for that directory.
## Retrieve a list of the directories with the most I/O activity
For a report on the directories with the most I/O activity returned in descending order, specify the I/O activity type you want to filter for by passing the `iops` or `throughput` property into the top_metric parameter. If the I/O activity type is not specified, by default the API returns a list of directories with the greatest number of average read operations per second. The current maximum number of directories returned by the API for an I/O activity type is 25.

* GET   /api/svm/svms/{svm.uuid}/top-metrics/directories
## Examples
### Retrieving a list of the directories with the greatest average number of read operations per second:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsSvmDirectory

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsSvmDirectory.get_collection("{svm.uuid}", top_metric="iops.read")
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    TopMetricsSvmDirectory(
        {
            "path": "/vol/fv1/dir1/dir2",
            "junction-path": "/fv1",
            "iops": {"read": 1495, "error": {"upper_bound": 1505, "lower_bound": 1495}},
            "svm": {"name": "vs1"},
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864/files/dir1%2Fdir2?return_metadata=true"
                }
            },
            "volume": {
                "uuid": "73b293df-e9d7-46cc-a9ce-2df8e52ef86",
                "name": "fv1",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef86"
                    }
                },
            },
        }
    ),
    TopMetricsSvmDirectory(
        {
            "path": "/vol/fv2/dir3/dir4",
            "junction-path": "/fv2",
            "iops": {"read": 1022, "error": {"upper_bound": 1032, "lower_bound": 1022}},
            "svm": {"name": "vs1"},
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/11b293df-e9d7-46cc-a9ce-2df8e52ef811/files/dir3%2Fdir4?return_metadata=true"
                }
            },
            "volume": {
                "uuid": "11b293df-e9d7-46cc-a9ce-2df8e52ef811",
                "name": "fv2",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/11b293df-e9d7-46cc-a9ce-2df8e52ef811"
                    }
                },
            },
        }
    ),
    TopMetricsSvmDirectory(
        {
            "path": "/vol/fv1/dir12",
            "junction-path": "/fv1",
            "iops": {"read": 345, "error": {"upper_bound": 355, "lower_bound": 345}},
            "svm": {"name": "vs1"},
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864/files/dir12?return_metadata=true"
                }
            },
            "volume": {
                "uuid": "73b293df-e9d7-46cc-a9ce-2df8e52ef864",
                "name": "fv1",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864"
                    }
                },
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a list of the directories with the most read traffic, with failure to obtain pathnames
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsSvmDirectory

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsSvmDirectory.get_collection("{svm.uuid}", top_metric="iops.read")
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    TopMetricsSvmDirectory(
        {
            "path": "73b293df-e9d7-46cc-a9ce-2df8e52ef86.1232",
            "junction-path": "/fv1",
            "iops": {"read": 1495, "error": {"upper_bound": 1505, "lower_bound": 1495}},
            "svm": {"name": "vs1"},
            "volume": {
                "uuid": "73b293df-e9d7-46cc-a9ce-2df8e52ef86",
                "name": "fv1",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef86"
                    }
                },
            },
        }
    ),
    TopMetricsSvmDirectory(
        {
            "path": "11b293df-e9d7-46cc-a9ce-2df8e52ef811.6574",
            "junction-path": "/fv2",
            "iops": {"read": 1022, "error": {"upper_bound": 1032, "lower_bound": 1022}},
            "svm": {"name": "vs1"},
            "volume": {
                "uuid": "11b293df-e9d7-46cc-a9ce-2df8e52ef811",
                "name": "fv2",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/11b293df-e9d7-46cc-a9ce-2df8e52ef811"
                    }
                },
            },
        }
    ),
    TopMetricsSvmDirectory(
        {
            "path": "73b293df-e9d7-46cc-a9ce-2df8e52ef864.7844",
            "junction-path": "/fv1",
            "iops": {"read": 345, "error": {"upper_bound": 355, "lower_bound": 345}},
            "svm": {"name": "vs1"},
            "volume": {
                "uuid": "73b293df-e9d7-46cc-a9ce-2df8e52ef864",
                "name": "fv1",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/73b293df-e9d7-46cc-a9ce-2df8e52ef864"
                    }
                },
            },
        }
    ),
]

```
</div>
</div>

---
### Example showing the behavior of the API where there is no read/write traffic:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import TopMetricsSvmDirectory

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            TopMetricsSvmDirectory.get_collection(
                "{svm.uuid}", top_metric="throughput.write"
            )
        )
    )

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[]

```
</div>
</div>

---"""

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


__all__ = ["TopMetricsSvmDirectory", "TopMetricsSvmDirectorySchema"]
__pdoc__ = {
    "TopMetricsSvmDirectorySchema.resource": False,
    "TopMetricsSvmDirectorySchema.opts": False,
}


class TopMetricsSvmDirectorySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the TopMetricsSvmDirectory object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.file_info_links.FileInfoLinksSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the top_metrics_svm_directory."""

    iops = marshmallow_fields.Nested("netapp_ontap.models.top_metrics_directory_iops.TopMetricsDirectoryIopsSchema", data_key="iops", unknown=EXCLUDE, allow_none=True)
    r""" The iops field of the top_metrics_svm_directory."""

    junction_path = marshmallow_fields.Str(
        data_key="junction-path",
        allow_none=True,
    )
    r""" Junction path of the file.

Example: /fv"""

    path = marshmallow_fields.Str(
        data_key="path",
        allow_none=True,
    )
    r""" Path of the directory.

Example: /vol/fv/dir_abc/dir_123/dir_20"""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the top_metrics_svm_directory."""

    throughput = marshmallow_fields.Nested("netapp_ontap.models.top_metrics_directory_throughput.TopMetricsDirectoryThroughputSchema", data_key="throughput", unknown=EXCLUDE, allow_none=True)
    r""" The throughput field of the top_metrics_svm_directory."""

    volume = marshmallow_fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE, allow_none=True)
    r""" The volume field of the top_metrics_svm_directory."""

    @property
    def resource(self):
        return TopMetricsSvmDirectory

    gettable_fields = [
        "links",
        "iops",
        "junction_path",
        "path",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "throughput",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,iops,junction_path,path,svm.links,svm.name,svm.uuid,throughput,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "iops",
        "throughput",
    ]
    """iops,throughput,"""

    postable_fields = [
        "iops",
        "throughput",
    ]
    """iops,throughput,"""

class TopMetricsSvmDirectory(Resource):
    r""" Information about a directory's IO activity. """

    _schema = TopMetricsSvmDirectorySchema
    _path = "/api/svm/svms/{svm[uuid]}/top-metrics/directories"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of directories with the most I/O activity.
### Learn more
* [`DOC /svm/svms/{svm.uuid}/top-metrics/directories`](#docs-svm-svm_svms_{svm.uuid}_top-metrics_directories)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all TopMetricsSvmDirectory resources that match the provided query"""
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
        """Returns a list of RawResources that represent TopMetricsSvmDirectory resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of directories with the most I/O activity.
### Learn more
* [`DOC /svm/svms/{svm.uuid}/top-metrics/directories`](#docs-svm-svm_svms_{svm.uuid}_top-metrics_directories)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






