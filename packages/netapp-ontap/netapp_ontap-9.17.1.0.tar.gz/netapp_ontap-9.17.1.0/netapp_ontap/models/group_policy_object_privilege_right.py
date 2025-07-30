r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["GroupPolicyObjectPrivilegeRight", "GroupPolicyObjectPrivilegeRightSchema"]
__pdoc__ = {
    "GroupPolicyObjectPrivilegeRightSchema.resource": False,
    "GroupPolicyObjectPrivilegeRightSchema.opts": False,
    "GroupPolicyObjectPrivilegeRight": False,
}


class GroupPolicyObjectPrivilegeRightSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the GroupPolicyObjectPrivilegeRight object"""

    change_notify_users = marshmallow_fields.List(marshmallow_fields.Str, data_key="change_notify_users", allow_none=True)
    r""" Users with traversing bypass privileges.

Example: ["usr1","usr2"] """

    security_privilege_users = marshmallow_fields.List(marshmallow_fields.Str, data_key="security_privilege_users", allow_none=True)
    r""" Users with security privileges.

Example: ["usr1","usr2"] """

    take_ownership_users = marshmallow_fields.List(marshmallow_fields.Str, data_key="take_ownership_users", allow_none=True)
    r""" Users who can take ownership of securable objects.

Example: ["usr1","usr2"] """

    @property
    def resource(self):
        return GroupPolicyObjectPrivilegeRight

    gettable_fields = [
        "change_notify_users",
        "security_privilege_users",
        "take_ownership_users",
    ]
    """change_notify_users,security_privilege_users,take_ownership_users,"""

    patchable_fields = [
        "change_notify_users",
        "security_privilege_users",
        "take_ownership_users",
    ]
    """change_notify_users,security_privilege_users,take_ownership_users,"""

    postable_fields = [
        "change_notify_users",
        "security_privilege_users",
        "take_ownership_users",
    ]
    """change_notify_users,security_privilege_users,take_ownership_users,"""


class GroupPolicyObjectPrivilegeRight(Resource):

    _schema = GroupPolicyObjectPrivilegeRightSchema
