r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupNas", "ConsistencyGroupNasSchema"]
__pdoc__ = {
    "ConsistencyGroupNasSchema.resource": False,
    "ConsistencyGroupNasSchema.opts": False,
    "ConsistencyGroupNas": False,
}


class ConsistencyGroupNasSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupNas object"""

    cifs = marshmallow_fields.Nested("netapp_ontap.models.consistency_group_consistency_groups_volumes_nas_cifs.ConsistencyGroupConsistencyGroupsVolumesNasCifsSchema", unknown=EXCLUDE, data_key="cifs", allow_none=True)
    r""" The cifs field of the consistency_group_nas. """

    export_policy = marshmallow_fields.Nested("netapp_ontap.models.consistency_group_export_policy.ConsistencyGroupExportPolicySchema", unknown=EXCLUDE, data_key="export_policy", allow_none=True)
    r""" The policy associated with volumes to export them for protocol access. """

    gid = Size(data_key="gid", allow_none=True)
    r""" The UNIX group ID of the volume. Valid in POST or PATCH. """

    junction_parent = marshmallow_fields.Nested("netapp_ontap.models.consistency_group_consistency_groups_volumes_nas_junction_parent.ConsistencyGroupConsistencyGroupsVolumesNasJunctionParentSchema", unknown=EXCLUDE, data_key="junction_parent", allow_none=True)
    r""" The junction_parent field of the consistency_group_nas. """

    path = marshmallow_fields.Str(data_key="path", allow_none=True)
    r""" The fully-qualified path in the owning SVM's namespace at which the volume is mounted. The path is case insensitive and must be unique within an SVM's namespace. Path must begin with '/' and must not end with '/'. Only one volume can be mounted at any given junction path. An empty path in POST creates an unmounted volume. An empty path in PATCH deactivates and unmounts the volume. Taking a volume offline or restricted state removes its junction path. This attribute is reported in GET only when the volume is mounted.

Example: /user/my_volume """

    security_style = marshmallow_fields.Str(data_key="security_style", allow_none=True)
    r""" Security style associated with the volume. Valid in POST or PATCH.<br>mixed &dash; Mixed-style security<br>ntfs &dash; NTFS/WIndows-style security<br>unified &dash; Unified-style security, unified UNIX, NFS and CIFS permissions<br>unix &dash; UNIX-style security.

Valid choices:

* mixed
* ntfs
* unified
* unix """

    uid = Size(data_key="uid", allow_none=True)
    r""" The UNIX user ID of the volume. Valid in POST or PATCH. """

    unix_permissions = Size(data_key="unix_permissions", allow_none=True)
    r""" UNIX permissions to be viewed as an octal number, consisting of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). First digit selects the set user ID (4), set group ID (2), and sticky (1) attributes. Second digit selects permission for the owner of the file. Third selects permissions for other users in the same group while the fourth selects permissions for other users not in the group. Valid in POST or PATCH. For security style "mixed" or "unix", the default setting is 0755 in octal (493 in decimal) and for security style "ntfs", the default setting is 0000. In cases where only owner, group, and other permissions are given (as in 755, representing the second, third and fourth digit), the first digit is assumed to be zero.

Example: 493 """

    @property
    def resource(self):
        return ConsistencyGroupNas

    gettable_fields = [
        "cifs",
        "export_policy",
        "gid",
        "junction_parent",
        "path",
        "security_style",
        "uid",
        "unix_permissions",
    ]
    """cifs,export_policy,gid,junction_parent,path,security_style,uid,unix_permissions,"""

    patchable_fields = [
        "cifs",
        "export_policy",
    ]
    """cifs,export_policy,"""

    postable_fields = [
        "cifs",
        "export_policy",
        "gid",
        "junction_parent",
        "path",
        "security_style",
        "uid",
        "unix_permissions",
    ]
    """cifs,export_policy,gid,junction_parent,path,security_style,uid,unix_permissions,"""


class ConsistencyGroupNas(Resource):

    _schema = ConsistencyGroupNasSchema
