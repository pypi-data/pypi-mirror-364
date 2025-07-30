r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NodeHaGiveback", "NodeHaGivebackSchema"]
__pdoc__ = {
    "NodeHaGivebackSchema.resource": False,
    "NodeHaGivebackSchema.opts": False,
    "NodeHaGiveback": False,
}


class NodeHaGivebackSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NodeHaGiveback object"""

    failure = marshmallow_fields.Nested("netapp_ontap.models.cluster_nodes_ha_giveback_failure.ClusterNodesHaGivebackFailureSchema", unknown=EXCLUDE, data_key="failure", allow_none=True)
    r""" Indicates the failure code and message. This property is not supported on the ASA r2 platform. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" The state field of the node_ha_giveback.

Valid choices:

* nothing_to_giveback
* not_attempted
* in_progress
* failed """

    status = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.cluster_nodes_ha_giveback_status.ClusterNodesHaGivebackStatusSchema", unknown=EXCLUDE, allow_none=True), data_key="status", allow_none=True)
    r""" Giveback status of each aggregate. This property is not supported on the ASA r2 platform. """

    @property
    def resource(self):
        return NodeHaGiveback

    gettable_fields = [
        "failure",
        "state",
        "status",
    ]
    """failure,state,status,"""

    patchable_fields = [
        "failure",
        "state",
    ]
    """failure,state,"""

    postable_fields = [
        "failure",
        "state",
    ]
    """failure,state,"""


class NodeHaGiveback(Resource):

    _schema = NodeHaGivebackSchema
