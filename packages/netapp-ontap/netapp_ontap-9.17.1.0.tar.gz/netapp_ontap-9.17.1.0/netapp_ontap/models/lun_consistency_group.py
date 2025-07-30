r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["LunConsistencyGroup", "LunConsistencyGroupSchema"]
__pdoc__ = {
    "LunConsistencyGroupSchema.resource": False,
    "LunConsistencyGroupSchema.opts": False,
    "LunConsistencyGroup": False,
}


class LunConsistencyGroupSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the LunConsistencyGroup object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the lun_consistency_group. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the consistency group.


Example: cg1 """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the consistency group.


Example: 4abc2317-4332-9d37-93a0-20bd29c22df0 """

    @property
    def resource(self):
        return LunConsistencyGroup

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunConsistencyGroup(Resource):

    _schema = LunConsistencyGroupSchema
