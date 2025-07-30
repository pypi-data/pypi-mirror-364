r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["QuotaReportSpaceUsed", "QuotaReportSpaceUsedSchema"]
__pdoc__ = {
    "QuotaReportSpaceUsedSchema.resource": False,
    "QuotaReportSpaceUsedSchema.opts": False,
    "QuotaReportSpaceUsed": False,
}


class QuotaReportSpaceUsedSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the QuotaReportSpaceUsed object"""

    hard_limit_percent = Size(data_key="hard_limit_percent", allow_none=True)
    r""" Total space used as a percentage of space hard limit """

    soft_limit_percent = Size(data_key="soft_limit_percent", allow_none=True)
    r""" Total space used as a percentage of space soft limit """

    total = Size(data_key="total", allow_none=True)
    r""" Total space used """

    @property
    def resource(self):
        return QuotaReportSpaceUsed

    gettable_fields = [
        "hard_limit_percent",
        "soft_limit_percent",
        "total",
    ]
    """hard_limit_percent,soft_limit_percent,total,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class QuotaReportSpaceUsed(Resource):

    _schema = QuotaReportSpaceUsedSchema
