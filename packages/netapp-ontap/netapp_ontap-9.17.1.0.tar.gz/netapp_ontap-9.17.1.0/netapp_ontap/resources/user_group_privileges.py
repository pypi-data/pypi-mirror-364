r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
Privileges associated with local or Active Directory users or groups defines the permissions for the specified user or group. You can use this API to display and/or control privileges of local or Active Directory users or groups.
## Retrieving the privileges of a specific local or Active Directory user or group and an SVM
The users and groups privileges GET endpoint retrieves privileges of the specified local or Active Directory user or group and the SVM.
## Examples
### Retrieving the privileges of all of the users or groups of data SVMs.
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(UserGroupPrivileges.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    UserGroupPrivileges(
        {
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "privileges": ["sechangenotifyprivilege", "setakeownershipprivilege"],
            "name": "VS1.CIFS\\user1",
        }
    ),
    UserGroupPrivileges(
        {
            "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
            "privileges": ["sebackupprivilege", "setakeownershipprivilege"],
            "name": "ACTIVE_DIRECTORY\\user",
        }
    ),
    UserGroupPrivileges(
        {
            "svm": {"uuid": "0ac79c37-3867-11eb-bece-0050568ed0a2", "name": "vs2"},
            "privileges": [
                "sesecurityprivilege",
                "sebackupprivilege",
                "serestoreprivilege",
            ],
            "name": "VS2.CIFS\\group1",
        }
    ),
]

```
</div>
</div>

### Retrieving the privileges of the specific SVM and user or group
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "25b363a6-2971-11eb-88e1-0050568eefd4"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
UserGroupPrivileges(
    {
        "svm": {"uuid": "25b363a6-2971-11eb-88e1-0050568eefd4", "name": "vs1"},
        "privileges": ["sechangenotifyprivilege", "setakeownershipprivilege"],
        "name": "VS1.CIFS\\user1",
    }
)

```
</div>
</div>

## Adding privileges to the local or Active Directory user or group
The users and groups privileges POST endpoint adds privileges to the specified local or Active Directory user or group and the SVM.
### Adding the privileges to the local user 'user1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges()
    resource.privileges = [
        "SeSecurityPrivilege",
        "SeBackupPrivilege",
        "SeRestorePrivilege",
    ]
    resource.post(hydrate=True)
    print(resource)

```

## Updating the privileges of the local or Active Directory user or group of a specific SVM
## Example
### Updating the privileges of local user 'user1' in SVM 'vs1' to 'SeRestorePrivilege' and 'SeSecurityPrivilege'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.privileges = ["SeRestorePrivilege", "SeSecurityPrivilege"]
    resource.patch()

```

### Reset all the privileges associated with the local user 'user1' in SVM 'vs1'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import UserGroupPrivileges

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = UserGroupPrivileges(
        name="user1", **{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    )
    resource.privileges = []
    resource.patch()

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


__all__ = ["UserGroupPrivileges", "UserGroupPrivilegesSchema"]
__pdoc__ = {
    "UserGroupPrivilegesSchema.resource": False,
    "UserGroupPrivilegesSchema.opts": False,
}


class UserGroupPrivilegesSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the UserGroupPrivileges object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the user_group_privileges."""

    name = marshmallow_fields.Str(
        data_key="name",
        allow_none=True,
    )
    r""" Local or Active Directory user or group name.


Example: user1"""

    privileges = marshmallow_fields.List(marshmallow_fields.Str, data_key="privileges", allow_none=True)
    r""" An array of privileges associated with the local or Active Directory user or group.
The available values are:

* SeTcbPrivilege              - Allows user to act as part of the operating system
* SeBackupPrivilege           - Allows user to back up files and directories, overriding any ACLs
* SeRestorePrivilege          - Allows user to restore files and directories, overriding any ACLs
* SeTakeOwnershipPrivilege    - Allows user to take ownership of files or other objects
* SeSecurityPrivilege         - Allows user to manage auditing and viewing/dumping/clearing the security log
* SeChangeNotifyPrivilege     - Allows user to bypass traverse checking"""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the user_group_privileges."""

    @property
    def resource(self):
        return UserGroupPrivileges

    gettable_fields = [
        "links",
        "name",
        "privileges",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,name,privileges,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "privileges",
    ]
    """privileges,"""

    postable_fields = [
        "name",
        "privileges",
        "svm.name",
        "svm.uuid",
    ]
    """name,privileges,svm.name,svm.uuid,"""

class UserGroupPrivileges(Resource):
    """Allows interaction with UserGroupPrivileges objects on the host"""

    _schema = UserGroupPrivilegesSchema
    _path = "/api/protocols/cifs/users-and-groups/privileges"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
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
        """Returns a count of all UserGroupPrivileges resources that match the provided query"""
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
        """Returns a list of RawResources that represent UserGroupPrivileges resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["UserGroupPrivileges"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates privileges of the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges will replace all the existing privileges associated with the user or group.
* To reset privileges associated with the user or group, specify the privileges list as empty.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege reset-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["UserGroupPrivileges"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["UserGroupPrivileges"], NetAppResponse]:
        r"""Adds privileges to the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges are appended to the existing list of privileges.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which privileges are added to user or group.
* `name` - Existing local or Active Directory user or group for which privileges are to be added.
* `privileges` - List of privileges to be added to a user or group.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege add-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)


    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves privileges of the specified local or Active Directory user or group and SVM.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege show`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
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
        r"""Adds privileges to the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges are appended to the existing list of privileges.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which privileges are added to user or group.
* `name` - Existing local or Active Directory user or group for which privileges are to be added.
* `privileges` - List of privileges to be added to a user or group.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege add-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
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
        r"""Updates privileges of the specified local or Active Directory user or group and SVM.
### Important note
* Specified privileges will replace all the existing privileges associated with the user or group.
* To reset privileges associated with the user or group, specify the privileges list as empty.
### Related ONTAP commands
* `vserver cifs users-and-groups privilege reset-privilege`
### Learn more
* [`DOC /protocols/cifs/users-and-groups/privileges`](#docs-NAS-protocols_cifs_users-and-groups_privileges)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)



