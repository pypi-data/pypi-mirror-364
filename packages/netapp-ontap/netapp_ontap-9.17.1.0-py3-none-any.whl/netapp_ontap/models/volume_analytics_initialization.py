r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeAnalyticsInitialization", "VolumeAnalyticsInitializationSchema"]
__pdoc__ = {
    "VolumeAnalyticsInitializationSchema.resource": False,
    "VolumeAnalyticsInitializationSchema.opts": False,
    "VolumeAnalyticsInitialization": False,
}


class VolumeAnalyticsInitializationSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeAnalyticsInitialization object"""

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" State of the analytics file system scan.

Valid choices:

* running
* paused """

    @property
    def resource(self):
        return VolumeAnalyticsInitialization

    gettable_fields = [
        "state",
    ]
    """state,"""

    patchable_fields = [
        "state",
    ]
    """state,"""

    postable_fields = [
        "state",
    ]
    """state,"""


class VolumeAnalyticsInitialization(Resource):

    _schema = VolumeAnalyticsInitializationSchema
