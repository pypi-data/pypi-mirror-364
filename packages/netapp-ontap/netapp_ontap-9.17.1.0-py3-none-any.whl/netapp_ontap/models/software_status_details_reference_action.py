r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SoftwareStatusDetailsReferenceAction", "SoftwareStatusDetailsReferenceActionSchema"]
__pdoc__ = {
    "SoftwareStatusDetailsReferenceActionSchema.resource": False,
    "SoftwareStatusDetailsReferenceActionSchema.opts": False,
    "SoftwareStatusDetailsReferenceAction": False,
}


class SoftwareStatusDetailsReferenceActionSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SoftwareStatusDetailsReferenceAction object"""

    code = Size(data_key="code", allow_none=True)
    r""" Error code corresponding the status error """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Corrective action to be taken to resolve the status error. """

    @property
    def resource(self):
        return SoftwareStatusDetailsReferenceAction

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    postable_fields = [
        "code",
        "message",
    ]
    """code,message,"""


class SoftwareStatusDetailsReferenceAction(Resource):

    _schema = SoftwareStatusDetailsReferenceActionSchema
