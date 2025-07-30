r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["EmsConnectivityError", "EmsConnectivityErrorSchema"]
__pdoc__ = {
    "EmsConnectivityErrorSchema.resource": False,
    "EmsConnectivityErrorSchema.opts": False,
    "EmsConnectivityError": False,
}


class EmsConnectivityErrorSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the EmsConnectivityError object"""

    message = marshmallow_fields.Nested("netapp_ontap.models.ems_ui_message.EmsUiMessageSchema", unknown=EXCLUDE, data_key="message", allow_none=True)
    r""" Information to be displayed to the user. """

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the ems_connectivity_error. """

    @property
    def resource(self):
        return EmsConnectivityError

    gettable_fields = [
        "message",
        "node.links",
        "node.name",
        "node.uuid",
    ]
    """message,node.links,node.name,node.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class EmsConnectivityError(Resource):

    _schema = EmsConnectivityErrorSchema
