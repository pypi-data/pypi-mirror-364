r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
Bulk import of the CIFS local users, groups and group membership information can be
done from the specified Uniform Resource Identifier (URI). This replaces the existing contents of the
CIFS local users, groups and group memberships. This API is used to bulk import from the specified URI,
get the status of the last import and to upload the import status to the specified URI.
## Retrieving import status of the last bulk import
The bulk-import GET endpoint retrieves the status of the last bulk-import operation of the specified SVM.
## Examples
### Retrieving the status of a successful bulk import
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUsersAndGroupsImport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUsersAndGroupsImport("6de1d39d-1473-11ec-b0cf-0050568e4acc")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
LocalCifsUsersAndGroupsImport(
    {
        "elements_ignored": 0,
        "detailed_status": {
            "message": "Operation completed successfully.",
            "code": "0",
        },
        "svm": {
            "uuid": "6de1d39d-1473-11ec-b0cf-0050568e4acc",
            "name": "vs1",
            "_links": {
                "self": {"href": "/api/svm/svms/6de1d39d-1473-11ec-b0cf-0050568e4acc"}
            },
        },
        "state": "success",
        "import_uri": {"path": "http://<import_uri>/file.7z"},
        "_links": {
            "self": {
                "href": "/api/protocols/cifs/users-and-groups/import/6de1d39d-1473-11ec-b0cf-0050568e4acc"
            }
        },
        "elements_imported": 2,
    }
)

```
</div>
</div>

### Retrieving the status of a bulk import that failed
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUsersAndGroupsImport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUsersAndGroupsImport("6de1d39d-1473-11ec-b0cf-0050568e4acc")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
LocalCifsUsersAndGroupsImport(
    {
        "elements_ignored": 0,
        "detailed_status": {
            "message": "Failed parsing line 1 of the input file. Check syntax and contents.",
            "code": "655698",
        },
        "svm": {
            "uuid": "6de1d39d-1473-11ec-b0cf-0050568e4acc",
            "name": "vs1",
            "_links": {
                "self": {"href": "/api/svm/svms/6de1d39d-1473-11ec-b0cf-0050568e4acc"}
            },
        },
        "state": "success",
        "import_uri": {"path": "http://<import_uri>/file.7z"},
        "_links": {
            "self": {
                "href": "/api/protocols/cifs/users-and-groups/import/6de1d39d-1473-11ec-b0cf-0050568e4acc"
            }
        },
        "elements_imported": 0,
    }
)

```
</div>
</div>

## Retrieving bulk import information for CIFS local users, groups, and group memberships
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUsersAndGroupsImport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUsersAndGroupsImport("6de1d39d-1473-11ec-b0cf-0050568e4acc")
    resource.import_uri.username = "user1"
    resource.import_uri.password = "aaaa"
    resource.decryption_password = "cccc"
    resource.import_uri.path = "http://example.com/file1.7z"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
LocalCifsUsersAndGroupsImport(
    {
        "decryption_password": "cccc",
        "import_uri": {
            "path": "http://example.com/file1.7z",
            "password": "aaaa",
            "username": "user1",
        },
    }
)

