r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["S3ServicePost", "S3ServicePostSchema"]
__pdoc__ = {
    "S3ServicePostSchema.resource": False,
    "S3ServicePostSchema.opts": False,
    "S3ServicePost": False,
}


class S3ServicePostSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the S3ServicePost object"""

    num_records = Size(data_key="num_records", allow_none=True)
    r""" Number of Records

Example: 1 """

    records = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.s3_service_post_response_records.S3ServicePostResponseRecordsSchema", unknown=EXCLUDE, allow_none=True), data_key="records", allow_none=True)
    r""" The records field of the s3_service_post. """

    @property
    def resource(self):
        return S3ServicePost

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


class S3ServicePost(Resource):

    _schema = S3ServicePostSchema
