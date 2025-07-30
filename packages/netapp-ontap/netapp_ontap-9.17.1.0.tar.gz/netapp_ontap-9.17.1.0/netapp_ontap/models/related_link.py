r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["RelatedLink", "RelatedLinkSchema"]
__pdoc__ = {
    "RelatedLinkSchema.resource": False,
    "RelatedLinkSchema.opts": False,
    "RelatedLink": False,
}


class RelatedLinkSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the RelatedLink object"""

    related = marshmallow_fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="related", allow_none=True)
    r""" The related field of the related_link. """

    @property
    def resource(self):
        return RelatedLink

    gettable_fields = [
        "related",
    ]
    """related,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class RelatedLink(Resource):

    _schema = RelatedLinkSchema
