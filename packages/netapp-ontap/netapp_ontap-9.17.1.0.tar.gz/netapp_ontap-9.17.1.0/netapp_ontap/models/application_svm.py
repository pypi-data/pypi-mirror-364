r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationSvm", "ApplicationSvmSchema"]
__pdoc__ = {
    "ApplicationSvmSchema.resource": False,
    "ApplicationSvmSchema.opts": False,
    "ApplicationSvm": False,
}


class ApplicationSvmSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationSvm object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" SVM Name. Either the SVM name or UUID must be provided to create an application. """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" SVM UUID. Either the SVM name or UUID must be provided to create an application. """

    @property
    def resource(self):
        return ApplicationSvm

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class ApplicationSvm(Resource):

    _schema = ApplicationSvmSchema
