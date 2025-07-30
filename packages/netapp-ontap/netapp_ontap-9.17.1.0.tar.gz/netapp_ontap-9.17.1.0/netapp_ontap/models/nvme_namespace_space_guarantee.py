r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NvmeNamespaceSpaceGuarantee", "NvmeNamespaceSpaceGuaranteeSchema"]
__pdoc__ = {
    "NvmeNamespaceSpaceGuaranteeSchema.resource": False,
    "NvmeNamespaceSpaceGuaranteeSchema.opts": False,
    "NvmeNamespaceSpaceGuarantee": False,
}


class NvmeNamespaceSpaceGuaranteeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NvmeNamespaceSpaceGuarantee object"""

    requested = marshmallow_fields.Boolean(data_key="requested", allow_none=True)
    r""" The requested space reservation policy for the NVMe namespace. If _true_, a space reservation is requested for the namespace; if _false_, the namespace is thin provisioned. Guaranteeing a space reservation request for a namespace requires that the volume in which the namespace resides also be space reserved and that the fractional reserve for the volume be 100%.<br/>
The space reservation policy for an NVMe namespace is determined by ONTAP. """

    reserved = marshmallow_fields.Boolean(data_key="reserved", allow_none=True)
    r""" Reports if the NVMe namespace is space guaranteed.<br/>
This property is _true_ if a space guarantee is requested and the containing volume and aggregate support the request. This property is _false_ if a space guarantee is not requested or if a space guarantee is requested and either the containing volume and aggregate do not support the request. """

    @property
    def resource(self):
        return NvmeNamespaceSpaceGuarantee

    gettable_fields = [
        "requested",
        "reserved",
    ]
    """requested,reserved,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeNamespaceSpaceGuarantee(Resource):

    _schema = NvmeNamespaceSpaceGuaranteeSchema
