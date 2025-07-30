r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["IgroupInitiatorsLinks", "IgroupInitiatorsLinksSchema"]
__pdoc__ = {
    "IgroupInitiatorsLinksSchema.resource": False,
    "IgroupInitiatorsLinksSchema.opts": False,
    "IgroupInitiatorsLinks": False,
}


class IgroupInitiatorsLinksSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the IgroupInitiatorsLinks object"""

    connectivity_tracking = marshmallow_fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="connectivity_tracking", allow_none=True)
    r""" The connectivity_tracking field of the igroup_initiators_links. """

    self_ = marshmallow_fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self", allow_none=True)
    r""" The self_ field of the igroup_initiators_links. """

    @property
    def resource(self):
        return IgroupInitiatorsLinks

    gettable_fields = [
        "connectivity_tracking",
        "self_",
    ]
    """connectivity_tracking,self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IgroupInitiatorsLinks(Resource):

    _schema = IgroupInitiatorsLinksSchema
