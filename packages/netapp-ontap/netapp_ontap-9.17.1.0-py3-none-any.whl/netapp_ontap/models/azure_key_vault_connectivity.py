r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AzureKeyVaultConnectivity", "AzureKeyVaultConnectivitySchema"]
__pdoc__ = {
    "AzureKeyVaultConnectivitySchema.resource": False,
    "AzureKeyVaultConnectivitySchema.opts": False,
    "AzureKeyVaultConnectivity": False,
}


class AzureKeyVaultConnectivitySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AzureKeyVaultConnectivity object"""

    code = marshmallow_fields.Str(data_key="code", allow_none=True)
    r""" Code corresponding to the status message. Returns a 0 if AKV service is reachable from all nodes in the cluster.

Example: 346758 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Error message set when reachability is false.

Example: AKV service is not reachable from all nodes - reason. """

    reachable = marshmallow_fields.Boolean(data_key="reachable", allow_none=True)
    r""" Set to true when the AKV service is reachable from all nodes of the cluster. """

    @property
    def resource(self):
        return AzureKeyVaultConnectivity

    gettable_fields = [
        "code",
        "message",
        "reachable",
    ]
    """code,message,reachable,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AzureKeyVaultConnectivity(Resource):

    _schema = AzureKeyVaultConnectivitySchema
