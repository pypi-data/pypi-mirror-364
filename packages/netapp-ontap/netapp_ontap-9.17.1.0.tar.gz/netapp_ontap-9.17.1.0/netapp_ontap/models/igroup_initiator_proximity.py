r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["IgroupInitiatorProximity", "IgroupInitiatorProximitySchema"]
__pdoc__ = {
    "IgroupInitiatorProximitySchema.resource": False,
    "IgroupInitiatorProximitySchema.opts": False,
    "IgroupInitiatorProximity": False,
}


class IgroupInitiatorProximitySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the IgroupInitiatorProximity object"""

    local_svm = marshmallow_fields.Boolean(data_key="local_svm", allow_none=True)
    r""" A boolean that indicates if the initiator is proximal to the SVM of the containing initiator group. This is required for any POST or PATCH that includes the `proximity` sub-object. """

    peer_svms = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.igroup_initiators_proximity_peer_svms.IgroupInitiatorsProximityPeerSvmsSchema", unknown=EXCLUDE, allow_none=True), data_key="peer_svms", allow_none=True)
    r""" An array of remote peer SVMs to which the initiator is proximal. """

    @property
    def resource(self):
        return IgroupInitiatorProximity

    gettable_fields = [
        "local_svm",
        "peer_svms.links",
        "peer_svms.name",
        "peer_svms.uuid",
    ]
    """local_svm,peer_svms.links,peer_svms.name,peer_svms.uuid,"""

    patchable_fields = [
        "local_svm",
        "peer_svms.name",
        "peer_svms.uuid",
    ]
    """local_svm,peer_svms.name,peer_svms.uuid,"""

    postable_fields = [
        "local_svm",
        "peer_svms.name",
        "peer_svms.uuid",
    ]
    """local_svm,peer_svms.name,peer_svms.uuid,"""


class IgroupInitiatorProximity(Resource):

    _schema = IgroupInitiatorProximitySchema
