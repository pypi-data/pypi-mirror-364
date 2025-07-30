r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["JobNode", "JobNodeSchema"]
__pdoc__ = {
    "JobNodeSchema.resource": False,
    "JobNodeSchema.opts": False,
    "JobNode": False,
}


class JobNodeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the JobNode object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the node """

    @property
    def resource(self):
        return JobNode

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class JobNode(Resource):

    _schema = JobNodeSchema
