r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationNamespaceObject", "ApplicationNamespaceObjectSchema"]
__pdoc__ = {
    "ApplicationNamespaceObjectSchema.resource": False,
    "ApplicationNamespaceObjectSchema.opts": False,
    "ApplicationNamespaceObject": False,
}


class ApplicationNamespaceObjectSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationNamespaceObject object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the application_namespace_object. """

    creation_timestamp = ImpreciseDateTime(data_key="creation_timestamp", allow_none=True)
    r""" Namespace creation time """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Namespace name """

    size = Size(data_key="size", allow_none=True)
    r""" Namespace size """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" Namespace UUID """

    @property
    def resource(self):
        return ApplicationNamespaceObject

    gettable_fields = [
        "links",
        "creation_timestamp",
        "name",
        "size",
        "uuid",
    ]
    """links,creation_timestamp,name,size,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNamespaceObject(Resource):

    _schema = ApplicationNamespaceObjectSchema
