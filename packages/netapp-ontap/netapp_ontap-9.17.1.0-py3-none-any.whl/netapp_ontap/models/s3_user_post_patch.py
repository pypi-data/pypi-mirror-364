r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["S3UserPostPatch", "S3UserPostPatchSchema"]
__pdoc__ = {
    "S3UserPostPatchSchema.resource": False,
    "S3UserPostPatchSchema.opts": False,
    "S3UserPostPatch": False,
}


class S3UserPostPatchSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the S3UserPostPatch object"""

    num_records = Size(data_key="num_records", allow_none=True)
    r""" Number of records

Example: 1 """

    records = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.s3_service_user_post_response.S3ServiceUserPostSchema", unknown=EXCLUDE, allow_none=True), data_key="records", allow_none=True)
    r""" The records field of the s3_user_post_patch. """

    @property
    def resource(self):
        return S3UserPostPatch

    gettable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""

    patchable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""

    postable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""


class S3UserPostPatch(Resource):

    _schema = S3UserPostPatchSchema
