r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
An NVMe subsystem maintains configuration state and namespace access control for a set of NVMe-connected hosts.<br/>
The NVMe subsystem REST API allows you to create, update, delete, and discover NVMe subsystems as well as add and remove NVMe hosts that can access the subsystem and associated namespaces.
## Examples
### Creating an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem()
    resource.svm = {"name": "svm1"}
    resource.name = "subsystem1"
    resource.os_type = "linux"
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating an NVMe subsystem with multiple NVMe subsystem hosts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem()
    resource.svm = {"name": "svm1"}
    resource.name = "subsystem2"
    resource.os_type = "vmware"
    resource.hosts = [
        {"nqn": "nqn.1992-01.example.com:host1"},
        {"nqn": "nqn.1992-01.example.com:host2"},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all NVMe subsystems
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeSubsystem.get_collection()))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    NvmeSubsystem(
        {
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem1",
        }
    ),
    NvmeSubsystem(
        {
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "bcde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem2",
        }
    ),
]

```
</div>
</div>

---
### Retrieving all NVMe subsystems with OS type _linux_
Note that the `os_type` query parameter is used to perform the query.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NvmeSubsystem.get_collection(os_type="linux")))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    NvmeSubsystem(
        {
            "os_type": "linux",
            "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
            "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
            "name": "subsystem1",
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
NvmeSubsystem(
    {
        "serial_number": "wtJNKNKD-uPLAAAAAAAD",
        "os_type": "linux",
        "io_queue": {"default": {"depth": 32, "count": 4}},
        "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
        "target_nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.subsystem1",
        "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
        "name": "subsystem1",
    }
)

```
</div>
</div>

---
### Retrieving the NVMe namespaces mapped to a specific NVMe subsystem
Note that the `fields` query parameter is used to specify the desired properties.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.get(fields="subsystem_maps")
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
NvmeSubsystem(
    {
        "svm": {"uuid": "a009a9e7-4081-b576-7575-ada21efcaf16", "name": "svm1"},
        "subsystem_maps": [
            {
                "anagrpid": "00000001h",
                "nsid": "00000001h",
                "namespace": {
                    "uuid": "eeaaca23-128d-4a7d-be4a-dc9106705799",
                    "name": "/vol/vol1/namespace1",
                },
            },
            {
                "anagrpid": "00000002h",
                "nsid": "00000002h",
                "namespace": {
                    "uuid": "feaaca23-83a0-4a7d-beda-dc9106705799",
                    "name": "/vol/vol1/namespace2",
                },
            },
        ],
        "uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f",
        "name": "subsystem1",
    }
)

```
</div>
</div>

---
### Adding a comment about an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.comment = "A brief comment about the subsystem"
    resource.patch()

```

---
### Deleting an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete()

```

### Deleting an NVMe subsystem with mapped NVMe namespaces
Normally, deleting an NVMe subsystem that has mapped NVMe namespaces is not allowed. The deletion can be forced using the `allow_delete_while_mapped` query parameter.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete(allow_delete_while_mapped=True)

```

