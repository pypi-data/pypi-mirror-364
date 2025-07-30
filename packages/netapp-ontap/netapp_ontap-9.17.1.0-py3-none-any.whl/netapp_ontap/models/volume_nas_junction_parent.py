r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeNasJunctionParent", "VolumeNasJunctionParentSchema"]
__pdoc__ = {
    "VolumeNasJunctionParentSchema.resource": False,
    "VolumeNasJunctionParentSchema.opts": False,
    "VolumeNasJunctionParent": False,
}


class VolumeNasJunctionParentSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeNasJunctionParent object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the volume_nas_junction_parent. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the parent volume that contains the junction inode of this volume. The junction parent volume must belong to the same SVM that owns this volume.

Example: vs1_root """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" Unique identifier for the parent volume.

Example: 75c9cfb0-3eb4-11eb-9fb4-005056bb088a """

    @property
    def resource(self):
        return VolumeNasJunctionParent

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class VolumeNasJunctionParent(Resource):

    _schema = VolumeNasJunctionParentSchema
