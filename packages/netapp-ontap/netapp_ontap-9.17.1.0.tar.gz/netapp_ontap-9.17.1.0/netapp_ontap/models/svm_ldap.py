r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SvmLdap", "SvmLdapSchema"]
__pdoc__ = {
    "SvmLdapSchema.resource": False,
    "SvmLdapSchema.opts": False,
    "SvmLdap": False,
}


class SvmLdapSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SvmLdap object"""

    ad_domain = marshmallow_fields.Str(data_key="ad_domain", allow_none=True)
    r""" This parameter specifies the name of the Active Directory domain
used to discover LDAP servers for use by this client.
This is mutually exclusive with `servers` during POST. """

    base_dn = marshmallow_fields.Str(data_key="base_dn", allow_none=True)
    r""" Specifies the default base DN for all searches. """

    bind_dn = marshmallow_fields.Str(data_key="bind_dn", allow_none=True)
    r""" Specifies the user that binds to the LDAP servers. SVM API supports anonymous binding. For Simple and SASL LDAP binding, use the LDAP API endpoint. """

    enabled = marshmallow_fields.Boolean(data_key="enabled", allow_none=True)
    r""" Enable LDAP? Setting to true creates a configuration if not already created. """

    restrict_discovery_to_site = marshmallow_fields.Boolean(data_key="restrict_discovery_to_site", allow_none=True)
    r""" Specifies whether or not LDAP server discovery is restricted to site-scope. """

    servers = marshmallow_fields.List(marshmallow_fields.Str, data_key="servers", allow_none=True)
    r""" The servers field of the svm_ldap. """

    @property
    def resource(self):
        return SvmLdap

    gettable_fields = [
        "ad_domain",
        "base_dn",
        "bind_dn",
        "enabled",
        "restrict_discovery_to_site",
        "servers",
    ]
    """ad_domain,base_dn,bind_dn,enabled,restrict_discovery_to_site,servers,"""

    patchable_fields = [
        "ad_domain",
        "base_dn",
        "bind_dn",
        "enabled",
        "restrict_discovery_to_site",
        "servers",
    ]
    """ad_domain,base_dn,bind_dn,enabled,restrict_discovery_to_site,servers,"""

    postable_fields = [
        "ad_domain",
        "base_dn",
        "bind_dn",
        "enabled",
        "restrict_discovery_to_site",
        "servers",
    ]
    """ad_domain,base_dn,bind_dn,enabled,restrict_discovery_to_site,servers,"""


class SvmLdap(Resource):

    _schema = SvmLdapSchema
