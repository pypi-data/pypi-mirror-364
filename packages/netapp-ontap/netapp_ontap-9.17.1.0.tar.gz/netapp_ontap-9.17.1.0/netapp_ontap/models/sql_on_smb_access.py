r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SqlOnSmbAccess", "SqlOnSmbAccessSchema"]
__pdoc__ = {
    "SqlOnSmbAccessSchema.resource": False,
    "SqlOnSmbAccessSchema.opts": False,
    "SqlOnSmbAccess": False,
}


class SqlOnSmbAccessSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SqlOnSmbAccess object"""

    installer = marshmallow_fields.Str(data_key="installer", allow_none=True)
    r""" SQL installer admin user name. """

    service_account = marshmallow_fields.Str(data_key="service_account", allow_none=True)
    r""" SQL service account user name. """

    @property
    def resource(self):
        return SqlOnSmbAccess

    gettable_fields = [
        "installer",
        "service_account",
    ]
    """installer,service_account,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "installer",
        "service_account",
    ]
    """installer,service_account,"""


class SqlOnSmbAccess(Resource):

    _schema = SqlOnSmbAccessSchema
