r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["OracleOnSan", "OracleOnSanSchema"]
__pdoc__ = {
    "OracleOnSanSchema.resource": False,
    "OracleOnSanSchema.opts": False,
    "OracleOnSan": False,
}


class OracleOnSanSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the OracleOnSan object"""

    archive_log = marshmallow_fields.Nested("netapp_ontap.models.oracle_on_nfs_archive_log.OracleOnNfsArchiveLogSchema", unknown=EXCLUDE, data_key="archive_log", allow_none=True)
    r""" The archive_log field of the oracle_on_san. """

    db = marshmallow_fields.Nested("netapp_ontap.models.oracle_on_nfs_db.OracleOnNfsDbSchema", unknown=EXCLUDE, data_key="db", allow_none=True)
    r""" The db field of the oracle_on_san. """

    igroup_name = marshmallow_fields.Str(data_key="igroup_name", allow_none=True)
    r""" The name of the initiator group through which the contents of this application will be accessed. Modification of this parameter is a disruptive operation. All LUNs in the application component will be unmapped from the current igroup and re-mapped to the new igroup. """

    new_igroups = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.oracle_on_san_new_igroups.OracleOnSanNewIgroupsSchema", unknown=EXCLUDE, allow_none=True), data_key="new_igroups", allow_none=True)
    r""" The list of initiator groups to create. """

    ora_home = marshmallow_fields.Nested("netapp_ontap.models.oracle_on_nfs_ora_home.OracleOnNfsOraHomeSchema", unknown=EXCLUDE, data_key="ora_home", allow_none=True)
    r""" The ora_home field of the oracle_on_san. """

    os_type = marshmallow_fields.Str(data_key="os_type", allow_none=True)
    r""" The name of the host OS running the application.

Valid choices:

* aix
* hpux
* hyper_v
* linux
* solaris
* solaris_efi
* vmware
* windows
* windows_2008
* windows_gpt
* xen """

    protection_type = marshmallow_fields.Nested("netapp_ontap.models.mongo_db_on_san_protection_type.MongoDbOnSanProtectionTypeSchema", unknown=EXCLUDE, data_key="protection_type", allow_none=True)
    r""" The protection_type field of the oracle_on_san. """

    redo_log = marshmallow_fields.Nested("netapp_ontap.models.oracle_on_nfs_redo_log.OracleOnNfsRedoLogSchema", unknown=EXCLUDE, data_key="redo_log", allow_none=True)
    r""" The redo_log field of the oracle_on_san. """

    @property
    def resource(self):
        return OracleOnSan

    gettable_fields = [
        "archive_log",
        "db",
        "igroup_name",
        "ora_home",
        "os_type",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,igroup_name,ora_home,os_type,protection_type,redo_log,"""

    patchable_fields = [
        "archive_log",
        "db",
        "igroup_name",
        "new_igroups",
        "ora_home",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,igroup_name,new_igroups,ora_home,protection_type,redo_log,"""

    postable_fields = [
        "archive_log",
        "db",
        "igroup_name",
        "new_igroups",
        "ora_home",
        "os_type",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,igroup_name,new_igroups,ora_home,os_type,protection_type,redo_log,"""


class OracleOnSan(Resource):

    _schema = OracleOnSanSchema
