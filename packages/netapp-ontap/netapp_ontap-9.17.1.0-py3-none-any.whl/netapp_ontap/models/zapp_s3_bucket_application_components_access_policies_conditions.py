r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ZappS3BucketApplicationComponentsAccessPoliciesConditions", "ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema"]
__pdoc__ = {
    "ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema.resource": False,
    "ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema.opts": False,
    "ZappS3BucketApplicationComponentsAccessPoliciesConditions": False,
}


class ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ZappS3BucketApplicationComponentsAccessPoliciesConditions object"""

    delimiters = marshmallow_fields.List(marshmallow_fields.Str, data_key="delimiters", allow_none=True)
    r""" The delimiters field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    max_keys = marshmallow_fields.List(Size, data_key="max_keys", allow_none=True)
    r""" The max_keys field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    operator = marshmallow_fields.Str(data_key="operator", allow_none=True)
    r""" Policy Condition Operator. """

    prefixes = marshmallow_fields.List(marshmallow_fields.Str, data_key="prefixes", allow_none=True)
    r""" The prefixes field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    source_ips = marshmallow_fields.List(marshmallow_fields.Str, data_key="source_ips", allow_none=True)
    r""" The source_ips field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    usernames = marshmallow_fields.List(marshmallow_fields.Str, data_key="usernames", allow_none=True)
    r""" The usernames field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    @property
    def resource(self):
        return ZappS3BucketApplicationComponentsAccessPoliciesConditions

    gettable_fields = [
        "delimiters",
        "max_keys",
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""

    patchable_fields = [
        "delimiters",
        "max_keys",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,prefixes,source_ips,usernames,"""

    postable_fields = [
        "delimiters",
        "max_keys",
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""


class ZappS3BucketApplicationComponentsAccessPoliciesConditions(Resource):

    _schema = ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema
