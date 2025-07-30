r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["OnboardKeyManagerConfigurableStatus", "OnboardKeyManagerConfigurableStatusSchema"]
__pdoc__ = {
    "OnboardKeyManagerConfigurableStatusSchema.resource": False,
    "OnboardKeyManagerConfigurableStatusSchema.opts": False,
    "OnboardKeyManagerConfigurableStatus": False,
}


class OnboardKeyManagerConfigurableStatusSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the OnboardKeyManagerConfigurableStatus object"""

    code = Size(data_key="code", allow_none=True)
    r""" Code corresponding to the status message. Returns a 0 if the Onboard Key Manager can be configured in the cluster.

Example: 65537300 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Reason that Onboard Key Manager cannot be configured in the cluster.

Example: No platform support for volume encryption in following nodes - node1, node2. """

    supported = marshmallow_fields.Boolean(data_key="supported", allow_none=True)
    r""" Set to true if the Onboard Key Manager can be configured in the cluster. """

    @property
    def resource(self):
        return OnboardKeyManagerConfigurableStatus

    gettable_fields = [
        "code",
        "message",
        "supported",
    ]
    """code,message,supported,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class OnboardKeyManagerConfigurableStatus(Resource):

    _schema = OnboardKeyManagerConfigurableStatusSchema
