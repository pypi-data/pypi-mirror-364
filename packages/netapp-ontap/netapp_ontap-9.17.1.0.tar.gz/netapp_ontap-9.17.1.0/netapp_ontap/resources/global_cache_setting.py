r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
This API is used to retrieve and manage global nameservice cache settings.
## Examples
### Retrieving a global nameservice cache setting
---
The following example shows how to use the cache setting GET endpoint to retrieve the global nameservice cache setting.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GlobalCacheSetting

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GlobalCacheSetting()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
GlobalCacheSetting({"remote_fetch_enabled": True, "eviction_time_interval": "P2D"})

```
</div>
</div>

---
### Updating a global nameservice cache setting
---
The following example shows how to use the cache setting PATCH endpoint to update the global nameservice cache setting.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GlobalCacheSetting

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GlobalCacheSetting()
    resource.eviction_time_interval = "PT2H"
    resource.patch()

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


__all__ = ["GlobalCacheSetting", "GlobalCacheSettingSchema"]
__pdoc__ = {
    "GlobalCacheSettingSchema.resource": False,
    "GlobalCacheSettingSchema.opts": False,
}


class GlobalCacheSettingSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the GlobalCacheSetting object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the global_cache_setting."""

    eviction_time_interval = marshmallow_fields.Str(
        data_key="eviction_time_interval",
        allow_none=True,
    )
    r""" Specifies the time interval, in ISO 8601 format after which a periodic cache eviction happens. Default is 4 hours.


Example: PT2H"""

    remote_fetch_enabled = marshmallow_fields.Boolean(
        data_key="remote_fetch_enabled",
        allow_none=True,
    )
    r""" Indicates whether or not a node is allowed to fetch the data from a remote node."""

    @property
    def resource(self):
        return GlobalCacheSetting

    gettable_fields = [
        "links",
        "eviction_time_interval",
        "remote_fetch_enabled",
    ]
    """links,eviction_time_interval,remote_fetch_enabled,"""

    patchable_fields = [
        "eviction_time_interval",
        "remote_fetch_enabled",
    ]
    """eviction_time_interval,remote_fetch_enabled,"""

    postable_fields = [
        "eviction_time_interval",
        "remote_fetch_enabled",
    ]
    """eviction_time_interval,remote_fetch_enabled,"""

class GlobalCacheSetting(Resource):
    """Allows interaction with GlobalCacheSetting objects on the host"""

    _schema = GlobalCacheSettingSchema
    _path = "/api/name-services/cache/setting"






    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a global nameservice cache setting.
### Related ONTAP commands
* `vserver services name-service cache settings show`
### Learn more
* [`DOC /name-services/cache/setting`](#docs-name-services-name-services_cache_setting)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a global nameservice cache setting.
### Important notes
  - Both the cache eviction time and remote fetch option can be modified.
### Related ONTAP commands
* `vserver services name-service cache settings modify`
### Learn more
* [`DOC /name-services/cache/setting`](#docs-name-services-name-services_cache_setting)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)



