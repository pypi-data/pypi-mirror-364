r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Entitlement", "EntitlementSchema"]
__pdoc__ = {
    "EntitlementSchema.resource": False,
    "EntitlementSchema.opts": False,
    "Entitlement": False,
}


class EntitlementSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Entitlement object"""

    action = marshmallow_fields.Str(data_key="action", allow_none=True)
    r""" Entitlement action to be taken to mitigate the risk

Valid choices:

* acquire_license
* adjust_capacity
* verify_entitlement
* verify_system_health
* none """

    risk = marshmallow_fields.Str(data_key="risk", allow_none=True)
    r""" Entitlement risk of the package

Valid choices:

* high
* medium
* low
* unlicensed
* unknown """

    @property
    def resource(self):
        return Entitlement

    gettable_fields = [
        "action",
        "risk",
    ]
    """action,risk,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Entitlement(Resource):

    _schema = EntitlementSchema
