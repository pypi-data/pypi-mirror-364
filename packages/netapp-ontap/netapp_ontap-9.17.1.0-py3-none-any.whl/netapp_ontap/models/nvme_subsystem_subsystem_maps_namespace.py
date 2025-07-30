r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemSubsystemMapsNamespace", "NvmeSubsystemSubsystemMapsNamespaceSchema"]
__pdoc__ = {
    "NvmeSubsystemSubsystemMapsNamespaceSchema.resource": False,
    "NvmeSubsystemSubsystemMapsNamespaceSchema.opts": False,
    "NvmeSubsystemSubsystemMapsNamespace": False,
}


class NvmeSubsystemSubsystemMapsNamespaceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NvmeSubsystemSubsystemMapsNamespace object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the nvme_subsystem_subsystem_maps_namespace. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the NVMe namespace.


Example: /vol/vol1/namespace1 """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the NVMe namespace.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeSubsystemSubsystemMapsNamespace

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeSubsystemSubsystemMapsNamespace(Resource):

    _schema = NvmeSubsystemSubsystemMapsNamespaceSchema
