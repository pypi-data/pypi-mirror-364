r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AggregateDataEncryption", "AggregateDataEncryptionSchema"]
__pdoc__ = {
    "AggregateDataEncryptionSchema.resource": False,
    "AggregateDataEncryptionSchema.opts": False,
    "AggregateDataEncryption": False,
}


class AggregateDataEncryptionSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AggregateDataEncryption object"""

    drive_protection_enabled = marshmallow_fields.Boolean(data_key="drive_protection_enabled", allow_none=True)
    r""" Specifies whether the aggregate uses self-encrypting drives with data protection enabled. """

    software_encryption_enabled = marshmallow_fields.Boolean(data_key="software_encryption_enabled", allow_none=True)
    r""" Specifies whether NetApp aggregate encryption is enabled. All data in the aggregate is encrypted. """

    @property
    def resource(self):
        return AggregateDataEncryption

    gettable_fields = [
        "drive_protection_enabled",
        "software_encryption_enabled",
    ]
    """drive_protection_enabled,software_encryption_enabled,"""

    patchable_fields = [
        "software_encryption_enabled",
    ]
    """software_encryption_enabled,"""

    postable_fields = [
        "software_encryption_enabled",
    ]
    """software_encryption_enabled,"""


class AggregateDataEncryption(Resource):

    _schema = AggregateDataEncryptionSchema
