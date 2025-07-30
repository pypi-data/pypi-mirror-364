r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["CifsDomainPreferredDcStatus", "CifsDomainPreferredDcStatusSchema"]
__pdoc__ = {
    "CifsDomainPreferredDcStatusSchema.resource": False,
    "CifsDomainPreferredDcStatusSchema.opts": False,
    "CifsDomainPreferredDcStatus": False,
}


class CifsDomainPreferredDcStatusSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the CifsDomainPreferredDcStatus object"""

    details = marshmallow_fields.Str(data_key="details", allow_none=True)
    r""" Provides a detailed description of the state if the state is 'down' or
the response time of the DNS server if the state is 'up'.


Example: Response time (msec): 111 """

    reachable = marshmallow_fields.Boolean(data_key="reachable", allow_none=True)
    r""" Indicates whether or not the domain controller is reachable.

Example: true """

    @property
    def resource(self):
        return CifsDomainPreferredDcStatus

    gettable_fields = [
        "details",
        "reachable",
    ]
    """details,reachable,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class CifsDomainPreferredDcStatus(Resource):

    _schema = CifsDomainPreferredDcStatusSchema
