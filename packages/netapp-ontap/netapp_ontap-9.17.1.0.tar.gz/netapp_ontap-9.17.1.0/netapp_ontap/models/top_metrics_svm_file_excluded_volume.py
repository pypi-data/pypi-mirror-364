r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["TopMetricsSvmFileExcludedVolume", "TopMetricsSvmFileExcludedVolumeSchema"]
__pdoc__ = {
    "TopMetricsSvmFileExcludedVolumeSchema.resource": False,
    "TopMetricsSvmFileExcludedVolumeSchema.opts": False,
    "TopMetricsSvmFileExcludedVolume": False,
}


class TopMetricsSvmFileExcludedVolumeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the TopMetricsSvmFileExcludedVolume object"""

    reason = marshmallow_fields.Nested("netapp_ontap.models.top_metrics_svm_client_excluded_volume_reason.TopMetricsSvmClientExcludedVolumeReasonSchema", unknown=EXCLUDE, data_key="reason", allow_none=True)
    r""" The reason field of the top_metrics_svm_file_excluded_volume. """

    volume = marshmallow_fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume", allow_none=True)
    r""" The volume field of the top_metrics_svm_file_excluded_volume. """

    @property
    def resource(self):
        return TopMetricsSvmFileExcludedVolume

    gettable_fields = [
        "reason",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """reason,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class TopMetricsSvmFileExcludedVolume(Resource):

    _schema = TopMetricsSvmFileExcludedVolumeSchema
