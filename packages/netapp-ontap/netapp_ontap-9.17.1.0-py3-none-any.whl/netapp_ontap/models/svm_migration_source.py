r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SvmMigrationSource", "SvmMigrationSourceSchema"]
__pdoc__ = {
    "SvmMigrationSourceSchema.resource": False,
    "SvmMigrationSourceSchema.opts": False,
    "SvmMigrationSource": False,
}


class SvmMigrationSourceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SvmMigrationSource object"""

    cluster = marshmallow_fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", unknown=EXCLUDE, data_key="cluster", allow_none=True)
    r""" The cluster field of the svm_migration_source. """

    svm = marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm", allow_none=True)
    r""" The svm field of the svm_migration_source. """

    @property
    def resource(self):
        return SvmMigrationSource

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.links,cluster.name,cluster.uuid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.name,cluster.uuid,svm.name,svm.uuid,"""


class SvmMigrationSource(Resource):

    _schema = SvmMigrationSourceSchema
