r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Member", "MemberSchema"]
__pdoc__ = {
    "MemberSchema.resource": False,
    "MemberSchema.opts": False,
    "Member": False,
}


class MemberSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Member object"""

    nis_netgroup = marshmallow_fields.Str(data_key="nis_netgroup", allow_none=True)
    r""" RFC 2307 memberNisNetgroup attribute.

Example: msSFU30MemberNisNetgroup """

    uid = marshmallow_fields.Str(data_key="uid", allow_none=True)
    r""" RFC 2307 memberUid attribute.

Example: msSFU30MemberUid """

    @property
    def resource(self):
        return Member

    gettable_fields = [
        "nis_netgroup",
        "uid",
    ]
    """nis_netgroup,uid,"""

    patchable_fields = [
        "nis_netgroup",
        "uid",
    ]
    """nis_netgroup,uid,"""

    postable_fields = [
        "nis_netgroup",
        "uid",
    ]
    """nis_netgroup,uid,"""


class Member(Resource):

    _schema = MemberSchema
