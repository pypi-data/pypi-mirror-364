r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareAttackReportLinks", "AntiRansomwareAttackReportLinksSchema"]
__pdoc__ = {
    "AntiRansomwareAttackReportLinksSchema.resource": False,
    "AntiRansomwareAttackReportLinksSchema.opts": False,
    "AntiRansomwareAttackReportLinks": False,
}


class AntiRansomwareAttackReportLinksSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AntiRansomwareAttackReportLinks object"""

    suspects = marshmallow_fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="suspects", allow_none=True)
    r""" The suspects field of the anti_ransomware_attack_report_links. """

    @property
    def resource(self):
        return AntiRansomwareAttackReportLinks

    gettable_fields = [
        "suspects",
    ]
    """suspects,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AntiRansomwareAttackReportLinks(Resource):

    _schema = AntiRansomwareAttackReportLinksSchema
