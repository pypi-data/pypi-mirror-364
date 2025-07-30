r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AzureKeyVaultEkmipReachability", "AzureKeyVaultEkmipReachabilitySchema"]
__pdoc__ = {
    "AzureKeyVaultEkmipReachabilitySchema.resource": False,
    "AzureKeyVaultEkmipReachabilitySchema.opts": False,
    "AzureKeyVaultEkmipReachability": False,
}


class AzureKeyVaultEkmipReachabilitySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AzureKeyVaultEkmipReachability object"""

    code = marshmallow_fields.Str(data_key="code", allow_none=True)
    r""" Code corresponding to the error message. Returns a 0 if a given SVM is able to communicate to the EKMIP servers of all of the nodes in the cluster.

Example: 346758 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Error message set when cluster-wide EKMIP server availability from the given SVM and node is false.

Example: embedded KMIP server status unavailable on node. """

    node = marshmallow_fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node", allow_none=True)
    r""" The node field of the azure_key_vault_ekmip_reachability. """

    reachable = marshmallow_fields.Boolean(data_key="reachable", allow_none=True)
    r""" Set to true if the given SVM on the given node is able to communicate to all EKMIP servers configured on all nodes in the cluster. """

    @property
    def resource(self):
        return AzureKeyVaultEkmipReachability

    gettable_fields = [
        "code",
        "message",
        "node.links",
        "node.name",
        "node.uuid",
        "reachable",
    ]
    """code,message,node.links,node.name,node.uuid,reachable,"""

    patchable_fields = [
        "code",
        "message",
        "node.name",
        "node.uuid",
        "reachable",
    ]
    """code,message,node.name,node.uuid,reachable,"""

    postable_fields = [
        "code",
        "message",
        "node.name",
        "node.uuid",
        "reachable",
    ]
    """code,message,node.name,node.uuid,reachable,"""


class AzureKeyVaultEkmipReachability(Resource):

    _schema = AzureKeyVaultEkmipReachabilitySchema
