r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["S3PolicyStatement", "S3PolicyStatementSchema"]
__pdoc__ = {
    "S3PolicyStatementSchema.resource": False,
    "S3PolicyStatementSchema.opts": False,
    "S3PolicyStatement": False,
}


class S3PolicyStatementSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the S3PolicyStatement object"""

    actions = marshmallow_fields.List(marshmallow_fields.Str, data_key="actions", allow_none=True)
    r""" For each resource, S3 supports a set of operations. The resource operations allowed or denied are identified by an action list:

* GetObject - retrieves objects from a bucket.
* PutObject - puts objects in a bucket.
* DeleteObject - deletes objects from a bucket.
* ListBucket - lists the objects in a bucket.
* GetBucketAcl - retrieves the access control list (ACL) of a bucket.
* GetObjectAcl - retrieves the access control list (ACL) of an object.
* ListAllMyBuckets - lists all of the buckets in a server.
* ListBucketMultipartUploads - lists the multipart uploads in progress for a bucket.
* ListMultipartUploadParts - lists the parts in a multipart upload.
* CreateBucket - creates a new bucket.
* DeleteBucket - deletes an existing bucket.
* GetObjectTagging - retrieves the tag set of an object.
* PutObjecttagging - sets the tag set for an object.
* DeleteObjectTagging - deletes the tag set of an object.
* GetBucketLocation - retrieves the location of a bucket.
* GetBucketVersioning - retrieves the versioning configuration of a bucket.
* PutBucketVersioning - modifies the versioning configuration of a bucket.
* ListBucketVersions - lists the object versions in a bucket.
* PutBucketPolicy - puts bucket policy on the bucket specified.
* GetBucketPolicy - retrieves the bucket policy of a bucket.
* DeleteBucketPolicy - deletes the policy created for a bucket.
The wildcard character "*" can be used to form a regular expression for specifying actions.


Example: ["*"] """

    effect = marshmallow_fields.Str(data_key="effect", allow_none=True)
    r""" Specifies whether access is allowed or denied. If access (to allow) is not granted explicitly to a resource, access is implicitly denied. Access can also be denied explicitly to a resource, in order to make sure that a user cannot access it, even if a different policy grants access.

Valid choices:

* allow
* deny """

    index = Size(data_key="index", allow_none=True)
    r""" Specifies a unique statement index used to identify a particular statement. This parameter should not be specified in the POST method. A statement index is automatically generated. It is not retrieved in the GET method. """

    resources = marshmallow_fields.List(marshmallow_fields.Str, data_key="resources", allow_none=True)
    r""" The resources field of the s3_policy_statement.

Example: ["bucket1","bucket1/*"] """

    sid = marshmallow_fields.Str(data_key="sid", allow_none=True)
    r""" Specifies the statement identifier which contains additional information about the statement.

Example: FullAccessToBucket1 """

    @property
    def resource(self):
        return S3PolicyStatement

    gettable_fields = [
        "actions",
        "effect",
        "index",
        "resources",
        "sid",
    ]
    """actions,effect,index,resources,sid,"""

    patchable_fields = [
        "actions",
        "effect",
        "resources",
        "sid",
    ]
    """actions,effect,resources,sid,"""

    postable_fields = [
        "actions",
        "effect",
        "resources",
        "sid",
    ]
    """actions,effect,resources,sid,"""


class S3PolicyStatement(Resource):

    _schema = S3PolicyStatementSchema
