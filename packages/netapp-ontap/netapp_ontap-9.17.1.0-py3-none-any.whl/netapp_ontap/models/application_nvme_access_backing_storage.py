r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationNvmeAccessBackingStorage", "ApplicationNvmeAccessBackingStorageSchema"]
__pdoc__ = {
    "ApplicationNvmeAccessBackingStorageSchema.resource": False,
    "ApplicationNvmeAccessBackingStorageSchema.opts": False,
    "ApplicationNvmeAccessBackingStorage": False,
}


class ApplicationNvmeAccessBackingStorageSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationNvmeAccessBackingStorage object"""

    type = marshmallow_fields.Str(data_key="type", allow_none=True)
    r""" Backing storage type

Valid choices:

* namespace """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" Backing storage UUID """

    @property
    def resource(self):
        return ApplicationNvmeAccessBackingStorage

    gettable_fields = [
        "type",
        "uuid",
    ]
    """type,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNvmeAccessBackingStorage(Resource):

    _schema = ApplicationNvmeAccessBackingStorageSchema
