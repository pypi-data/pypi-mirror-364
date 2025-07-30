r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupTiering", "ConsistencyGroupTieringSchema"]
__pdoc__ = {
    "ConsistencyGroupTieringSchema.resource": False,
    "ConsistencyGroupTieringSchema.opts": False,
    "ConsistencyGroupTiering": False,
}


class ConsistencyGroupTieringSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ConsistencyGroupTiering object"""

    control = marshmallow_fields.Str(data_key="control", allow_none=True)
    r""" Storage tiering placement rules for the object.

Valid choices:

* allowed
* best_effort
* disallowed
* required """

    object_stores = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.consistency_group_consistency_groups_tiering_object_stores.ConsistencyGroupConsistencyGroupsTieringObjectStoresSchema", unknown=EXCLUDE, allow_none=True), data_key="object_stores", allow_none=True)
    r""" Object stores to use. Used for placement. """

    policy = marshmallow_fields.Str(data_key="policy", allow_none=True)
    r""" Policy that determines whether the user data blocks of a volume in a FabricPool will be tiered to the cloud store when they become cold.
<br>FabricPool combines flash (performance tier) with a cloud store into a single aggregate. Temperature of a volume block increases if it is accessed frequently and decreases when it is not. Valid in POST or PATCH.<br/>all &dash; Allows tiering of both snapshots and active file system user data to the cloud store as soon as possible by ignoring the temperature on the volume blocks.<br/>auto &dash; Allows tiering of both snapshot and active file system user data to the cloud store<br/>none &dash; Volume blocks are not be tiered to the cloud store.<br/>snapshot_only &dash; Allows tiering of only the volume snapshots not associated with the active file system.
<br>The default tiering policy is "snapshot-only" for a FlexVol volume and "none" for a FlexGroup volume. The default minimum cooling period for the "snapshot-only" tiering policy is 2 days and for the "auto" tiering policy it is 31 days.


Valid choices:

* all
* auto
* backup
* none
* snapshot_only """

    @property
    def resource(self):
        return ConsistencyGroupTiering

    gettable_fields = [
        "object_stores",
        "policy",
    ]
    """object_stores,policy,"""

    patchable_fields = [
        "control",
        "object_stores",
    ]
    """control,object_stores,"""

    postable_fields = [
        "control",
        "object_stores",
        "policy",
    ]
    """control,object_stores,policy,"""


class ConsistencyGroupTiering(Resource):

    _schema = ConsistencyGroupTieringSchema
