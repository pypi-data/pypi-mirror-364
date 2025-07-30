r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["DrPair", "DrPairSchema"]
__pdoc__ = {
    "DrPairSchema.resource": False,
    "DrPairSchema.opts": False,
    "DrPair": False,
}


class DrPairSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the DrPair object"""

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the dr_pair. """

    partner = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="partner", allow_none=True)
    r""" The partner field of the dr_pair. """

    @property
    def resource(self):
        return DrPair

    gettable_fields = [
        "node.links",
        "node.name",
        "node.uuid",
        "partner.links",
        "partner.name",
        "partner.uuid",
    ]
    """node.links,node.name,node.uuid,partner.links,partner.name,partner.uuid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
        "partner.name",
        "partner.uuid",
    ]
    """node.name,node.uuid,partner.name,partner.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
        "partner.name",
        "partner.uuid",
    ]
    """node.name,node.uuid,partner.name,partner.uuid,"""


class DrPair(Resource):

    _schema = DrPairSchema
