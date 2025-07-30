r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["GroupPolicyObjectSecuritySetting", "GroupPolicyObjectSecuritySettingSchema"]
__pdoc__ = {
    "GroupPolicyObjectSecuritySettingSchema.resource": False,
    "GroupPolicyObjectSecuritySettingSchema.opts": False,
    "GroupPolicyObjectSecuritySetting": False,
}


class GroupPolicyObjectSecuritySettingSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the GroupPolicyObjectSecuritySetting object"""

    event_audit_settings = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_event_audit.GroupPolicyObjectEventAuditSchema", unknown=EXCLUDE, data_key="event_audit_settings", allow_none=True)
    r""" The event_audit_settings field of the group_policy_object_security_setting. """

    event_log_settings = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_event_log.GroupPolicyObjectEventLogSchema", unknown=EXCLUDE, data_key="event_log_settings", allow_none=True)
    r""" The event_log_settings field of the group_policy_object_security_setting. """

    files_or_folders = marshmallow_fields.List(marshmallow_fields.Str, data_key="files_or_folders", allow_none=True)
    r""" Files/Directories for file security.

Example: ["/vol1/home","/vol1/dir1"] """

    kerberos = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_kerberos.GroupPolicyObjectKerberosSchema", unknown=EXCLUDE, data_key="kerberos", allow_none=True)
    r""" The kerberos field of the group_policy_object_security_setting. """

    privilege_rights = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_privilege_right.GroupPolicyObjectPrivilegeRightSchema", unknown=EXCLUDE, data_key="privilege_rights", allow_none=True)
    r""" The privilege_rights field of the group_policy_object_security_setting. """

    registry_values = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_registry_value.GroupPolicyObjectRegistryValueSchema", unknown=EXCLUDE, data_key="registry_values", allow_none=True)
    r""" The registry_values field of the group_policy_object_security_setting. """

    restrict_anonymous = marshmallow_fields.Nested("netapp_ontap.models.group_policy_object_restrict_anonymous.GroupPolicyObjectRestrictAnonymousSchema", unknown=EXCLUDE, data_key="restrict_anonymous", allow_none=True)
    r""" The restrict_anonymous field of the group_policy_object_security_setting. """

    restricted_groups = marshmallow_fields.List(marshmallow_fields.Str, data_key="restricted_groups", allow_none=True)
    r""" The restricted_groups field of the group_policy_object_security_setting. """

    @property
    def resource(self):
        return GroupPolicyObjectSecuritySetting

    gettable_fields = [
        "event_audit_settings",
        "event_log_settings",
        "files_or_folders",
        "kerberos",
        "privilege_rights",
        "registry_values",
        "restrict_anonymous",
        "restricted_groups",
    ]
    """event_audit_settings,event_log_settings,files_or_folders,kerberos,privilege_rights,registry_values,restrict_anonymous,restricted_groups,"""

    patchable_fields = [
        "event_audit_settings",
        "event_log_settings",
        "files_or_folders",
        "kerberos",
        "privilege_rights",
        "registry_values",
        "restrict_anonymous",
        "restricted_groups",
    ]
    """event_audit_settings,event_log_settings,files_or_folders,kerberos,privilege_rights,registry_values,restrict_anonymous,restricted_groups,"""

    postable_fields = [
        "event_audit_settings",
        "event_log_settings",
        "files_or_folders",
        "kerberos",
        "privilege_rights",
        "registry_values",
        "restrict_anonymous",
        "restricted_groups",
    ]
    """event_audit_settings,event_log_settings,files_or_folders,kerberos,privilege_rights,registry_values,restrict_anonymous,restricted_groups,"""


class GroupPolicyObjectSecuritySetting(Resource):

    _schema = GroupPolicyObjectSecuritySettingSchema
