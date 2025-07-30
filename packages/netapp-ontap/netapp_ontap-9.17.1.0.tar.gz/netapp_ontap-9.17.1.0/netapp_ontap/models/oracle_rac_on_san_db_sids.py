r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["OracleRacOnSanDbSids", "OracleRacOnSanDbSidsSchema"]
__pdoc__ = {
    "OracleRacOnSanDbSidsSchema.resource": False,
    "OracleRacOnSanDbSidsSchema.opts": False,
    "OracleRacOnSanDbSids": False,
}


class OracleRacOnSanDbSidsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the OracleRacOnSanDbSids object"""

    igroup_name = marshmallow_fields.Str(data_key="igroup_name", allow_none=True)
    r""" The name of the initiator group through which the contents of this application will be accessed. Modification of this parameter is a disruptive operation. All LUNs in the application component will be unmapped from the current igroup and re-mapped to the new igroup. """

    @property
    def resource(self):
        return OracleRacOnSanDbSids

    gettable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""

    patchable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""

    postable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""


class OracleRacOnSanDbSids(Resource):

    _schema = OracleRacOnSanDbSidsSchema
