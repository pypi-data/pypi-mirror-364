r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationComponentSnapshotComponent", "ApplicationComponentSnapshotComponentSchema"]
__pdoc__ = {
    "ApplicationComponentSnapshotComponentSchema.resource": False,
    "ApplicationComponentSnapshotComponentSchema.opts": False,
    "ApplicationComponentSnapshotComponent": False,
}


class ApplicationComponentSnapshotComponentSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationComponentSnapshotComponent object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the application_component_snapshot_component. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Component Name """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" Component UUID """

    @property
    def resource(self):
        return ApplicationComponentSnapshotComponent

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


class ApplicationComponentSnapshotComponent(Resource):

    _schema = ApplicationComponentSnapshotComponentSchema
