r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
Displays the netgroup file details or raw netgroup file of an SVM.
Note: The GET collection endpoint is not supported for netgroup files.
## Examples
###  Retrieving the netgroup file status of a given SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NetgroupFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NetgroupFile(**{"svm.uuid": "53942195-1709-11ec-b0d4-0050568efd14"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
NetgroupFile(
    {
        "timestamp": "2021-10-04T13:05:06+05:30",
        "file_size": 5118686,
        "hash_value_by_host": "eb109a44056a47bdeb4b407ec821a14b",
        "hash_value": "729b6e43cee04bcee18efa3aa689881d",
        "svm": {"uuid": "53942195-1709-11ec-b0d4-0050568efd14", "name": "svm1"},
    }
)

```
</div>
</div>

---
### Retrieving the raw netgroup file of a given SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NetgroupFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NetgroupFile(**{"svm.uuid": "53942195-1709-11ec-b0d4-0050568efd14"})
    resource.get()
    print(resource)

```

---
### Deleting a netgroup file of a given SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NetgroupFile

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NetgroupFile(**{"svm.uuid": "53942195-1709-11ec-b0d4-0050568efd14"})
    resource.delete()

```

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


__all__ = ["NetgroupFile", "NetgroupFileSchema"]
__pdoc__ = {
    "NetgroupFileSchema.resource": False,
    "NetgroupFileSchema.opts": False,
}


class NetgroupFileSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NetgroupFile object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the netgroup_file."""

    file_size = Size(
        data_key="file_size",
        allow_none=True,
    )
    r""" File size of the netgroup definitions file in bytes.

Example: 5118686"""

    hash_value = marshmallow_fields.Str(
        data_key="hash_value",
        allow_none=True,
    )
    r""" Hash value of the netgroup definitions.

Example: e53ec87782356bd6786f146ce0a48449"""

    hash_value_by_host = marshmallow_fields.Str(
        data_key="hash_value_by_host",
        allow_none=True,
    )
    r""" Hash value of the netgroup-by-host database.

Example: e012b7f62e4810936725ed1239018314"""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the netgroup_file."""

    timestamp = ImpreciseDateTime(
        data_key="timestamp",
        allow_none=True,
    )
    r""" Load time for netgroup definitions."""

    @property
    def resource(self):
        return NetgroupFile

    gettable_fields = [
        "links",
        "file_size",
        "hash_value",
        "hash_value_by_host",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "timestamp",
    ]
    """links,file_size,hash_value,hash_value_by_host,svm.links,svm.name,svm.uuid,timestamp,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

class NetgroupFile(Resource):
    """Allows interaction with NetgroupFile objects on the host"""

    _schema = NetgroupFileSchema
    _path = "/api/name-services/netgroup-files"
    _keys = ["svm.uuid"]




    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["NetgroupFile"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the netgroup file for a given SVM.
### Related ONTAP commands
* `vserver services name-service netgroup file delete`
### Learn more
* [`DOC /name-services/netgroup-files/{svm.uuid}`](#docs-name-services-name-services_netgroup-files_{svm.uuid})
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)


    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the netgroup file details for a given SVM if the header is set as "accept: application/json".
If the header is set as "accept: multipart/form-data", the raw netgroup file of the given SVM is retrieved.
### Important notes
* For a raw netgroup file, set the header as "accept: multipart/form-data" else "accept: application/json" for netgroup file details.
* Maximum size supported for raw netgroup file is 5MB, but netgroup file details of any valid SVM can be retrieved if present.
### Related ONTAP commands
* `vserver services name-service netgroup status`
* `vserver services name-service netgroup file show`
### Learn more
* [`DOC /name-services/netgroup-files/{svm.uuid}`](#docs-name-services-name-services_netgroup-files_{svm.uuid})
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)



    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the netgroup file for a given SVM.
### Related ONTAP commands
* `vserver services name-service netgroup file delete`
### Learn more
* [`DOC /name-services/netgroup-files/{svm.uuid}`](#docs-name-services-name-services_netgroup-files_{svm.uuid})
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