```
</div>
</div>

## Retrieving status upload information of the last import operation for the specified URI
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LocalCifsUsersAndGroupsImport

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LocalCifsUsersAndGroupsImport("6de1d39d-1473-11ec-b0cf-0050568e4acc")
    resource.status_uri.username = "user1"
    resource.status_uri.password = "aaaa"
    resource.status_uri.path = "http://example.com/fileupload.7z"
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


__all__ = ["LocalCifsUsersAndGroupsImport", "LocalCifsUsersAndGroupsImportSchema"]
__pdoc__ = {
    "LocalCifsUsersAndGroupsImportSchema.resource": False,
    "LocalCifsUsersAndGroupsImportSchema.opts": False,
}


class LocalCifsUsersAndGroupsImportSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the LocalCifsUsersAndGroupsImport object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the local_cifs_users_and_groups_import."""

    decryption_password = marshmallow_fields.Str(
        data_key="decryption_password",
        validate=len_validation(minimum=0, maximum=128),
        allow_none=True,
    )
    r""" Password to decrypt the compressed file."""

    detailed_status = marshmallow_fields.Nested("netapp_ontap.models.detailed_status_code_message.DetailedStatusCodeMessageSchema", data_key="detailed_status", unknown=EXCLUDE, allow_none=True)
    r""" The detailed_status field of the local_cifs_users_and_groups_import."""

    elements_ignored = Size(
        data_key="elements_ignored",
        allow_none=True,
    )
    r""" Number of elements ignored."""

    elements_imported = Size(
        data_key="elements_imported",
        allow_none=True,
    )
    r""" Number of elements successfully imported."""

    import_uri = marshmallow_fields.Nested("netapp_ontap.models.uniform_resource_identifier.UniformResourceIdentifierSchema", data_key="import_uri", unknown=EXCLUDE, allow_none=True)
    r""" The import_uri field of the local_cifs_users_and_groups_import."""

    state = marshmallow_fields.Str(
        data_key="state",
        validate=enum_validation(['failed', 'success', 'success_with_warnings', 'in_progress', 'unknown']),
        allow_none=True,
    )
    r""" Operation status.

Valid choices:

* failed
* success
* success_with_warnings
* in_progress
* unknown"""

    status_uri = marshmallow_fields.Nested("netapp_ontap.models.uniform_resource_identifier.UniformResourceIdentifierSchema", data_key="status_uri", unknown=EXCLUDE, allow_none=True)
    r""" The status_uri field of the local_cifs_users_and_groups_import."""

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE, allow_none=True)
    r""" The svm field of the local_cifs_users_and_groups_import."""

    @property
    def resource(self):
        return LocalCifsUsersAndGroupsImport

    gettable_fields = [
        "links",
        "detailed_status",
        "elements_ignored",
        "elements_imported",
        "import_uri",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,detailed_status,elements_ignored,elements_imported,import_uri,state,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "status_uri",
    ]
    """status_uri,"""

    postable_fields = [
        "decryption_password",
        "import_uri",
    ]
    """decryption_password,import_uri,"""

class LocalCifsUsersAndGroupsImport(Resource):
    """Allows interaction with LocalCifsUsersAndGroupsImport objects on the host"""

    _schema = LocalCifsUsersAndGroupsImportSchema
    _path = "/api/protocols/cifs/users-and-groups/bulk-import/{svm[uuid]}"
    _keys = ["svm.uuid"]






    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about the import operation status of the CIFS local users,
groups, and group memberships.
### Related ONTAP commands
* `vserver cifs users-and-groups import get-status`

### Learn more
* [`DOC /protocols/cifs/users-and-groups/bulk-import/{svm.uuid}`](#docs-NAS-protocols_cifs_users-and-groups_bulk-import_{svm.uuid})"""
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
        r"""Loads CIFS local users,groups and group memberships file from the specified URL.<br/>
### Important notes
Existing CIFS local users, groups, and group memberships will be replaced with the contents of the file.
### Required properties
- import_uri.path
- decryption_password
### Optional properties
- import_uri.username
- import_uri.password
### Related ONTAP commands
* `vserver cifs users-and-groups import load-from-uri`

### Learn more
* [`DOC /protocols/cifs/users-and-groups/bulk-import/{svm.uuid}`](#docs-NAS-protocols_cifs_users-and-groups_bulk-import_{svm.uuid})"""
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
        r"""Upload the status of the bulk-import of the specified SVM to the specified URI.
### Important notes
* Only the status of the last bulk-import will be uploaded and not the status of the previous bulk-imports.
### Required properties
- status_uri.path - URI to which the status needs to be uploaded.
### Optional properties
- status_uri.username - Username of the specified URI.
- status_uri.password - Password of the specified URI.
### Related ONTAP commands
* `vserver cifs users-and-groups import get-status`

### Learn more
* [`DOC /protocols/cifs/users-and-groups/bulk-import/{svm.uuid}`](#docs-NAS-protocols_cifs_users-and-groups_bulk-import_{svm.uuid})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)



