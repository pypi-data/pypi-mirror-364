r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AppNfsAccess", "AppNfsAccessSchema"]
__pdoc__ = {
    "AppNfsAccessSchema.resource": False,
    "AppNfsAccessSchema.opts": False,
    "AppNfsAccess": False,
}


class AppNfsAccessSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AppNfsAccess object"""

    access = marshmallow_fields.Str(data_key="access", allow_none=True)
    r""" The NFS access granted.

Valid choices:

* none
* ro
* rw """

    host = marshmallow_fields.Str(data_key="host", allow_none=True)
    r""" The name of the NFS entity granted access. """

    @property
    def resource(self):
        return AppNfsAccess

    gettable_fields = [
        "access",
        "host",
    ]
    """access,host,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "access",
        "host",
    ]
    """access,host,"""


class AppNfsAccess(Resource):

    _schema = AppNfsAccessSchema
