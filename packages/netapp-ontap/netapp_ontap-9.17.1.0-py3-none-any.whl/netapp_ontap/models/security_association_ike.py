r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SecurityAssociationIke", "SecurityAssociationIkeSchema"]
__pdoc__ = {
    "SecurityAssociationIkeSchema.resource": False,
    "SecurityAssociationIkeSchema.opts": False,
    "SecurityAssociationIke": False,
}


class SecurityAssociationIkeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SecurityAssociationIke object"""

    authentication = marshmallow_fields.Str(data_key="authentication", allow_none=True)
    r""" Authentication method for internet key exchange protocol.

Valid choices:

* none
* psk
* cert """

    initiator_security_parameter_index = marshmallow_fields.Str(data_key="initiator_security_parameter_index", allow_none=True)
    r""" Initiator's security parameter index for the IKE security association. """

    is_initiator = marshmallow_fields.Boolean(data_key="is_initiator", allow_none=True)
    r""" Indicates whether or not IKE has been initiated by this node. """

    responder_security_parameter_index = marshmallow_fields.Str(data_key="responder_security_parameter_index", allow_none=True)
    r""" Responder's security parameter index for the IKE security association. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" State of the IKE connection.

Valid choices:

* none
* connecting
* established
* dead_peer_probe """

    version = Size(data_key="version", allow_none=True)
    r""" Internet key exchange protocol version. """

    @property
    def resource(self):
        return SecurityAssociationIke

    gettable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""

    patchable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""

    postable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""


class SecurityAssociationIke(Resource):

    _schema = SecurityAssociationIkeSchema
