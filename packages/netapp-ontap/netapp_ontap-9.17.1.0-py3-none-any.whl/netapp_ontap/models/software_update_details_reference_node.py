r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SoftwareUpdateDetailsReferenceNode", "SoftwareUpdateDetailsReferenceNodeSchema"]
__pdoc__ = {
    "SoftwareUpdateDetailsReferenceNodeSchema.resource": False,
    "SoftwareUpdateDetailsReferenceNodeSchema.opts": False,
    "SoftwareUpdateDetailsReferenceNode": False,
}


class SoftwareUpdateDetailsReferenceNodeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SoftwareUpdateDetailsReferenceNode object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Name of the node to be retrieved for update details.

Example: node1 """

    @property
    def resource(self):
        return SoftwareUpdateDetailsReferenceNode

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwareUpdateDetailsReferenceNode(Resource):

    _schema = SoftwareUpdateDetailsReferenceNodeSchema
