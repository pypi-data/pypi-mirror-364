r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["QuotaReportFiles", "QuotaReportFilesSchema"]
__pdoc__ = {
    "QuotaReportFilesSchema.resource": False,
    "QuotaReportFilesSchema.opts": False,
    "QuotaReportFiles": False,
}


class QuotaReportFilesSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the QuotaReportFiles object"""

    hard_limit = Size(data_key="hard_limit", allow_none=True)
    r""" File hard limit """

    soft_limit = Size(data_key="soft_limit", allow_none=True)
    r""" File soft limit """

    used = marshmallow_fields.Nested("netapp_ontap.models.quota_report_files_used.QuotaReportFilesUsedSchema", unknown=EXCLUDE, data_key="used", allow_none=True)
    r""" The used field of the quota_report_files. """

    @property
    def resource(self):
        return QuotaReportFiles

    gettable_fields = [
        "hard_limit",
        "soft_limit",
        "used",
    ]
    """hard_limit,soft_limit,used,"""

    patchable_fields = [
        "used",
    ]
    """used,"""

    postable_fields = [
        "used",
    ]
    """used,"""


class QuotaReportFiles(Resource):

    _schema = QuotaReportFilesSchema
