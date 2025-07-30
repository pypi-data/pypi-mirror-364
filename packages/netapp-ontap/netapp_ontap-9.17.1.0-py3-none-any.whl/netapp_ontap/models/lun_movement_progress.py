r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["LunMovementProgress", "LunMovementProgressSchema"]
__pdoc__ = {
    "LunMovementProgressSchema.resource": False,
    "LunMovementProgressSchema.opts": False,
    "LunMovementProgress": False,
}


class LunMovementProgressSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the LunMovementProgress object"""

    elapsed = Size(data_key="elapsed", allow_none=True)
    r""" The amount of time that has elapsed since the start of the LUN movement, in seconds. """

    failure = marshmallow_fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="failure", allow_none=True)
    r""" Error information provided if the asynchronous LUN movement operation fails. """

    percent_complete = Size(data_key="percent_complete", allow_none=True)
    r""" The percentage completed of the LUN movement. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" The state of the LUN movement.<br/>
Valid in PATCH when an LUN movement is active. Set to _paused_ to pause a LUN movement. Set to _replicating_ to resume a paused LUN movement.


Valid choices:

* preparing
* replicating
* paused
* paused_error
* complete
* reverting
* failed """

    volume_snapshot_blocked = marshmallow_fields.Boolean(data_key="volume_snapshot_blocked", allow_none=True)
    r""" This property reports if volume snapshots are blocked by the LUN movement. This property can be polled to identify when volume snapshots can be resumed after beginning a LUN movement. """

    @property
    def resource(self):
        return LunMovementProgress

    gettable_fields = [
        "elapsed",
        "failure",
        "percent_complete",
        "state",
        "volume_snapshot_blocked",
    ]
    """elapsed,failure,percent_complete,state,volume_snapshot_blocked,"""

    patchable_fields = [
        "state",
    ]
    """state,"""

    postable_fields = [
    ]
    """"""


class LunMovementProgress(Resource):

    _schema = LunMovementProgressSchema
