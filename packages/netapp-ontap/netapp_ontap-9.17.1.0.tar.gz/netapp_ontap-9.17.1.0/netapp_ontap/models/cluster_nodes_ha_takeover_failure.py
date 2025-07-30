r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ClusterNodesHaTakeoverFailure", "ClusterNodesHaTakeoverFailureSchema"]
__pdoc__ = {
    "ClusterNodesHaTakeoverFailureSchema.resource": False,
    "ClusterNodesHaTakeoverFailureSchema.opts": False,
    "ClusterNodesHaTakeoverFailure": False,
}


class ClusterNodesHaTakeoverFailureSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ClusterNodesHaTakeoverFailure object"""

    code = Size(data_key="code", allow_none=True)
    r""" Message code

Example: 852130 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Detailed message based on the state.

Example: Failed to initiate takeover. Run the "storage failover show-takeover" command for more information. """

    @property
    def resource(self):
        return ClusterNodesHaTakeoverFailure

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    postable_fields = [
        "code",
        "message",
    ]
    """code,message,"""


class ClusterNodesHaTakeoverFailure(Resource):

    _schema = ClusterNodesHaTakeoverFailureSchema
