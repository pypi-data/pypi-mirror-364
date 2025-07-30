r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["EmsEventUpdate", "EmsEventUpdateSchema"]
__pdoc__ = {
    "EmsEventUpdateSchema.resource": False,
    "EmsEventUpdateSchema.opts": False,
    "EmsEventUpdate": False,
}


class EmsEventUpdateSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the EmsEventUpdate object"""

    log_message = marshmallow_fields.Str(data_key="log_message", allow_none=True)
    r""" A formatted text string about the update. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" State of the event instance when the update is raised.

Valid choices:

* opened
* resolving
* resolved
* closed """

    update_time = ImpreciseDateTime(data_key="update_time", allow_none=True)
    r""" Timestamp of the update. """

    @property
    def resource(self):
        return EmsEventUpdate

    gettable_fields = [
        "log_message",
        "state",
        "update_time",
    ]
    """log_message,state,update_time,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class EmsEventUpdate(Resource):

    _schema = EmsEventUpdateSchema
