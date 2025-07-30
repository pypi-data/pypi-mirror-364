r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NvmeNamespaceQosPolicy", "NvmeNamespaceQosPolicySchema"]
__pdoc__ = {
    "NvmeNamespaceQosPolicySchema.resource": False,
    "NvmeNamespaceQosPolicySchema.opts": False,
    "NvmeNamespaceQosPolicy": False,
}


class NvmeNamespaceQosPolicySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NvmeNamespaceQosPolicy object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the nvme_namespace_qos_policy. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the QoS policy. To remove the QoS policy from an NVMe namespace, leaving it with no QoS policy, set this property to an empty string ("") in a PATCH request. Valid in POST and PATCH.


Example: qos1 """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the QoS policy. Valid in POST and PATCH.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeNamespaceQosPolicy

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class NvmeNamespaceQosPolicy(Resource):

    _schema = NvmeNamespaceQosPolicySchema
