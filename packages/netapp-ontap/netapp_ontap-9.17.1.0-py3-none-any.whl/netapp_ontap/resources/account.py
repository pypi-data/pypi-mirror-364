r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
This API displays and manages the configuration of scoped user accounts.<p/>
Newly created user accounts might need to be updated for many reasons. For example, a user account might need to use a different application or its role might need to be modified. According to a policy, the password or authentication source of a user account might need to be changed, or a user account might need to be locked or deleted from the system. This API allows you to make these changes to user accounts.<p/>
Specify the owner UUID and the user account name in the URI path. The owner UUID corresponds to the UUID of the SVM for which the user account has been created and can be obtained from the response body of the GET request performed on one of the following APIs:
<i>/api/security/accounts</i> for all user accounts
<i>/api/security/accounts/?scope=cluster</i> for cluster-scoped user accounts
<i>/api/security/accounts/?scope=svm</i> for SVM-scoped accounts
<i>/api/security/accounts/?owner.name=<svm-name></i> for a specific SVM
This API response contains the complete URI for each user account that can be used.
## Examples
### Retrieving the user account details
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Account(
    {
        "scope": "svm",
        "applications": [
            {
                "second_authentication_method": "none",
                "application": "ssh",
                "authentication_methods": ["password"],
            }
        ],
        "password_hash_algorithm": "sha512",
        "owner": {
            "uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25",
            "name": "svm1",
            "_links": {
                "self": {"href": "/api/svm/svms/aaef7c38-4bd3-11e9-b238-0050568e2e25"}
            },
        },
        "locked": False,
        "role": {
            "_links": {
                "self": {
                    "href": "/api/svms/aaef7c38-4bd3-11e9-b238-0050568e2e25/admin/roles/vsadmin"
                }
            },
            "name": "vsadmin",
        },
        "_links": {
            "self": {
                "href": "/api/security/accounts/aaef7c38-4bd3-11e9-b238-0050568e2e25/svm_user1"
            }
        },
        "name": "svm_user1",
    }
)

```
</div>
</div>

### Updating the applications and role in a user account
Specify the desired configuration in the form of tuples (of applications and authentication methods) and the role. All other previously configured applications that are not specified in the "applications" parameter of the PATCH request will be de-provisioned for the user account.<p/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.applications = [
        {"application": "http", "authentication_methods": ["domain"]},
        {"application": "ontapi", "authentication_methods": ["password"]},
    ]
    resource.role = {"name": "vsadmin-backup"}
    resource.patch()

```

### Updating the password for a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.password = "newp@ssw@rd2"
    resource.patch()

```

### Locking a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
    )
    resource.locked = True
    resource.patch()

```

