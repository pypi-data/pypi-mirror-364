r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
The core dump GET API retrieves all of the core dumps on the cluster or a node.  The core dump DELETE API deletes a specified core dump.
Some fields are only populated for core dump type "kernel".  Refer to the model for further information.  Fields will not be displayed if they are not populated.
A core can be deleted even if the core is in the process of being saved.
## Examples
### 1) Retrieving a list of core dumps from the cluster
The following example returns a list of core dumps on the cluster:
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Coredump

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Coredump.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    Coredump(
        {
            "type": "kernel",
            "node": {
                "uuid": "227683c1-e9c7-11eb-b995-005056bbbfb3",
                "name": "node2",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/227683c1-e9c7-11eb-b995-005056bbbfb3"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/support/coredump/coredumps/227683c1-e9c7-11eb-b995-005056bbbfb3/core.4136886422.2021-07-21.20_20_53.nz"
                }
            },
            "name": "core.4136886422.2021-07-21.20_20_53.nz",
        }
    ),
    Coredump(
        {
            "type": "application",
            "node": {
                "uuid": "227683c1-e9c7-11eb-b995-005056bbbfb3",
                "name": "node2",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/227683c1-e9c7-11eb-b995-005056bbbfb3"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/support/coredump/coredumps/227683c1-e9c7-11eb-b995-005056bbbfb3/mlogd.968.4136886422.2021-07-22.01_10_01.ucore.bz2"
                }
            },
            "name": "mlogd.968.4136886422.2021-07-22.01_10_01.ucore.bz2",
        }
    ),
    Coredump(
        {
            "type": "kernel",
            "node": {
                "uuid": "d583d44e-e9c6-11eb-a270-005056bb47f9",
                "name": "node1",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/d583d44e-e9c6-11eb-a270-005056bb47f9"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/support/coredump/coredumps/d583d44e-e9c6-11eb-a270-005056bb47f9/core.4136886421.2021-07-21.17_57_02.nz"
                }
            },
            "name": "core.4136886421.2021-07-21.17_57_02.nz",
        }
    ),
    Coredump(
        {
            "type": "application",
            "node": {
                "uuid": "d583d44e-e9c6-11eb-a270-005056bb47f9",
                "name": "node1",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/d583d44e-e9c6-11eb-a270-005056bb47f9"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/support/coredump/coredumps/d583d44e-e9c6-11eb-a270-005056bb47f9/mlogd.979.4136886421.2021-07-22.01_11_37.ucore.bz2"
                }
            },
            "name": "mlogd.979.4136886421.2021-07-22.01_11_37.ucore.bz2",
        }
    ),
]

```
</div>
</div>

---
### 2) Retrieving a specific core dump
The following example returns the requested core dump. If there is no core dump with the requested node UUID and name, an error is returned.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Coredump

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Coredump(
        name="core.4136886421.2021-07-21.17_57_02.nz",
        **{"node.uuid": "d583d44e-e9c6-11eb-a270-005056bb47f9"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Coredump(
    {
        "is_saved": True,
        "type": "kernel",
        "size": 945111148,
        "panic_time": "2021-07-21T13:57:02-04:00",
        "node": {
            "uuid": "d583d44e-e9c6-11eb-a270-005056bb47f9",
            "name": "node1",
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/d583d44e-e9c6-11eb-a270-005056bb47f9"
                }
            },
        },
        "_links": {
            "self": {
                "href": "/api/support/coredump/coredumps/d583d44e-e9c6-11eb-a270-005056bb47f9/core.4136886421.2021-07-21.17_57_02.nz"
            }
        },
        "name": "core.4136886421.2021-07-21.17_57_02.nz",
    }
)

```
</div>
</div>

---
### 3) Deleting a core dump
The following example deletes the requested core dump. If there is no core dump with the requested node UUID and name to delete, an error is returned.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Coredump

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Coredump(
        name="mlogd.979.4136886421.2021-07-22.01_11_37.ucore.bz2",
        **{"node.uuid": "d583d44e-e9c6-11eb-a270-005056bb47f9"}
    )
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


__all__ = ["Coredump", "CoredumpSchema"]
__pdoc__ = {
    "CoredumpSchema.resource": False,
    "CoredumpSchema.opts": False,
}


class CoredumpSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Coredump object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the coredump."""

    is_partial = marshmallow_fields.Boolean(
        data_key="is_partial",
        allow_none=True,
    )
    r""" Specifies whether or not the core is a partial core.  Applicable only to kernel core dump type."""

    is_saved = marshmallow_fields.Boolean(
        data_key="is_saved",
        allow_none=True,
    )
    r""" Specifies whether or not the core file is saved."""

    md5_data_checksum = marshmallow_fields.Str(
        data_key="md5_data_checksum",
        allow_none=True,
    )
    r""" MD5 checksum of the compressed data of core.  Applicable only to kernel core dump type.

Example: 5118488cc5065e33a16986001b1ffa48"""

    name = marshmallow_fields.Str(
        data_key="name",
        allow_none=True,
    )
    r""" Core name

Example: core.4136886413.2021-03-01.22_09_11.nz"""

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE, allow_none=True)
    r""" The node field of the coredump."""

    panic_time = ImpreciseDateTime(
        data_key="panic_time",
        allow_none=True,
    )
    r""" Time of panic that generated the core.

Example: 2021-03-01T22:09:11.000+0000"""

    size = Size(
        data_key="size",
        allow_none=True,
    )
    r""" Size of core, in bytes.  Applicable only to kernel core dump type.

Example: 1161629804"""

    type = marshmallow_fields.Str(
        data_key="type",
        validate=enum_validation(['kernel', 'application', 'ancillary_kernel_segment']),
        allow_none=True,
    )
    r""" Core type, kernel or application

Valid choices:

* kernel
* application
* ancillary_kernel_segment"""

    @property
    def resource(self):
        return Coredump

    gettable_fields = [
        "links",
        "is_partial",
        "is_saved",
        "md5_data_checksum",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "panic_time",
        "size",
        "type",
    ]
    """links,is_partial,is_saved,md5_data_checksum,name,node.links,node.name,node.uuid,panic_time,size,type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

class Coredump(Resource):
    """Allows interaction with Coredump objects on the host"""

    _schema = CoredumpSchema
    _path = "/api/support/coredump/coredumps"
    _keys = ["node.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of coredumps.
### Related ONTAP commands
* `system node coredump show`

### Learn more
* [`DOC /support/coredump/coredumps`](#docs-support-support_coredump_coredumps)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Coredump resources that match the provided query"""
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
        """Returns a list of RawResources that represent Coredump resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)



    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Coredump"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a core dump.
### Related ONTAP commands
* `system node coredump delete`

### Learn more
* [`DOC /support/coredump/coredumps`](#docs-support-support_coredump_coredumps)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of coredumps.
### Related ONTAP commands
* `system node coredump show`

### Learn more
* [`DOC /support/coredump/coredumps`](#docs-support-support_coredump_coredumps)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific core dump.
### Related ONTAP commands
* `system node coredump show`

### Learn more
* [`DOC /support/coredump/coredumps`](#docs-support-support_coredump_coredumps)"""
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
        r"""Deletes a core dump.
### Related ONTAP commands
* `system node coredump delete`

### Learn more
* [`DOC /support/coredump/coredumps`](#docs-support-support_coredump_coredumps)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


