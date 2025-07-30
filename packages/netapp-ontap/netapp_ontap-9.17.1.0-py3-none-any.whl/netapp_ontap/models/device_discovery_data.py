r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["DeviceDiscoveryData", "DeviceDiscoveryDataSchema"]
__pdoc__ = {
    "DeviceDiscoveryDataSchema.resource": False,
    "DeviceDiscoveryDataSchema.opts": False,
    "DeviceDiscoveryData": False,
}


class DeviceDiscoveryDataSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the DeviceDiscoveryData object"""

    capabilities = marshmallow_fields.List(marshmallow_fields.Str, data_key="capabilities", allow_none=True)
    r""" The list of the capabilities of the discovered device. """

    chassis_id = marshmallow_fields.Str(data_key="chassis_id", allow_none=True)
    r""" Identifier associated with this specific discovered device, useful for locating the device in a data center. """

    ip_addresses = marshmallow_fields.List(marshmallow_fields.Str, data_key="ip_addresses", allow_none=True)
    r""" The IP addresses on the discovered device.

Example: ["192.168.100.24","192.168.100.26"] """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Name of the discovered device.

Example: ETY-R1S4-510Q13.datacenter.example.com """

    platform = marshmallow_fields.Str(data_key="platform", allow_none=True)
    r""" Hardware platform of the discovered device.

Example: 93180YC-EX """

    protocol = marshmallow_fields.Str(data_key="protocol", allow_none=True)
    r""" The protocol used to identify the discovered device. This can have a value of CDP or LLDP.

Valid choices:

* cdp
* lldp """

    remaining_hold_time = Size(data_key="remaining_hold_time", allow_none=True)
    r""" The number of seconds until the discovered device entry expires and is removed. """

    remote_port = marshmallow_fields.Str(data_key="remote_port", allow_none=True)
    r""" The name of the remote port on the discovered device. The format is dependent on the reporting device.

Example: FastEthernet0/12 """

    system_name = marshmallow_fields.Str(data_key="system_name", allow_none=True)
    r""" Additional name used to identify a specific piece of equipment. """

    version = marshmallow_fields.Str(data_key="version", allow_none=True)
    r""" The version of the software running on the discovered device.

Example: Cisco Nexus Operating System (NX-OS) Software, Version 8.1 """

    @property
    def resource(self):
        return DeviceDiscoveryData

    gettable_fields = [
        "capabilities",
        "chassis_id",
        "ip_addresses",
        "name",
        "platform",
        "protocol",
        "remaining_hold_time",
        "remote_port",
        "system_name",
        "version",
    ]
    """capabilities,chassis_id,ip_addresses,name,platform,protocol,remaining_hold_time,remote_port,system_name,version,"""

    patchable_fields = [
        "capabilities",
        "chassis_id",
        "ip_addresses",
        "name",
        "platform",
        "protocol",
        "remaining_hold_time",
        "remote_port",
        "system_name",
        "version",
    ]
    """capabilities,chassis_id,ip_addresses,name,platform,protocol,remaining_hold_time,remote_port,system_name,version,"""

    postable_fields = [
        "capabilities",
        "chassis_id",
        "ip_addresses",
        "name",
        "platform",
        "protocol",
        "remaining_hold_time",
        "remote_port",
        "system_name",
        "version",
    ]
    """capabilities,chassis_id,ip_addresses,name,platform,protocol,remaining_hold_time,remote_port,system_name,version,"""


class DeviceDiscoveryData(Resource):

    _schema = DeviceDiscoveryDataSchema
