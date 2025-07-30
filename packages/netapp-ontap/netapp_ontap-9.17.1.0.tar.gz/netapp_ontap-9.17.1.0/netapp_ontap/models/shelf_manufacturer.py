r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ShelfManufacturer", "ShelfManufacturerSchema"]
__pdoc__ = {
    "ShelfManufacturerSchema.resource": False,
    "ShelfManufacturerSchema.opts": False,
    "ShelfManufacturer": False,
}


class ShelfManufacturerSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ShelfManufacturer object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name field of the shelf_manufacturer.

Example: NETAPP """

    @property
    def resource(self):
        return ShelfManufacturer

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


class ShelfManufacturer(Resource):

    _schema = ShelfManufacturerSchema
