r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ManagementProtocols", "ManagementProtocolsSchema"]
__pdoc__ = {
    "ManagementProtocolsSchema.resource": False,
    "ManagementProtocolsSchema.opts": False,
    "ManagementProtocols": False,
}


class ManagementProtocolsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ManagementProtocols object"""

    rsh_enabled = marshmallow_fields.Boolean(data_key="rsh_enabled", allow_none=True)
    r""" Indicates whether or not security protocol rsh is enabled on the cluster. """

    telnet_enabled = marshmallow_fields.Boolean(data_key="telnet_enabled", allow_none=True)
    r""" Indicates whether or not security protocol telnet is enabled on the cluster. """

    @property
    def resource(self):
        return ManagementProtocols

    gettable_fields = [
        "rsh_enabled",
        "telnet_enabled",
    ]
    """rsh_enabled,telnet_enabled,"""

    patchable_fields = [
        "rsh_enabled",
        "telnet_enabled",
    ]
    """rsh_enabled,telnet_enabled,"""

    postable_fields = [
    ]
    """"""


class ManagementProtocols(Resource):

    _schema = ManagementProtocolsSchema
