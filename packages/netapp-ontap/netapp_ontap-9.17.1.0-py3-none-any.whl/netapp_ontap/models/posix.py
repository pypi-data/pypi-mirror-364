r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Posix", "PosixSchema"]
__pdoc__ = {
    "PosixSchema.resource": False,
    "PosixSchema.opts": False,
    "Posix": False,
}


class PosixSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Posix object"""

    account = marshmallow_fields.Str(data_key="account", allow_none=True)
    r""" RFC 2307 posixAccount object class.

Example: User """

    group = marshmallow_fields.Str(data_key="group", allow_none=True)
    r""" RFC 2307 posixGroup object class.

Example: Group """

    @property
    def resource(self):
        return Posix

    gettable_fields = [
        "account",
        "group",
    ]
    """account,group,"""

    patchable_fields = [
        "account",
        "group",
    ]
    """account,group,"""

    postable_fields = [
        "account",
        "group",
    ]
    """account,group,"""


class Posix(Resource):

    _schema = PosixSchema
