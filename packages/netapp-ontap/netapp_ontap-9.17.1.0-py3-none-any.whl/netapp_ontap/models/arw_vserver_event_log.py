r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ArwVserverEventLog", "ArwVserverEventLogSchema"]
__pdoc__ = {
    "ArwVserverEventLogSchema.resource": False,
    "ArwVserverEventLogSchema.opts": False,
    "ArwVserverEventLog": False,
}


class ArwVserverEventLogSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ArwVserverEventLog object"""

    is_enabled_on_new_file_extension_seen = marshmallow_fields.Boolean(data_key="is_enabled_on_new_file_extension_seen", allow_none=True)
    r""" Specifies whether to send an EMS when a new file extension is discovered. """

    is_enabled_on_snapshot_copy_creation = marshmallow_fields.Boolean(data_key="is_enabled_on_snapshot_copy_creation", allow_none=True)
    r""" Specifies whether to send an EMS when a snapshot is created. """

    @property
    def resource(self):
        return ArwVserverEventLog

    gettable_fields = [
        "is_enabled_on_new_file_extension_seen",
        "is_enabled_on_snapshot_copy_creation",
    ]
    """is_enabled_on_new_file_extension_seen,is_enabled_on_snapshot_copy_creation,"""

    patchable_fields = [
        "is_enabled_on_new_file_extension_seen",
        "is_enabled_on_snapshot_copy_creation",
    ]
    """is_enabled_on_new_file_extension_seen,is_enabled_on_snapshot_copy_creation,"""

    postable_fields = [
        "is_enabled_on_new_file_extension_seen",
        "is_enabled_on_snapshot_copy_creation",
    ]
    """is_enabled_on_new_file_extension_seen,is_enabled_on_snapshot_copy_creation,"""


class ArwVserverEventLog(Resource):

    _schema = ArwVserverEventLogSchema
