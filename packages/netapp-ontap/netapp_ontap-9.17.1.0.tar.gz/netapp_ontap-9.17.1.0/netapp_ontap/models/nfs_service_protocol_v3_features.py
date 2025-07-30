r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NfsServiceProtocolV3Features", "NfsServiceProtocolV3FeaturesSchema"]
__pdoc__ = {
    "NfsServiceProtocolV3FeaturesSchema.resource": False,
    "NfsServiceProtocolV3FeaturesSchema.opts": False,
    "NfsServiceProtocolV3Features": False,
}


class NfsServiceProtocolV3FeaturesSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NfsServiceProtocolV3Features object"""

    connection_drop = marshmallow_fields.Boolean(data_key="connection_drop", allow_none=True)
    r""" Specifies whether the dropping of a connection when an NFSv3 request is dropped is enabled. """

    ejukebox_enabled = marshmallow_fields.Boolean(data_key="ejukebox_enabled", allow_none=True)
    r""" Specifies whether NFSv3 EJUKEBOX error is enabled. """

    fsid_change = marshmallow_fields.Boolean(data_key="fsid_change", allow_none=True)
    r""" Specifies whether the change in FSID as NFSv3 clients traverse filesystems should be shown. """

    hide_snapshot_enabled = marshmallow_fields.Boolean(data_key="hide_snapshot_enabled", allow_none=True)
    r""" Specifies whether hiding a snapshot directory under a NFSv3 mount point is enabled. """

    mount_daemon_port = Size(data_key="mount_daemon_port", allow_none=True)
    r""" Specifies which port the NFS mount daemon (mountd) uses. """

    mount_root_only = marshmallow_fields.Boolean(data_key="mount_root_only", allow_none=True)
    r""" Specifies whether the SVM allows MOUNT protocol calls only from privileged ports (port numbers less than 1024). """

    network_lock_manager_port = Size(data_key="network_lock_manager_port", allow_none=True)
    r""" Specifies which port the Network lock manager uses. """

    network_status_monitor_port = Size(data_key="network_status_monitor_port", allow_none=True)
    r""" Specifies which port the Network status monitor port uses. """

    rquota_daemon_port = Size(data_key="rquota_daemon_port", allow_none=True)
    r""" Specifies which port the NFS quota daemon port uses. """

    @property
    def resource(self):
        return NfsServiceProtocolV3Features

    gettable_fields = [
        "connection_drop",
        "ejukebox_enabled",
        "fsid_change",
        "hide_snapshot_enabled",
        "mount_daemon_port",
        "mount_root_only",
        "network_lock_manager_port",
        "network_status_monitor_port",
        "rquota_daemon_port",
    ]
    """connection_drop,ejukebox_enabled,fsid_change,hide_snapshot_enabled,mount_daemon_port,mount_root_only,network_lock_manager_port,network_status_monitor_port,rquota_daemon_port,"""

    patchable_fields = [
        "connection_drop",
        "ejukebox_enabled",
        "fsid_change",
        "hide_snapshot_enabled",
        "mount_daemon_port",
        "mount_root_only",
        "network_lock_manager_port",
        "network_status_monitor_port",
        "rquota_daemon_port",
    ]
    """connection_drop,ejukebox_enabled,fsid_change,hide_snapshot_enabled,mount_daemon_port,mount_root_only,network_lock_manager_port,network_status_monitor_port,rquota_daemon_port,"""

    postable_fields = [
        "connection_drop",
        "ejukebox_enabled",
        "fsid_change",
        "hide_snapshot_enabled",
        "mount_daemon_port",
        "mount_root_only",
        "network_lock_manager_port",
        "network_status_monitor_port",
        "rquota_daemon_port",
    ]
    """connection_drop,ejukebox_enabled,fsid_change,hide_snapshot_enabled,mount_daemon_port,mount_root_only,network_lock_manager_port,network_status_monitor_port,rquota_daemon_port,"""


class NfsServiceProtocolV3Features(Resource):

    _schema = NfsServiceProtocolV3FeaturesSchema
