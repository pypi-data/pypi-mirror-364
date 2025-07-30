r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["Version", "VersionSchema"]
__pdoc__ = {
    "VersionSchema.resource": False,
    "VersionSchema.opts": False,
    "Version": False,
}


class VersionSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Version object"""

    full = marshmallow_fields.Str(data_key="full", allow_none=True)
    r""" The full cluster version string.

Example: NetApp Release 9.4.0: Sun Nov 05 18:20:57 UTC 2017 """

    generation = Size(data_key="generation", allow_none=True)
    r""" The generation portion of the version.

Example: 9 """

    major = Size(data_key="major", allow_none=True)
    r""" The major portion of the version.

Example: 4 """

    minor = Size(data_key="minor", allow_none=True)
    r""" The minor portion of the version.

Example: 0 """

    @property
    def resource(self):
        return Version

    gettable_fields = [
        "full",
        "generation",
        "major",
        "minor",
    ]
    """full,generation,major,minor,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Version(Resource):

    _schema = VersionSchema
