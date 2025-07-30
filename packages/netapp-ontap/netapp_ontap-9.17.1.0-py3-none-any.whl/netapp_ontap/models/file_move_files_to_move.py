r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FileMoveFilesToMove", "FileMoveFilesToMoveSchema"]
__pdoc__ = {
    "FileMoveFilesToMoveSchema.resource": False,
    "FileMoveFilesToMoveSchema.opts": False,
    "FileMoveFilesToMove": False,
}


class FileMoveFilesToMoveSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FileMoveFilesToMove object"""

    destinations = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.file_move_file.FileMoveFileSchema", unknown=EXCLUDE, allow_none=True), data_key="destinations", allow_none=True)
    r""" The destination file information. """

    sources = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.file_move_file.FileMoveFileSchema", unknown=EXCLUDE, allow_none=True), data_key="sources", allow_none=True)
    r""" The source file information. """

    @property
    def resource(self):
        return FileMoveFilesToMove

    gettable_fields = [
        "destinations",
        "sources",
    ]
    """destinations,sources,"""

    patchable_fields = [
        "destinations",
        "sources",
    ]
    """destinations,sources,"""

    postable_fields = [
        "destinations",
        "sources",
    ]
    """destinations,sources,"""


class FileMoveFilesToMove(Resource):

    _schema = FileMoveFilesToMoveSchema
