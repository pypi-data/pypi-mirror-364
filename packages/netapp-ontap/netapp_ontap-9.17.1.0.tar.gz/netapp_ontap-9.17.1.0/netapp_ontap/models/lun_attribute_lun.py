r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["LunAttributeLun", "LunAttributeLunSchema"]
__pdoc__ = {
    "LunAttributeLunSchema.resource": False,
    "LunAttributeLunSchema.opts": False,
    "LunAttributeLun": False,
}


class LunAttributeLunSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the LunAttributeLun object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the lun_attribute_lun. """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the LUN.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return LunAttributeLun

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunAttributeLun(Resource):

    _schema = LunAttributeLunSchema
