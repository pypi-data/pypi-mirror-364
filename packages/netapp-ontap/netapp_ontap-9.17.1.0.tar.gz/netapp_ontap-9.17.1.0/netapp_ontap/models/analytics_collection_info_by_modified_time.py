r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AnalyticsCollectionInfoByModifiedTime", "AnalyticsCollectionInfoByModifiedTimeSchema"]
__pdoc__ = {
    "AnalyticsCollectionInfoByModifiedTimeSchema.resource": False,
    "AnalyticsCollectionInfoByModifiedTimeSchema.opts": False,
    "AnalyticsCollectionInfoByModifiedTime": False,
}


class AnalyticsCollectionInfoByModifiedTimeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AnalyticsCollectionInfoByModifiedTime object"""

    bytes_used = marshmallow_fields.Nested("netapp_ontap.models.analytics_collection_info_by_modified_time_bytes_used.AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema", unknown=EXCLUDE, data_key="bytes_used", allow_none=True)
    r""" Number of bytes used on-disk, broken down by date of last modification. """

    @property
    def resource(self):
        return AnalyticsCollectionInfoByModifiedTime

    gettable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""

    patchable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""

    postable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""


class AnalyticsCollectionInfoByModifiedTime(Resource):

    _schema = AnalyticsCollectionInfoByModifiedTimeSchema
