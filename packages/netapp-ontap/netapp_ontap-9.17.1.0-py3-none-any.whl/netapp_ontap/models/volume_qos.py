r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeQos", "VolumeQosSchema"]
__pdoc__ = {
    "VolumeQosSchema.resource": False,
    "VolumeQosSchema.opts": False,
    "VolumeQos": False,
}


class VolumeQosSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeQos object"""

    policy = marshmallow_fields.Nested("netapp_ontap.resources.qos_policy.QosPolicySchema", unknown=EXCLUDE, data_key="policy", allow_none=True)
    r""" The policy field of the volume_qos. """

    @property
    def resource(self):
        return VolumeQos

    gettable_fields = [
        "policy.links",
        "policy.max_throughput",
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.links,policy.max_throughput,policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""

    patchable_fields = [
        "policy.max_throughput",
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.max_throughput,policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""

    postable_fields = [
        "policy.max_throughput",
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.max_throughput,policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""


class VolumeQos(Resource):

    _schema = VolumeQosSchema
