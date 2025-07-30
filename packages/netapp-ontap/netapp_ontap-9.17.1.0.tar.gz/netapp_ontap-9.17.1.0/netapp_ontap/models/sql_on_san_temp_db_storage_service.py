r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SqlOnSanTempDbStorageService", "SqlOnSanTempDbStorageServiceSchema"]
__pdoc__ = {
    "SqlOnSanTempDbStorageServiceSchema.resource": False,
    "SqlOnSanTempDbStorageServiceSchema.opts": False,
    "SqlOnSanTempDbStorageService": False,
}


class SqlOnSanTempDbStorageServiceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SqlOnSanTempDbStorageService object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The storage service of the temp DB.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return SqlOnSanTempDbStorageService

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class SqlOnSanTempDbStorageService(Resource):

    _schema = SqlOnSanTempDbStorageServiceSchema