### Delete an NVMe subsystem with NVMe subsystem hosts
Normally, deleting an NVMe subsystem with NVMe subsystem hosts is disallowed. The deletion can be forced using the `allow_delete_with_hosts` query parameter.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystem

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystem(uuid="acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.delete(allow_delete_with_hosts=True)

```

---
## An NVMe Subsystem Host
An NVMe subsystem host is a network host provisioned to an NVMe subsystem to access namespaces mapped to that subsystem.
## Examples
### Adding an NVMe subsystem host to an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost("acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.nqn = "nqn.1992-01.com.example:subsys1.host1"
    resource.post(hydrate=True)
    print(resource)

```

---
### Adding multiple NVMe subsystem hosts to an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost("acde901a-a379-4a91-9ea6-1b728ed6696f")
    resource.records = [
        {"nqn": "nqn.1992-01.com.example:subsys1.host2"},
        {"nqn": "nqn.1992-01.com.example:subsys1.host3"},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all NVMe subsystem hosts for an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(NvmeSubsystemHost.get_collection("acde901a-a379-4a91-9ea6-1b728ed6696f"))
    )

```
<div class="try_it_out">
<input id="example12_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example12_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example12_result" class="try_it_out_content">
```
[
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host1"}),
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host2"}),
    NvmeSubsystemHost({"nqn": "nqn.1992-01.com.example:subsys1.host3"}),
]

```
</div>
</div>

---
### Retrieving a specific NVMe subsystem host for an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost(
        "acde901a-a379-4a91-9ea6-1b728ed6696f",
        nqn="nqn.1992-01.com.example:subsys1.host1",
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example13_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example13_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example13_result" class="try_it_out_content">
```
NvmeSubsystemHost(
    {
        "priority": "regular",
        "dh_hmac_chap": {},
        "subsystem": {"uuid": "acde901a-a379-4a91-9ea6-1b728ed6696f"},
        "nqn": "nqn.1992-01.com.example:subsys1.host1",
    }
)

```
</div>
</div>

---
### Deleting an NVMe subsystem host from an NVMe subsystem
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NvmeSubsystemHost

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NvmeSubsystemHost(
        "acde901a-a379-4a91-9ea6-1b728ed6696f",
        nqn="nqn.1992-01.com.example:subsys1.host1",
    )
    resource.delete()

```
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


__all__ = ["NvmeSubsystem", "NvmeSubsystemSchema"]
__pdoc__ = {
    "NvmeSubsystemSchema.resource": False,
    "NvmeSubsystemSchema.opts": False,
}


class NvmeSubsystemSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NvmeSubsystem object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the nvme_subsystem."""

    comment = marshmallow_fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=255),
        allow_none=True,
    )
    r""" A configurable comment for the NVMe subsystem. Optional in POST and PATCH."""

    delete_on_unmap = marshmallow_fields.Boolean(
        data_key="delete_on_unmap",
        allow_none=True,
    )
    r""" An option that causes the subsystem to be deleted when the last subsystem map associated with it is deleted. Optional in POST and PATCH. This property defaults to _false_ when the subsystem is created."""

    hosts = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.nvme_subsystem_hosts.NvmeSubsystemHostsSchema", unknown=EXCLUDE, allow_none=True), data_key="hosts", allow_none=True)
    r""" The NVMe hosts configured for access to the NVMe subsystem. Optional in POST."""

    io_queue = marshmallow_fields.Nested("netapp_ontap.models.nvme_subsystem_io_queue.NvmeSubsystemIoQueueSchema", data_key="io_queue", unknown=EXCLUDE, allow_none=True)
    r""" The properties of the submission queue used to submit I/O commands for execution by the NVMe controller."""

    name = marshmallow_fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=64),
        allow_none=True,
    )
    r""" The name of the NVMe subsystem. Once created, an NVMe subsystem cannot be renamed. Required in POST.


Example: subsystem1"""

    os_type = marshmallow_fields.Str(
        data_key="os_type",
        validate=enum_validation(['aix', 'linux', 'vmware', 'windows']),
        allow_none=True,
    )
    r""" The host operating system of the NVMe subsystem's hosts. Required in POST.


Valid choices:

* aix
* linux
* vmware
* windows"""

    replication = marshmallow_fields.Nested("netapp_ontap.models.nvme_subsystem_replication.NvmeSubsystemReplicationSchema", data_key="replication", unknown=EXCLUDE, allow_none=True)
    r""" Properties related to subsystem replication."""

    serial_number = marshmallow_fields.Str(
        data_key="serial_number",
        validate=len_validation(minimum=20, maximum=20),
        allow_none=True,
    )
    r""" The serial number of the NVMe subsystem.


Example: wCVsgFMiuMhVAAAAAAAB"""

    subsystem_maps = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.nvme_subsystem_subsystem_maps.NvmeSubsystemSubsystemMapsSchema", unknown=EXCLUDE, allow_none=True), data_key="subsystem_maps", allow_none=True)
    r""" The NVMe namespaces mapped to the NVMe subsystem.<br/>
There is an added computational cost to retrieving property values for `subsystem_maps`. They are not populated for a GET request unless explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more."""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the nvme_subsystem."""

    target_nqn = marshmallow_fields.Str(
        data_key="target_nqn",
        validate=len_validation(minimum=1, maximum=223),
        allow_none=True,
    )
    r""" The NVMe qualified name (NQN) used to identify the NVMe storage target.


Example: nqn.1992-01.example.com:string"""

    uuid = marshmallow_fields.Str(
        data_key="uuid",
        allow_none=True,
    )
    r""" The unique identifier of the NVMe subsystem.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412"""

    vendor_uuids = marshmallow_fields.List(marshmallow_fields.Str, data_key="vendor_uuids", allow_none=True)
    r""" Vendor-specific identifiers (UUIDs) optionally assigned to an NVMe subsystem when the subsystem is created. The identifiers are used to enable vendor-specific NVMe protocol features. The identifiers are provided by a host application vendor and shared with NetApp prior to a joint product release. Creating an NVMe subsystem with an unknown or non-specific identifier will have no effect on the NVMe subsystem. Refer to the ONTAP SAN Administration Guide for a list of the supported vendor-specific identifiers. After a subsystem is created, the vendor-specific identifiers cannot be changed or removed. Optional in POST."""

    @property
    def resource(self):
        return NvmeSubsystem

    gettable_fields = [
        "links",
        "comment",
        "delete_on_unmap",
        "hosts",
        "io_queue",
        "name",
        "os_type",
        "replication",
        "serial_number",
        "subsystem_maps",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "target_nqn",
        "uuid",
        "vendor_uuids",
    ]
    """links,comment,delete_on_unmap,hosts,io_queue,name,os_type,replication,serial_number,subsystem_maps,svm.links,svm.name,svm.uuid,target_nqn,uuid,vendor_uuids,"""

    patchable_fields = [
        "comment",
        "delete_on_unmap",
        "replication",
    ]
    """comment,delete_on_unmap,replication,"""

    postable_fields = [
        "comment",
        "delete_on_unmap",
        "hosts",
        "name",
        "os_type",
        "replication",
        "svm.name",
        "svm.uuid",
        "vendor_uuids",
    ]
    """comment,delete_on_unmap,hosts,name,os_type,replication,svm.name,svm.uuid,vendor_uuids,"""

class NvmeSubsystem(Resource):
    r""" An NVMe subsystem maintains configuration state and namespace access control for a set of NVMe-connected hosts. """

    _schema = NvmeSubsystemSchema
    _path = "/api/protocols/nvme/subsystems"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves NVMe subsystems.
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NvmeSubsystem resources that match the provided query"""
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
        """Returns a list of RawResources that represent NvmeSubsystem resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NvmeSubsystem"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem modify`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NvmeSubsystem"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NvmeSubsystem"], NetAppResponse]:
        r"""Creates an NVMe subsystem.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem.
* `name` - Name for NVMe subsystem. Once created, an NVMe subsystem cannot be renamed.
* `os_type` - Operating system of the NVMe subsystem's hosts.
### Related ONTAP commands
* `vserver nvme subsystem create`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["NvmeSubsystem"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem delete`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves NVMe subsystems.
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an NVMe subsystem.
### Expensive properties
There is an added computational cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `subsystem_maps.*`
### Related ONTAP commands
* `vserver nvme subsystem host show`
* `vserver nvme subsystem map show`
* `vserver nvme subsystem show`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates an NVMe subsystem.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the NVMe subsystem.
* `name` - Name for NVMe subsystem. Once created, an NVMe subsystem cannot be renamed.
* `os_type` - Operating system of the NVMe subsystem's hosts.
### Related ONTAP commands
* `vserver nvme subsystem create`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem modify`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes an NVMe subsystem.
### Related ONTAP commands
* `vserver nvme subsystem delete`
### Learn more
* [`DOC /protocols/nvme/subsystems`](#docs-NVMe-protocols_nvme_subsystems)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


