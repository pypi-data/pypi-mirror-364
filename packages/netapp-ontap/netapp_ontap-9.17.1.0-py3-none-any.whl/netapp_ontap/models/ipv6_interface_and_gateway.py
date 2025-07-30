r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Ipv6InterfaceAndGateway", "Ipv6InterfaceAndGatewaySchema"]
__pdoc__ = {
    "Ipv6InterfaceAndGatewaySchema.resource": False,
    "Ipv6InterfaceAndGatewaySchema.opts": False,
    "Ipv6InterfaceAndGateway": False,
}


class Ipv6InterfaceAndGatewaySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Ipv6InterfaceAndGateway object"""

    address = marshmallow_fields.Str(data_key="address", allow_none=True)
    r""" IPv6 address

Example: fd20:8b1e:b255:5011:10:141:4:97 """

    gateway = marshmallow_fields.Str(data_key="gateway", allow_none=True)
    r""" The IPv6 address of the default router.

Example: fd20:8b1e:b255:5011:10::1 """

    netmask = Size(data_key="netmask", allow_none=True)
    r""" The IPv6 netmask/prefix length. The default value is 64 with a valid range of 1 to 127.

Example: 64 """

    @property
    def resource(self):
        return Ipv6InterfaceAndGateway

    gettable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""

    patchable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""

    postable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""


class Ipv6InterfaceAndGateway(Resource):

    _schema = Ipv6InterfaceAndGatewaySchema
