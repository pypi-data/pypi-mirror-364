r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FcLoginInitiator", "FcLoginInitiatorSchema"]
__pdoc__ = {
    "FcLoginInitiatorSchema.resource": False,
    "FcLoginInitiatorSchema.opts": False,
    "FcLoginInitiator": False,
}


class FcLoginInitiatorSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FcLoginInitiator object"""

    aliases = marshmallow_fields.List(marshmallow_fields.Str, data_key="aliases", allow_none=True)
    r""" The logged in initiator world wide port name (WWPN) aliases. """

    comment = marshmallow_fields.Str(data_key="comment", allow_none=True)
    r""" A comment available for use by the administrator. This is modifiable from the initiator REST endpoint directly. See [`PATCH /protocols/san/igroups/{igroup.uuid}/initiators/{name}`](#/SAN/igroup_initiator_modify).


Example: This is an FC initiator for host 5 """

    port_address = marshmallow_fields.Str(data_key="port_address", allow_none=True)
    r""" The port address of the initiator's FC port.<br/>
Each port in an FC switched fabric has its own unique port address for routing purposes. The port address is assigned by a switch in the fabric when that port logs in to the fabric. This property refers to the address given by a switch to the initiator port.<br/>
This is useful for obtaining statistics and diagnostic information from FC switches.<br/>
This is a hexadecimal encoded numeric value.


Example: 5060A """

    wwnn = marshmallow_fields.Str(data_key="wwnn", allow_none=True)
    r""" The logged in initiator world wide node name (WWNN).


Example: 2f:a0:00:a0:98:0b:56:13 """

    wwpn = marshmallow_fields.Str(data_key="wwpn", allow_none=True)
    r""" The logged in initiator WWPN.


Example: 2f:a0:00:a0:98:0b:56:13 """

    @property
    def resource(self):
        return FcLoginInitiator

    gettable_fields = [
        "aliases",
        "comment",
        "port_address",
        "wwnn",
        "wwpn",
    ]
    """aliases,comment,port_address,wwnn,wwpn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FcLoginInitiator(Resource):

    _schema = FcLoginInitiatorSchema
