r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FileMoveFilesToMoveSources", "FileMoveFilesToMoveSourcesSchema"]
__pdoc__ = {
    "FileMoveFilesToMoveSourcesSchema.resource": False,
    "FileMoveFilesToMoveSourcesSchema.opts": False,
    "FileMoveFilesToMoveSources": False,
}


class FileMoveFilesToMoveSourcesSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FileMoveFilesToMoveSources object"""

    path = marshmallow_fields.Str(data_key="path", allow_none=True)
    r""" The path field of the file_move_files_to_move_sources.

Example: d1/d2/file1 """

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm", allow_none=True)
    r""" The svm field of the file_move_files_to_move_sources. """

    volume = marshmallow_fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume", allow_none=True)
    r""" The volume field of the file_move_files_to_move_sources. """

    @property
    def resource(self):
        return FileMoveFilesToMoveSources

    gettable_fields = [
        "path",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """path,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "path",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """path,svm.name,svm.uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "path",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """path,svm.name,svm.uuid,volume.name,volume.uuid,"""


class FileMoveFilesToMoveSources(Resource):

    _schema = FileMoveFilesToMoveSourcesSchema
