r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationSnapshotRestoreApplication", "ApplicationSnapshotRestoreApplicationSchema"]
__pdoc__ = {
    "ApplicationSnapshotRestoreApplicationSchema.resource": False,
    "ApplicationSnapshotRestoreApplicationSchema.opts": False,
    "ApplicationSnapshotRestoreApplication": False,
}


class ApplicationSnapshotRestoreApplicationSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationSnapshotRestoreApplication object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the application_snapshot_restore_application. """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The application UUID. Valid in URL or POST. """

    @property
    def resource(self):
        return ApplicationSnapshotRestoreApplication

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
        "uuid",
    ]
    """uuid,"""

    postable_fields = [
        "uuid",
    ]
    """uuid,"""


class ApplicationSnapshotRestoreApplication(Resource):

    _schema = ApplicationSnapshotRestoreApplicationSchema
