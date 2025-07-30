r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SecurityAuditLogSvm", "SecurityAuditLogSvmSchema"]
__pdoc__ = {
    "SecurityAuditLogSvmSchema.resource": False,
    "SecurityAuditLogSvmSchema.opts": False,
    "SecurityAuditLogSvm": False,
}


class SecurityAuditLogSvmSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SecurityAuditLogSvm object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name field of the security_audit_log_svm. """

    @property
    def resource(self):
        return SecurityAuditLogSvm

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


class SecurityAuditLogSvm(Resource):

    _schema = SecurityAuditLogSvmSchema
