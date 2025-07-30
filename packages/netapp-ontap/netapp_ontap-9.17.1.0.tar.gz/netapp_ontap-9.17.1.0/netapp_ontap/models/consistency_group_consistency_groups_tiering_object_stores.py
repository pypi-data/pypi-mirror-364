r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupConsistencyGroupsTieringObjectStores", "ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema"]
__pdoc__ = {
    "ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema.resource": False,
    "ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema.opts": False,
    "ConsistencyGroupConsistencyGroupsTieringObjectStores": False,
}


class ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupConsistencyGroupsTieringObjectStores object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the object store to use. Used for placement. """

    @property
    def resource(self):
        return ConsistencyGroupConsistencyGroupsTieringObjectStores

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class ConsistencyGroupConsistencyGroupsTieringObjectStores(Resource):

    _schema = ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema
