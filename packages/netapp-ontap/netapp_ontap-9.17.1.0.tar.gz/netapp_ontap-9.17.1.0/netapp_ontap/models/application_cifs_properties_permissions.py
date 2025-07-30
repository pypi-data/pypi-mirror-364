r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationCifsPropertiesPermissions", "ApplicationCifsPropertiesPermissionsSchema"]
__pdoc__ = {
    "ApplicationCifsPropertiesPermissionsSchema.resource": False,
    "ApplicationCifsPropertiesPermissionsSchema.opts": False,
    "ApplicationCifsPropertiesPermissions": False,
}


class ApplicationCifsPropertiesPermissionsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationCifsPropertiesPermissions object"""

    access = marshmallow_fields.Str(data_key="access", allow_none=True)
    r""" Access granted to the user or group """

    user_or_group = marshmallow_fields.Str(data_key="user_or_group", allow_none=True)
    r""" User or group """

    @property
    def resource(self):
        return ApplicationCifsPropertiesPermissions

    gettable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationCifsPropertiesPermissions(Resource):

    _schema = ApplicationCifsPropertiesPermissionsSchema
