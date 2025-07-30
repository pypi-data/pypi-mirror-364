r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeFiles", "VolumeFilesSchema"]
__pdoc__ = {
    "VolumeFilesSchema.resource": False,
    "VolumeFilesSchema.opts": False,
    "VolumeFiles": False,
}


class VolumeFilesSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeFiles object"""

    inodefile_capacity = Size(data_key="inodefile_capacity", allow_none=True)
    r""" Number of inodes that can currently be stored on the volume for user-visible files.  This number dynamically increases as more user-visible files are created. """

    maximum = Size(data_key="maximum", allow_none=True)
    r""" The maximum number of files (inodes) for user-visible data allowed on the volume. This value can be increased or decreased. Increasing the maximum number of files does not immediately cause additional disk space to be used to track files. Instead, as more files are created on the volume, the system dynamically increases the number of disk blocks that are used to track files. The space assigned to track files is never freed, and this value cannot be decreased below the current number of files that can be tracked within the assigned space for the volume. Valid in PATCH. """

    used = Size(data_key="used", allow_none=True)
    r""" Number of files (inodes) used for user-visible data permitted on the volume. This field is valid only when the volume is online. """

    @property
    def resource(self):
        return VolumeFiles

    gettable_fields = [
        "inodefile_capacity",
        "maximum",
        "used",
    ]
    """inodefile_capacity,maximum,used,"""

    patchable_fields = [
        "maximum",
    ]
    """maximum,"""

    postable_fields = [
        "maximum",
    ]
    """maximum,"""


class VolumeFiles(Resource):

    _schema = VolumeFilesSchema
