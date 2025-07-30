r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["MultiAdminVerifyRuleApprovalGroups", "MultiAdminVerifyRuleApprovalGroupsSchema"]
__pdoc__ = {
    "MultiAdminVerifyRuleApprovalGroupsSchema.resource": False,
    "MultiAdminVerifyRuleApprovalGroupsSchema.opts": False,
    "MultiAdminVerifyRuleApprovalGroups": False,
}


class MultiAdminVerifyRuleApprovalGroupsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the MultiAdminVerifyRuleApprovalGroups object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Name of the approval group. """

    @property
    def resource(self):
        return MultiAdminVerifyRuleApprovalGroups

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class MultiAdminVerifyRuleApprovalGroups(Resource):

    _schema = MultiAdminVerifyRuleApprovalGroupsSchema
