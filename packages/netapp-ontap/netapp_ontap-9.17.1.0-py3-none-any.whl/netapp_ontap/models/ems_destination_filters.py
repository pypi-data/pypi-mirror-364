r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["EmsDestinationFilters", "EmsDestinationFiltersSchema"]
__pdoc__ = {
    "EmsDestinationFiltersSchema.resource": False,
    "EmsDestinationFiltersSchema.opts": False,
    "EmsDestinationFilters": False,
}


class EmsDestinationFiltersSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the EmsDestinationFilters object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the ems_destination_filters. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name field of the ems_destination_filters.

Example: important-events """

    @property
    def resource(self):
        return EmsDestinationFilters

    gettable_fields = [
        "links",
        "name",
    ]
    """links,name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class EmsDestinationFilters(Resource):

    _schema = EmsDestinationFiltersSchema
