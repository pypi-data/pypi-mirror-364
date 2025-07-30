r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AppCifsAccess", "AppCifsAccessSchema"]
__pdoc__ = {
    "AppCifsAccessSchema.resource": False,
    "AppCifsAccessSchema.opts": False,
    "AppCifsAccess": False,
}


class AppCifsAccessSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AppCifsAccess object"""

    access = marshmallow_fields.Str(data_key="access", allow_none=True)
    r""" The CIFS access granted to the user or group.

Valid choices:

* change
* full_control
* no_access
* read """

    user_or_group = marshmallow_fields.Str(data_key="user_or_group", allow_none=True)
    r""" The name of the CIFS user or group that will be granted access. """

    @property
    def resource(self):
        return AppCifsAccess

    gettable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""


class AppCifsAccess(Resource):

    _schema = AppCifsAccessSchema
