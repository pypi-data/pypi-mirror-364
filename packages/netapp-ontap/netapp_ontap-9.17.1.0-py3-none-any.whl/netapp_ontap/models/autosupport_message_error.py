r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AutosupportMessageError", "AutosupportMessageErrorSchema"]
__pdoc__ = {
    "AutosupportMessageErrorSchema.resource": False,
    "AutosupportMessageErrorSchema.opts": False,
    "AutosupportMessageError": False,
}


class AutosupportMessageErrorSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AutosupportMessageError object"""

    code = Size(data_key="code", allow_none=True)
    r""" Error code

Example: 53149746 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Error message

Example: Could not resolve host: test.com """

    @property
    def resource(self):
        return AutosupportMessageError

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AutosupportMessageError(Resource):

    _schema = AutosupportMessageErrorSchema
