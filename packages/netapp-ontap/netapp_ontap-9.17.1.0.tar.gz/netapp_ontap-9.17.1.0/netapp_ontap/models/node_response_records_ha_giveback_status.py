r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NodeResponseRecordsHaGivebackStatus", "NodeResponseRecordsHaGivebackStatusSchema"]
__pdoc__ = {
    "NodeResponseRecordsHaGivebackStatusSchema.resource": False,
    "NodeResponseRecordsHaGivebackStatusSchema.opts": False,
    "NodeResponseRecordsHaGivebackStatus": False,
}


class NodeResponseRecordsHaGivebackStatusSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NodeResponseRecordsHaGivebackStatus object"""

    aggregate = marshmallow_fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE, data_key="aggregate", allow_none=True)
    r""" The aggregate field of the node_response_records_ha_giveback_status. """

    error = marshmallow_fields.Nested("netapp_ontap.models.cluster_nodes_ha_giveback_status_error.ClusterNodesHaGivebackStatusErrorSchema", unknown=EXCLUDE, data_key="error", allow_none=True)
    r""" Indicates the failed aggregate giveback code and message. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" Giveback state of the aggregate. <br/>
Possible values include no aggregates to giveback(nothing_to_giveback), failed to disable background disk firmware update(BDFU) on source node(failed_bdfu_source), <br/>
giveback delayed as disk firmware update is in progress on source node(delayed_bdfu_source), performing veto checks(running_checks). <br/>


Valid choices:

* done
* failed
* in_progress
* not_started
* nothing_to_giveback
* failed_bdfu_source
* failed_bdfu_dest
* delayed_bdfu_source
* delayed_bdfu_dest
* running_checks """

    @property
    def resource(self):
        return NodeResponseRecordsHaGivebackStatus

    gettable_fields = [
        "aggregate.links",
        "aggregate.name",
        "aggregate.uuid",
        "error",
        "state",
    ]
    """aggregate.links,aggregate.name,aggregate.uuid,error,state,"""

    patchable_fields = [
        "aggregate.name",
        "aggregate.uuid",
        "error",
        "state",
    ]
    """aggregate.name,aggregate.uuid,error,state,"""

    postable_fields = [
        "aggregate.name",
        "aggregate.uuid",
        "error",
        "state",
    ]
    """aggregate.name,aggregate.uuid,error,state,"""


class NodeResponseRecordsHaGivebackStatus(Resource):

    _schema = NodeResponseRecordsHaGivebackStatusSchema
