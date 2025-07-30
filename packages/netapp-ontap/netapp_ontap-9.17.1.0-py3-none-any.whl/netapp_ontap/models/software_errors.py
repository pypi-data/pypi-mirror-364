r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SoftwareErrors", "SoftwareErrorsSchema"]
__pdoc__ = {
    "SoftwareErrorsSchema.resource": False,
    "SoftwareErrorsSchema.opts": False,
    "SoftwareErrors": False,
}


class SoftwareErrorsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SoftwareErrors object"""

    code = Size(data_key="code", allow_none=True)
    r""" Error code of message

Example: 177 """

    message = marshmallow_fields.Str(data_key="message", allow_none=True)
    r""" Error message

Example: Giveback of aggregate is vetoed. Action: Use the "storage failover show-giveback" command to view detailed veto status information. Correct the vetoed update check. Use the "storage failover giveback -ofnode "node1" command to complete the giveback. """

    severity = marshmallow_fields.Str(data_key="severity", allow_none=True)
    r""" Severity of error

Valid choices:

* informational
* warning
* error """

    @property
    def resource(self):
        return SoftwareErrors

    gettable_fields = [
        "code",
        "message",
        "severity",
    ]
    """code,message,severity,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwareErrors(Resource):

    _schema = SoftwareErrorsSchema
