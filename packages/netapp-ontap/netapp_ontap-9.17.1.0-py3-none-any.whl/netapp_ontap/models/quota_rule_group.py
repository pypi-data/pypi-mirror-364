r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["QuotaRuleGroup", "QuotaRuleGroupSchema"]
__pdoc__ = {
    "QuotaRuleGroupSchema.resource": False,
    "QuotaRuleGroupSchema.opts": False,
    "QuotaRuleGroup": False,
}


class QuotaRuleGroupSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the QuotaRuleGroup object"""

    id = marshmallow_fields.Str(data_key="id", allow_none=True)
    r""" Quota target group ID """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Quota target group name """

    @property
    def resource(self):
        return QuotaRuleGroup

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class QuotaRuleGroup(Resource):

    _schema = QuotaRuleGroupSchema
