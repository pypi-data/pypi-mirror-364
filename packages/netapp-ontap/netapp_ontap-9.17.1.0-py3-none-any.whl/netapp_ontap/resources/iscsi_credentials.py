r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
An iSCSI credentials object defines authentication credentials to be used between an initiator and ONTAP. It identifies an authentication type, user names, and passwords that must be used to authenticate a specific initiator.<br/>
The iSCSI credentials REST API allows you to create, update, delete, and discover iSCSI credentials.<br/>
## How iSCSI authentication works
An iSCSI credentials object defines the authentication credentials to be used between an initiator and ONTAP. While establishing an iSCSI connection, the initiator sends a login request to ONTAP to begin an iSCSI session. ONTAP then either permits or denies the login request, or determines that a login is not required.<p/>
For an initiator, you can specify an authentication type, user names and passwords, and a whitelist of optional network addresses from which the initiator is allowed to connect.
## iSCSI authentication methods
  - Challenge-Handshake Authentication Protocol (CHAP) - The initiator logs in using a CHAP user name and password. There are two types of CHAP user names and passwords:
    - Inbound - ONTAP authenticates the initiator. Inbound settings are required if you are using CHAP authentication.
    - Outbound - These are optional credentials to enable the initiator to authenticate ONTAP. You can use credentials only if inbound credentials are also being used.
  - deny - The initiator is denied access to ONTAP.
  - none - ONTAP does not require authentication for the initiator.
The CHAP inbound/outbound password can be any valid string or an even number of valid hexadecimal digits preceded by '0X' or '0x'.
## Initiator address list
The initiator address list is a way to specify valid IP addresses from which the initiator is allowed to connect. If the list is specified and the source address of an iSCSI connection is not in the list, the connection is rejected. Initiator addresses can be specified in either IPv4 or IPv6 format and in one of two forms:
- Range
  ```
  {
    "start": "192.168.0.0",
    "end": "192.168.0.255"
  }
  ```
- Mask
  ```
  {
    "address": "192.168.0.0",
    "netmask": "24"
  }
  ```
