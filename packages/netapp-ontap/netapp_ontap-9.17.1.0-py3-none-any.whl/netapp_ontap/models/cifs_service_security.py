r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["CifsServiceSecurity", "CifsServiceSecuritySchema"]
__pdoc__ = {
    "CifsServiceSecuritySchema.resource": False,
    "CifsServiceSecuritySchema.opts": False,
    "CifsServiceSecurity": False,
}


class CifsServiceSecuritySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the CifsServiceSecurity object"""

    advertised_kdc_encryptions = marshmallow_fields.List(marshmallow_fields.Str, data_key="advertised_kdc_encryptions", allow_none=True)
    r""" The advertised_kdc_encryptions field of the cifs_service_security. """

    aes_netlogon_enabled = marshmallow_fields.Boolean(data_key="aes_netlogon_enabled", allow_none=True)
    r""" Specifies whether or not an AES session key is enabled for the Netlogon channel. """

    encrypt_dc_connection = marshmallow_fields.Boolean(data_key="encrypt_dc_connection", allow_none=True)
    r""" Specifies whether encryption is required for domain controller connections. """

    kdc_encryption = marshmallow_fields.Boolean(data_key="kdc_encryption", allow_none=True)
    r""" Important: This attribute has been deprecated. Use "security.advertised_kdc_encryptions" to specify the encryption type to use.
Specifies whether AES-128 and AES-256 encryption is enabled for all Kerberos-based communication with the Active Directory KDC.
To take advantage of the strongest security with Kerberos-based communication, AES-256 and AES-128 encryption can be enabled on the CIFS server.
Kerberos-related communication for CIFS is used during CIFS server creation on the SVM, as well
as during the SMB session setup phase.
The CIFS server supports the following encryption types for Kerberos communication:

    * RC4-HMAC
    * DES
    * AES
When the CIFS server is created, the domain controller creates a computer machine account in
Active Directory. After a newly created machine account authenticates, the KDC and the CIFS server
negotiates encryption types. At this time, the KDC becomes aware of the encryption capabilities of
the particular machine account and uses those capabilities in subsequent communication with the
CIFS server.
In addition to negotiating encryption types during CIFS server creation, the encryption types are
renegotiated when a machine account password is reset. """

    ldap_referral_enabled = marshmallow_fields.Boolean(data_key="ldap_referral_enabled", allow_none=True)
    r""" Specifies whether or not LDAP referral chasing is enabled for AD LDAP connections. """

    lm_compatibility_level = marshmallow_fields.Str(data_key="lm_compatibility_level", allow_none=True)
    r""" It is CIFS server minimum security level, also known as the LMCompatibilityLevel. The minimum security level is the minimum level of the security tokens that        the CIFS server accepts from SMB clients.
The available values are:

* lm_ntlm_ntlmv2_krb          Accepts LM, NTLM, NTLMv2 and Kerberos
* ntlm_ntlmv2_krb             Accepts NTLM, NTLMv2 and Kerberos
* ntlmv2_krb                  Accepts NTLMv2 and Kerberos
* krb                         Accepts Kerberos only


Valid choices:

* lm_ntlm_ntlmv2_krb
* ntlm_ntlmv2_krb
* ntlmv2_krb
* krb """

    restrict_anonymous = marshmallow_fields.Str(data_key="restrict_anonymous", allow_none=True)
    r""" Specifies what level of access an anonymous user is granted. An anonymous user (also known as a "null user") can list or enumerate certain types of system information from Windows hosts on the network, including user names and details, account policies, and share names. Access for the anonymous user can be controlled by specifying one of three access restriction settings.
 The available values are:

 * no_restriction   - No access restriction for an anonymous user.
 * no_enumeration   - Enumeration is restricted for an anonymous user.
 * no_access        - All access is restricted for an anonymous user.


Valid choices:

* no_restriction
* no_enumeration
* no_access """

    session_security = marshmallow_fields.Str(data_key="session_security", allow_none=True)
    r""" Specifies client session security for AD LDAP connections.
The available values are:

  * none - No Signing or Sealing.
  * sign - Sign LDAP traffic.
  * seal - Seal and Sign LDAP traffic


Valid choices:

* none
* sign
* seal """

    smb_encryption = marshmallow_fields.Boolean(data_key="smb_encryption", allow_none=True)
    r""" Specifies whether encryption is required for incoming CIFS traffic. """

    smb_signing = marshmallow_fields.Boolean(data_key="smb_signing", allow_none=True)
    r""" Specifies whether signing is required for incoming CIFS traffic. SMB signing helps to ensure that network traffic between the CIFS server and the client is not compromised. """

    try_ldap_channel_binding = marshmallow_fields.Boolean(data_key="try_ldap_channel_binding", allow_none=True)
    r""" Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. """

    use_ldaps = marshmallow_fields.Boolean(data_key="use_ldaps", allow_none=True)
    r""" Specifies whether or not to use use LDAPS for secure Active Directory LDAP connections
by using the TLS/SSL protocols. """

    use_start_tls = marshmallow_fields.Boolean(data_key="use_start_tls", allow_none=True)
    r""" Specifies whether or not to use SSL/TLS for allowing secure LDAP communication with
Active Directory LDAP servers. """

    @property
    def resource(self):
        return CifsServiceSecurity

    gettable_fields = [
        "advertised_kdc_encryptions",
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "lm_compatibility_level",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """advertised_kdc_encryptions,aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,lm_compatibility_level,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""

    patchable_fields = [
        "advertised_kdc_encryptions",
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "lm_compatibility_level",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """advertised_kdc_encryptions,aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,lm_compatibility_level,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""

    postable_fields = [
        "advertised_kdc_encryptions",
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """advertised_kdc_encryptions,aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""


class CifsServiceSecurity(Resource):

    _schema = CifsServiceSecuritySchema
