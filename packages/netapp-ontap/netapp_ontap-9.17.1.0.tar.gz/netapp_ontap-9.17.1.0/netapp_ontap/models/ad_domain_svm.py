r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AdDomainSvm", "AdDomainSvmSchema"]
__pdoc__ = {
    "AdDomainSvmSchema.resource": False,
    "AdDomainSvmSchema.opts": False,
    "AdDomainSvm": False,
}


class AdDomainSvmSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AdDomainSvm object"""

    default_site = marshmallow_fields.Str(data_key="default_site", allow_none=True)
    r""" The default site used by LIFs that do not have a site membership. """

    fqdn = marshmallow_fields.Str(data_key="fqdn", allow_none=True)
    r""" The fully qualified domain name of the Windows Active Directory to which this CIFS server belongs. A CIFS server appears as a member of Windows server object in the Active Directory store.


Example: example.com """

    organizational_unit = marshmallow_fields.Str(data_key="organizational_unit", allow_none=True)
    r""" Specifies the organizational unit within the Active Directory domain to associate with the CIFS server. """

    password = marshmallow_fields.Str(data_key="password", allow_none=True)
    r""" The account password used to add this CIFS server to the Active Directory. This is not audited. Valid in POST only. """

    user = marshmallow_fields.Str(data_key="user", allow_none=True)
    r""" The user account used to add this CIFS server to the Active Directory. Valid in POST only. """

    @property
    def resource(self):
        return AdDomainSvm

    gettable_fields = [
        "default_site",
        "fqdn",
        "organizational_unit",
    ]
    """default_site,fqdn,organizational_unit,"""

    patchable_fields = [
        "default_site",
    ]
    """default_site,"""

    postable_fields = [
        "default_site",
        "fqdn",
        "organizational_unit",
        "password",
        "user",
    ]
    """default_site,fqdn,organizational_unit,password,user,"""


class AdDomainSvm(Resource):

    _schema = AdDomainSvmSchema