### Deleting a user account
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Account

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Account(
        name="svm_user1", **{"owner.uuid": "aaef7c38-4bd3-11e9-b238-0050568e2e25"}
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


__all__ = ["Account", "AccountSchema"]
__pdoc__ = {
    "AccountSchema.resource": False,
    "AccountSchema.opts": False,
}


class AccountSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Account object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the account."""

    applications = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.account_application.AccountApplicationSchema", unknown=EXCLUDE, allow_none=True), data_key="applications", allow_none=True)
    r""" The applications field of the account."""

    comment = marshmallow_fields.Str(
        data_key="comment",
        allow_none=True,
    )
    r""" Optional comment for the user account."""

    locked = marshmallow_fields.Boolean(
        data_key="locked",
        allow_none=True,
    )
    r""" Locked status of the account."""

    name = marshmallow_fields.Str(
        data_key="name",
        validate=len_validation(minimum=3, maximum=64),
        allow_none=True,
    )
    r""" User or group account name

Example: joe.smith"""

    owner = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="owner", unknown=EXCLUDE, allow_none=True)
    r""" The owner field of the account."""

    password = marshmallow_fields.Str(
        data_key="password",
        validate=len_validation(minimum=8, maximum=128),
        allow_none=True,
    )
    r""" Password for the account. The password can contain a mix of lower and upper case alphabetic characters, digits, and special characters."""

    password_hash_algorithm = marshmallow_fields.Str(
        data_key="password_hash_algorithm",
        validate=enum_validation(['sha512', 'sha256', 'md5']),
        allow_none=True,
    )
    r""" Password hash algorithm used to generate a hash of the user's password for password matching.To modify "password_hash_algorithm", use REST API "/api/security/authentication/password".

Valid choices:

* sha512
* sha256
* md5"""

    role = marshmallow_fields.Nested("netapp_ontap.resources.role.RoleSchema", data_key="role", unknown=EXCLUDE, allow_none=True)
    r""" The role field of the account."""

    scope = marshmallow_fields.Str(
        data_key="scope",
        validate=enum_validation(['cluster', 'svm']),
        allow_none=True,
    )
    r""" Scope of the entity. Set to "cluster" for cluster owned objects and to "svm" for SVM owned objects.

Valid choices:

* cluster
* svm"""

    @property
    def resource(self):
        return Account

    gettable_fields = [
        "links",
        "applications",
        "comment",
        "locked",
        "name",
        "owner.links",
        "owner.name",
        "owner.uuid",
        "password_hash_algorithm",
        "role.links",
        "role.name",
        "scope",
    ]
    """links,applications,comment,locked,name,owner.links,owner.name,owner.uuid,password_hash_algorithm,role.links,role.name,scope,"""

    patchable_fields = [
        "applications",
        "comment",
        "locked",
        "password",
        "role.name",
    ]
    """applications,comment,locked,password,role.name,"""

    postable_fields = [
        "applications",
        "comment",
        "locked",
        "name",
        "owner.name",
        "owner.uuid",
        "password",
        "role.name",
    ]
    """applications,comment,locked,name,owner.name,owner.uuid,password,role.name,"""

class Account(Resource):
    """Allows interaction with Account objects on the host"""

    _schema = AccountSchema
    _path = "/api/security/accounts"
    _keys = ["owner.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of user accounts in the cluster.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        """Returns a count of all Account resources that match the provided query"""
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
        """Returns a list of RawResources that represent Account resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Account"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a user account. Locks or unlocks a user account and/or updates the role, applications, and/or password for the user account.
### Required parameters
* `name` - Account name to be updated.
* `owner.uuid`  - UUID of the SVM housing the user account to be updated.
### Optional parameters
* `applications` - Array of one or more tuples (of application and authentication methods).
* `role` - RBAC role for the user account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for _ssh_ and _service_processor_ applications. Defaults to _none_ if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Set to true/false to lock/unlock the account.
* `is_ldap_fastbind` - Set to true/false to enable LDAP Fastbind Authentication.
* `is_ns_switch_group` - Set to true/false to specify whether the user is an LDAP or NIS group.
### Related ONTAP commands
* `security login create`
* `security login modify`
* `security login password`
* `security login lock`
* `security login unlock`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Account"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Account"], NetAppResponse]:
        r"""Creates a new user account.
### Required parameters
* `name` - Account name to be created.
* `applications` - Array of one or more application tuples (of application and authentication methods).
### Optional parameters
* `owner.name` or `owner.uuid`  - Name or UUID of the SVM for an SVM-scoped user account. If not supplied, a cluster-scoped user account is created.
* `role` - RBAC role for the user account. Defaulted to `admin` for cluster user account and to `vsadmin` for SVM-scoped account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for _ssh_ and _service_processor_ applications. Defaults to _none_ if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Locks the account after creation. Defaults to `false` if not supplied.
* `is_ldap_fastbind` - Needed for LDAP Fastbind Authentication and only supported for applications SSH, ONTAPI, and HTTP with authentication method "nsswitch" only. Defaults to false if not supplied.
* `is_ns_switch_group` - Specifies whether the user is an LDAP or NIS group and is only supported for SSH, ONTAPI, and HTTP applications with the authentication method "nsswitch". Defaults to false if not supplied.
### Related ONTAP commands
* `security login create`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        records: Iterable["Account"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a user account.
### Required parameters
* `name` - Account name to be deleted.
* `owner.uuid`  - UUID of the SVM housing the user account to be deleted.
### Related ONTAP commands
* `security login delete`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of user accounts in the cluster.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific user account.
### Related ONTAP commands
* `security login show`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        r"""Creates a new user account.
### Required parameters
* `name` - Account name to be created.
* `applications` - Array of one or more application tuples (of application and authentication methods).
### Optional parameters
* `owner.name` or `owner.uuid`  - Name or UUID of the SVM for an SVM-scoped user account. If not supplied, a cluster-scoped user account is created.
* `role` - RBAC role for the user account. Defaulted to `admin` for cluster user account and to `vsadmin` for SVM-scoped account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for _ssh_ and _service_processor_ applications. Defaults to _none_ if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Locks the account after creation. Defaults to `false` if not supplied.
* `is_ldap_fastbind` - Needed for LDAP Fastbind Authentication and only supported for applications SSH, ONTAPI, and HTTP with authentication method "nsswitch" only. Defaults to false if not supplied.
* `is_ns_switch_group` - Specifies whether the user is an LDAP or NIS group and is only supported for SSH, ONTAPI, and HTTP applications with the authentication method "nsswitch". Defaults to false if not supplied.
### Related ONTAP commands
* `security login create`
### Learn more
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        r"""Updates a user account. Locks or unlocks a user account and/or updates the role, applications, and/or password for the user account.
### Required parameters
* `name` - Account name to be updated.
* `owner.uuid`  - UUID of the SVM housing the user account to be updated.
### Optional parameters
* `applications` - Array of one or more tuples (of application and authentication methods).
* `role` - RBAC role for the user account.
* `password` - Password for the user account (if the authentication method is opted as password for one or more of applications).
* `second_authentication_method` - Needed for MFA and only supported for _ssh_ and _service_processor_ applications. Defaults to _none_ if not supplied.
* `comment` - Comment for the user account (e.g purpose of this account).
* `locked` - Set to true/false to lock/unlock the account.
* `is_ldap_fastbind` - Set to true/false to enable LDAP Fastbind Authentication.
* `is_ns_switch_group` - Set to true/false to specify whether the user is an LDAP or NIS group.
### Related ONTAP commands
* `security login create`
* `security login modify`
* `security login password`
* `security login lock`
* `security login unlock`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
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
        r"""Deletes a user account.
### Required parameters
* `name` - Account name to be deleted.
* `owner.uuid`  - UUID of the SVM housing the user account to be deleted.
### Related ONTAP commands
* `security login delete`
### Learn more
* [`DOC /security/accounts/{owner.uuid}/{name}`](#docs-security-security_accounts_{owner.uuid}_{name})
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


