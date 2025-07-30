r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["EmsDestinationConnectivityErrors", "EmsDestinationConnectivityErrorsSchema"]
__pdoc__ = {
    "EmsDestinationConnectivityErrorsSchema.resource": False,
    "EmsDestinationConnectivityErrorsSchema.opts": False,
    "EmsDestinationConnectivityErrors": False,
}


class EmsDestinationConnectivityErrorsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the EmsDestinationConnectivityErrors object"""

    message = marshmallow_fields.Nested("netapp_ontap.models.ems_ui_message.EmsUiMessageSchema", unknown=EXCLUDE, data_key="message", allow_none=True)
    r""" Information to be displayed to the user. """

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the ems_destination_connectivity_errors. """

    @property
    def resource(self):
        return EmsDestinationConnectivityErrors

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


class EmsDestinationConnectivityErrors(Resource):

    _schema = EmsDestinationConnectivityErrorsSchema
