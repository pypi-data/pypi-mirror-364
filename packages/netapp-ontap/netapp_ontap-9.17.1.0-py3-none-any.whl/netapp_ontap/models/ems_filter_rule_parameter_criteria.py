r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["EmsFilterRuleParameterCriteria", "EmsFilterRuleParameterCriteriaSchema"]
__pdoc__ = {
    "EmsFilterRuleParameterCriteriaSchema.resource": False,
    "EmsFilterRuleParameterCriteriaSchema.opts": False,
    "EmsFilterRuleParameterCriteria": False,
}


class EmsFilterRuleParameterCriteriaSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the EmsFilterRuleParameterCriteria object"""

    name_pattern = marshmallow_fields.Str(data_key="name_pattern", allow_none=True)
    r""" Parameter name pattern. Wildcard character '*' is supported.

Example: vol """

    value_pattern = marshmallow_fields.Str(data_key="value_pattern", allow_none=True)
    r""" Parameter value pattern. Wildcard character '*' is supported.

Example: cloud* """

    @property
    def resource(self):
        return EmsFilterRuleParameterCriteria

    gettable_fields = [
        "name_pattern",
        "value_pattern",
    ]
    """name_pattern,value_pattern,"""

    patchable_fields = [
        "name_pattern",
        "value_pattern",
    ]
    """name_pattern,value_pattern,"""

    postable_fields = [
        "name_pattern",
        "value_pattern",
    ]
    """name_pattern,value_pattern,"""


class EmsFilterRuleParameterCriteria(Resource):

    _schema = EmsFilterRuleParameterCriteriaSchema
