r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AggregateCloudStorage", "AggregateCloudStorageSchema"]
__pdoc__ = {
    "AggregateCloudStorageSchema.resource": False,
    "AggregateCloudStorageSchema.opts": False,
    "AggregateCloudStorage": False,
}


class AggregateCloudStorageSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AggregateCloudStorage object"""

    attach_eligible = marshmallow_fields.Boolean(data_key="attach_eligible", allow_none=True)
    r""" Specifies whether the aggregate is eligible for a cloud store to be attached. """

    migrate_threshold = Size(data_key="migrate_threshold", allow_none=True)
    r""" Specifies the minimum percentage of performance tier free space that must exist in order for migration of data from the capacity tier to performance tier to be allowed. Only valid for PATCH operations. """

    stores = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.cloud_storage_tier.CloudStorageTierSchema", unknown=EXCLUDE, allow_none=True), data_key="stores", allow_none=True)
    r""" Configuration information for each cloud storage portion of the aggregate. """

    tiering_fullness_threshold = Size(data_key="tiering_fullness_threshold", allow_none=True)
    r""" The percentage of space in the performance tier that must be used before data is tiered out to the cloud store. Only valid for PATCH operations. """

    @property
    def resource(self):
        return AggregateCloudStorage

    gettable_fields = [
        "attach_eligible",
        "stores",
    ]
    """attach_eligible,stores,"""

    patchable_fields = [
        "migrate_threshold",
        "tiering_fullness_threshold",
    ]
    """migrate_threshold,tiering_fullness_threshold,"""

    postable_fields = [
    ]
    """"""


class AggregateCloudStorage(Resource):

    _schema = AggregateCloudStorageSchema
