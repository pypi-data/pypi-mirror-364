r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["IscsiSessionInitiator", "IscsiSessionInitiatorSchema"]
__pdoc__ = {
    "IscsiSessionInitiatorSchema.resource": False,
    "IscsiSessionInitiatorSchema.opts": False,
    "IscsiSessionInitiator": False,
}


class IscsiSessionInitiatorSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the IscsiSessionInitiator object"""

    alias = marshmallow_fields.Str(data_key="alias", allow_none=True)
    r""" The initiator alias.


Example: initiator_alias1 """

    comment = marshmallow_fields.Str(data_key="comment", allow_none=True)
    r""" A comment available for use by the administrator. This is modifiable from the initiator REST endpoint directly. See [`PATCH /protocols/san/igroups/{igroup.uuid}/initiators/{name}`](#/SAN/igroup_initiator_modify).


Example: This is an iSCSI initiator for host 5 """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The world wide unique name of the initiator.


Example: iqn.1992-01.example.com:string """

    @property
    def resource(self):
        return IscsiSessionInitiator

    gettable_fields = [
        "alias",
        "comment",
        "name",
    ]
    """alias,comment,name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IscsiSessionInitiator(Resource):

    _schema = IscsiSessionInitiatorSchema
