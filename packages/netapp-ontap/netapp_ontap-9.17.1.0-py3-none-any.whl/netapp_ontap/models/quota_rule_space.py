r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["QuotaRuleSpace", "QuotaRuleSpaceSchema"]
__pdoc__ = {
    "QuotaRuleSpaceSchema.resource": False,
    "QuotaRuleSpaceSchema.opts": False,
    "QuotaRuleSpace": False,
}


class QuotaRuleSpaceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the QuotaRuleSpace object"""

    hard_limit = Size(data_key="hard_limit", allow_none=True)
    r""" This parameter specifies the space hard limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes. Valid in POST or PATCH. For a POST operation where the parameter is either empty or set to -1, no limit is applied. For a PATCH operation where a limit is configured, use a value of -1 to clear the limit. """

    soft_limit = Size(data_key="soft_limit", allow_none=True)
    r""" This parameter specifies the space soft limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes. Valid in POST or PATCH. For a POST operation where the parameter is either empty or set to -1, no limit is applied. For a PATCH operation where a limit is configured, use a value of -1 to clear the limit. """

    @property
    def resource(self):
        return QuotaRuleSpace

    gettable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""

    patchable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""

    postable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""


class QuotaRuleSpace(Resource):

    _schema = QuotaRuleSpaceSchema
