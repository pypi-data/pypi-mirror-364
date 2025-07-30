r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["NvmeHostProximityPeerSvms", "NvmeHostProximityPeerSvmsSchema"]
__pdoc__ = {
    "NvmeHostProximityPeerSvmsSchema.resource": False,
    "NvmeHostProximityPeerSvmsSchema.opts": False,
    "NvmeHostProximityPeerSvms": False,
}


class NvmeHostProximityPeerSvmsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the NvmeHostProximityPeerSvms object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the nvme_host_proximity_peer_svms. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The local name of the peer SVM. This name is unique among all local and peer SVMs.


Example: peer1 """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the SVM peer relationship. This is the UUID of the relationship, not the UUID of the peer SVM itself.


Example: 4204cf77-4c82-9bdb-5644-b5a841c097a9 """

    @property
    def resource(self):
        return NvmeHostProximityPeerSvms

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class NvmeHostProximityPeerSvms(Resource):

    _schema = NvmeHostProximityPeerSvmsSchema
