r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NasApplicationComponentsFlexcache", "NasApplicationComponentsFlexcacheSchema"]
__pdoc__ = {
    "NasApplicationComponentsFlexcacheSchema.resource": False,
    "NasApplicationComponentsFlexcacheSchema.opts": False,
    "NasApplicationComponentsFlexcache": False,
}


class NasApplicationComponentsFlexcacheSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NasApplicationComponentsFlexcache object"""

    dr_cache = marshmallow_fields.Boolean(data_key="dr_cache", allow_none=True)
    r""" Dr-cache is a FlexCache volume create time option that has the same flexgroup-msid as that of the origin of a FlexCache volume. By default, dr-cache is disabled. The flexgroup-msid of the FlexCache volume does not need to be same as that of the origin of a FlexCache volume. """

    origin = marshmallow_fields.Nested("netapp_ontap.models.nas_application_components_flexcache_origin.NasApplicationComponentsFlexcacheOriginSchema", unknown=EXCLUDE, data_key="origin", allow_none=True)
    r""" The origin field of the nas_application_components_flexcache. """

    @property
    def resource(self):
        return NasApplicationComponentsFlexcache

    gettable_fields = [
        "dr_cache",
        "origin",
    ]
    """dr_cache,origin,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "dr_cache",
        "origin",
    ]
    """dr_cache,origin,"""


class NasApplicationComponentsFlexcache(Resource):

    _schema = NasApplicationComponentsFlexcacheSchema