## Initiator "default"
The default iSCSI authentication definition is created when the iSCSI service is created. An iSCSI credentials object with _default_ as the initiator name identifies the default authentication for an SVM. The default credentials are used for any initiator that does not have specific iSCSI credentials. The default iSCSI authentication method is _none_, but can be changed to _deny_ or _CHAP_. The default credentials object does not support an initiator address list.
## Examples
### Creating iSCSI credentials requiring no authentication
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials()
    resource.svm = {"name": "svm1"}
    resource.initiator = "iqn.1992-08.com.netapp:initiator1"
    resource.authentication_type = "none"
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating iSCSI credentials using CHAP inbound authentication
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials()
    resource.svm = {"name": "svm1"}
    resource.initiator = "iqn.1992-08.com.netapp:initiator2"
    resource.authentication_type = "CHAP"
    resource.chap = {"inbound": {"user": "user1", "password": "password1"}}
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all properties of all iSCSI credentials
The `fields` query parameter is used to request all iSCSI credentials properties.<br/>
Passwords are not included in the GET output.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(IscsiCredentials.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    IscsiCredentials(
        {
            "authentication_type": "none",
            "initiator": "default",
            "svm": {
                "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
                "name": "svm1",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/19d04b8e-94d7-11e8-8370-005056b48fd2/default"
                }
            },
        }
    ),
    IscsiCredentials(
        {
            "authentication_type": "none",
            "initiator": "iqn.1992-08.com.netapp:initiator1",
            "svm": {
                "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
                "name": "svm1",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/19d04b8e-94d7-11e8-8370-005056b48fd2/iqn.1992-08.com.netapp:initiator1"
                }
            },
        }
    ),
    IscsiCredentials(
        {
            "authentication_type": "chap",
            "initiator": "iqn.1992-08.com.netapp:initiator2",
            "chap": {"inbound": {"user": "user1"}},
            "svm": {
                "uuid": "19d04b8e-94d7-11e8-8370-005056b48fd2",
                "name": "svm1",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/19d04b8e-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/19d04b8e-94d7-11e8-8370-005056b48fd2/iqn.1992-08.com.netapp:initiator2"
                }
            },
        }
    ),
    IscsiCredentials(
        {
            "authentication_type": "none",
            "initiator": "default",
            "svm": {
                "uuid": "25f617cf-94d7-11e8-8370-005056b48fd2",
                "name": "svm2",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/25f617cf-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/25f617cf-94d7-11e8-8370-005056b48fd2/default"
                }
            },
        }
    ),
    IscsiCredentials(
        {
            "authentication_type": "none",
            "initiator": "iqn.1992-08.com.netapp:initiator2",
            "svm": {
                "uuid": "25f617cf-94d7-11e8-8370-005056b48fd2",
                "name": "svm2",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/25f617cf-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/25f617cf-94d7-11e8-8370-005056b48fd2/iqn.1992-08.com.netapp:initiator2"
                }
            },
        }
    ),
    IscsiCredentials(
        {
            "authentication_type": "deny",
            "initiator": "iqn.1992-08.com.netapp:initiator3",
            "svm": {
                "uuid": "25f617cf-94d7-11e8-8370-005056b48fd2",
                "name": "svm2",
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/25f617cf-94d7-11e8-8370-005056b48fd2"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/iscsi/credentials/25f617cf-94d7-11e8-8370-005056b48fd2/iqn.1992-08.com.netapp:initiator3"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving specific iSCSI credentials
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials(
        initiator="iqn.1992-08.com.netapp:initiator2",
        **{"svm.uuid": "25f617cf-94d7-11e8-8370-005056b48fd2"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
IscsiCredentials(
    {
        "authentication_type": "chap",
        "initiator": "iqn.1992-08.com.netapp:initiator2",
        "chap": {"inbound": {"user": "user1"}},
        "svm": {
            "uuid": "25f617cf-94d7-11e8-8370-005056b48fd2",
            "name": "svm2",
            "_links": {
                "self": {"href": "/api/svm/svms/25f617cf-94d7-11e8-8370-005056b48fd2"}
            },
        },
        "_links": {
            "self": {
                "href": "/api/protocols/san/iscsi/credentials/25f617cf-94d7-11e8-8370-005056b48fd2/iqn.1992-08.com.netapp:initiator2"
            }
        },
    }
)

```
</div>
</div>

---
### Updating the authentication type of iSCSI credentials
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials(
        initiator="iqn.1992-08.com.netapp:initiator2",
        **{"svm.uuid": "25f617cf-94d7-11e8-8370-005056b48fd2"}
    )
    resource.authentication_type = "chap"
    resource.chap = {"inbound": {"user": "user1", "password": "password1"}}
    resource.patch()

```

---
### Updating the initiator address list of iSCSI credentials
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials(
        initiator="iqn.1992-08.com.netapp:initiator2",
        **{"svm.uuid": "25f617cf-94d7-11e8-8370-005056b48fd2"}
    )
    resource.initiator_address = {
        "ranges": [{"start": "192.168.0.0", "end": "192.168.255.255"}]
    }
    resource.patch()

```

---
### Deleting iSCSI credentials
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import IscsiCredentials

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = IscsiCredentials(
        initiator="iqn.1992-08.com.netapp:initiator2",
        **{"svm.uuid": "25f617cf-94d7-11e8-8370-005056b48fd2"}
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


__all__ = ["IscsiCredentials", "IscsiCredentialsSchema"]
__pdoc__ = {
    "IscsiCredentialsSchema.resource": False,
    "IscsiCredentialsSchema.opts": False,
}


class IscsiCredentialsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the IscsiCredentials object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the iscsi_credentials."""

    authentication_type = marshmallow_fields.Str(
        data_key="authentication_type",
        validate=enum_validation(['chap', 'none', 'deny']),
        allow_none=True,
    )
    r""" The iSCSI authentication type. Required in POST; optional in PATCH.


Valid choices:

* chap
* none
* deny"""

    chap = marshmallow_fields.Nested("netapp_ontap.models.iscsi_credentials_chap.IscsiCredentialsChapSchema", data_key="chap", unknown=EXCLUDE, allow_none=True)
    r""" Challenge-Handshake Authentication Protocol (CHAP) credentials."""

    initiator = marshmallow_fields.Str(
        data_key="initiator",
        allow_none=True,
    )
    r""" The iSCSI initiator to which the credentials apply. Required in POST.


Example: iqn.1998-01.com.corp.iscsi:name1"""

    initiator_address = marshmallow_fields.Nested("netapp_ontap.models.iscsi_credentials_initiator_address.IscsiCredentialsInitiatorAddressSchema", data_key="initiator_address", unknown=EXCLUDE, allow_none=True)
    r""" Initiator address ranges."""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the iscsi_credentials."""

    @property
    def resource(self):
        return IscsiCredentials

    gettable_fields = [
        "links",
        "authentication_type",
        "chap",
        "initiator",
        "initiator_address",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,authentication_type,chap,initiator,initiator_address,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "authentication_type",
        "chap",
        "initiator_address",
    ]
    """authentication_type,chap,initiator_address,"""

    postable_fields = [
        "authentication_type",
        "chap",
        "initiator",
        "initiator_address",
        "svm.name",
        "svm.uuid",
    ]
    """authentication_type,chap,initiator,initiator_address,svm.name,svm.uuid,"""

class IscsiCredentials(Resource):
    """Allows interaction with IscsiCredentials objects on the host"""

    _schema = IscsiCredentialsSchema
    _path = "/api/protocols/san/iscsi/credentials"
    _keys = ["svm.uuid", "initiator"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security show`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
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
        """Returns a count of all IscsiCredentials resources that match the provided query"""
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
        """Returns a list of RawResources that represent IscsiCredentials resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["IscsiCredentials"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates specified iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security add-initiator-address-ranges`
* `vserver iscsi security default`
* `vserver iscsi security modify`
* `vserver iscsi security remove-initiator-address-ranges`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["IscsiCredentials"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["IscsiCredentials"], NetAppResponse]:
        r"""Creates iSCSI credentials.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the iSCSI credentials.
* `initiator` - Initiator for which the iSCSI credentials are to be created.
* `authentication_type` - Type of authentication to use for the credentials.
### Recommended optional properties
* `chap.inbound.user` - In-bound CHAP authentication user name.
* `chap.inbound.password` - In-bound CHAP authentication password.
* `chap.outbound.user` - Out-bound CHAP authentication user name.
* `chap.outbound.password` - Out-bound CHAP authentication password.
### Related ONTAP commands
* `vserver iscsi security create`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
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
        records: Iterable["IscsiCredentials"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes specified iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security delete`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security show`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves specified iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security show`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
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
        r"""Creates iSCSI credentials.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the iSCSI credentials.
* `initiator` - Initiator for which the iSCSI credentials are to be created.
* `authentication_type` - Type of authentication to use for the credentials.
### Recommended optional properties
* `chap.inbound.user` - In-bound CHAP authentication user name.
* `chap.inbound.password` - In-bound CHAP authentication password.
* `chap.outbound.user` - Out-bound CHAP authentication user name.
* `chap.outbound.password` - Out-bound CHAP authentication password.
### Related ONTAP commands
* `vserver iscsi security create`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
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
        r"""Updates specified iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security add-initiator-address-ranges`
* `vserver iscsi security default`
* `vserver iscsi security modify`
* `vserver iscsi security remove-initiator-address-ranges`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
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
        r"""Deletes specified iSCSI credentials.
### Related ONTAP commands
* `vserver iscsi security delete`
### Learn more
* [`DOC /protocols/san/iscsi/credentials`](#docs-SAN-protocols_san_iscsi_credentials)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


