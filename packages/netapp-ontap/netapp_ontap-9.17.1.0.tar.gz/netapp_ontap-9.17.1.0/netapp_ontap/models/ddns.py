r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Ddns", "DdnsSchema"]
__pdoc__ = {
    "DdnsSchema.resource": False,
    "DdnsSchema.opts": False,
    "Ddns": False,
}


class DdnsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Ddns object"""

    enabled = marshmallow_fields.Boolean(data_key="enabled", allow_none=True)
    r""" Enable or disable Dynamic DNS (DDNS) updates for the specified SVM. """

    fqdn = marshmallow_fields.Str(data_key="fqdn", allow_none=True)
    r""" Fully Qualified Domain Name (FQDN) to be used for dynamic DNS updates.


Example: example.com """

    skip_fqdn_validation = marshmallow_fields.Boolean(data_key="skip_fqdn_validation", allow_none=True)
    r""" Enable or disable FQDN validation. """

    time_to_live = marshmallow_fields.Str(data_key="time_to_live", allow_none=True)
    r""" Time to live value for the dynamic DNS updates, in an ISO-8601 duration formatted string.
Maximum Time To Live is 720 hours(P30D in ISO-8601 format) and the default is 24 hours(P1D in ISO-8601 format).


Example: P2D """

    use_secure = marshmallow_fields.Boolean(data_key="use_secure", allow_none=True)
    r""" Enable or disable secure dynamic DNS updates for the specified SVM. """

    @property
    def resource(self):
        return Ddns

    gettable_fields = [
        "enabled",
        "fqdn",
        "time_to_live",
        "use_secure",
    ]
    """enabled,fqdn,time_to_live,use_secure,"""

    patchable_fields = [
        "enabled",
        "fqdn",
        "skip_fqdn_validation",
        "time_to_live",
        "use_secure",
    ]
    """enabled,fqdn,skip_fqdn_validation,time_to_live,use_secure,"""

    postable_fields = [
        "enabled",
        "fqdn",
        "time_to_live",
        "use_secure",
    ]
    """enabled,fqdn,time_to_live,use_secure,"""


class Ddns(Resource):

    _schema = DdnsSchema
