r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["WindowsToUnix", "WindowsToUnixSchema"]
__pdoc__ = {
    "WindowsToUnixSchema.resource": False,
    "WindowsToUnixSchema.opts": False,
    "WindowsToUnix": False,
}


class WindowsToUnixSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the WindowsToUnix object"""

    attribute = marshmallow_fields.Str(data_key="attribute", allow_none=True)
    r""" Attribute name used to retrieve the UNIX account information for a Windows user account.

Example: windowsAccount """

    no_domain_prefix = marshmallow_fields.Boolean(data_key="no_domain_prefix", allow_none=True)
    r""" Indicates whether or not the name for Windows to UNIX name mapping should have a domain prefix.

Example: false """

    object_class = marshmallow_fields.Str(data_key="object_class", allow_none=True)
    r""" Name used to represent the windowsToUnix object class.

Example: User """

    @property
    def resource(self):
        return WindowsToUnix

    gettable_fields = [
        "attribute",
        "no_domain_prefix",
        "object_class",
    ]
    """attribute,no_domain_prefix,object_class,"""

    patchable_fields = [
        "attribute",
        "no_domain_prefix",
        "object_class",
    ]
    """attribute,no_domain_prefix,object_class,"""

    postable_fields = [
        "attribute",
        "no_domain_prefix",
        "object_class",
    ]
    """attribute,no_domain_prefix,object_class,"""


class WindowsToUnix(Resource):

    _schema = WindowsToUnixSchema
