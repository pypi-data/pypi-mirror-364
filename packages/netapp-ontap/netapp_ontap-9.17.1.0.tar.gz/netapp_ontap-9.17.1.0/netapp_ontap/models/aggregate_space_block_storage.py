r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["AggregateSpaceBlockStorage", "AggregateSpaceBlockStorageSchema"]
__pdoc__ = {
    "AggregateSpaceBlockStorageSchema.resource": False,
    "AggregateSpaceBlockStorageSchema.opts": False,
    "AggregateSpaceBlockStorage": False,
}


class AggregateSpaceBlockStorageSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the AggregateSpaceBlockStorage object"""

    aggregate_metadata = Size(data_key="aggregate_metadata", allow_none=True)
    r""" Space used by different metafiles and internal operations inside the aggregate, in bytes.

Example: 2655 """

    aggregate_metadata_percent = Size(data_key="aggregate_metadata_percent", allow_none=True)
    r""" Aggregate metadata as a percentage.

Example: 8 """

    available = Size(data_key="available", allow_none=True)
    r""" Space available in bytes.

Example: 10156560384 """

    data_compacted_count = Size(data_key="data_compacted_count", allow_none=True)
    r""" Amount of compacted data in bytes.

Example: 1990000 """

    data_compaction_space_saved = Size(data_key="data_compaction_space_saved", allow_none=True)
    r""" Space saved in bytes by compacting the data.

Example: 1996000 """

    data_compaction_space_saved_percent = Size(data_key="data_compaction_space_saved_percent", allow_none=True)
    r""" Percentage saved by compacting the data.

Example: 27 """

    full_threshold_percent = Size(data_key="full_threshold_percent", allow_none=True)
    r""" The aggregate used percentage at which 'monitor.volume.full' EMS is generated. """

    inactive_user_data = Size(data_key="inactive_user_data", allow_none=True)
    r""" The size that is physically used in the block storage and has a cold temperature, in bytes. This property is only supported if the aggregate is either attached to a cloud store or can be attached to a cloud store.
This is an advanced property; there is an added computational cost to retrieving its value. The field is not populated for either a collection GET or an instance GET unless it is explicitly requested using the <i>fields</i> query parameter containing either block_storage.inactive_user_data or **.


Example: 304448 """

    inactive_user_data_percent = Size(data_key="inactive_user_data_percent", allow_none=True)
    r""" The percentage of inactive user data in the block storage. This property is only supported if the aggregate is either attached to a cloud store or can be attached to a cloud store.
This is an advanced property; there is an added computational cost to retrieving its value. The field is not populated for either a collection GET or an instance GET unless it is explicitly requested using the <i>fields</i> query parameter containing either block_storage.inactive_user_data_percent or **. """

    physical_used = Size(data_key="physical_used", allow_none=True)
    r""" Total physical used size of an aggregate in bytes.

Example: 2461696 """

    physical_used_percent = Size(data_key="physical_used_percent", allow_none=True)
    r""" Physical used percentage.

Example: 50 """

    size = Size(data_key="size", allow_none=True)
    r""" Total usable space in bytes, not including WAFL reserve and aggregate snapshot reserve.

Example: 10156769280 """

    used = Size(data_key="used", allow_none=True)
    r""" Space used or reserved in bytes. Includes volume guarantees and aggregate metadata.

Example: 2088960 """

    used_including_snapshot_reserve = Size(data_key="used_including_snapshot_reserve", allow_none=True)
    r""" Total used including the snapshot reserve, in bytes.

Example: 674685 """

    used_including_snapshot_reserve_percent = Size(data_key="used_including_snapshot_reserve_percent", allow_none=True)
    r""" Total used including the Snapshot reserve as a percentage.

Example: 35 """

    used_percent = Size(data_key="used_percent", allow_none=True)
    r""" Aggregate used percentage.

Example: 50 """

    volume_deduplication_shared_count = Size(data_key="volume_deduplication_shared_count", allow_none=True)
    r""" Amount of shared bytes counted by storage efficiency.

Example: 1990000 """

    volume_deduplication_space_saved = Size(data_key="volume_deduplication_space_saved", allow_none=True)
    r""" Amount of space saved in bytes by storage efficiency.

Example: 1996000 """

    volume_deduplication_space_saved_percent = Size(data_key="volume_deduplication_space_saved_percent", allow_none=True)
    r""" Percentage of space saved by storage efficiency.

Example: 27 """

    volume_footprints_percent = Size(data_key="volume_footprints_percent", allow_none=True)
    r""" A summation of volume footprints inside the aggregate, as a percentage. A volume's footprint is the amount of space being used for the volume in the aggregate.

Example: 14 """

    @property
    def resource(self):
        return AggregateSpaceBlockStorage

    gettable_fields = [
        "aggregate_metadata",
        "aggregate_metadata_percent",
        "available",
        "data_compacted_count",
        "data_compaction_space_saved",
        "data_compaction_space_saved_percent",
        "full_threshold_percent",
        "inactive_user_data",
        "inactive_user_data_percent",
        "physical_used",
        "physical_used_percent",
        "size",
        "used",
        "used_including_snapshot_reserve",
        "used_including_snapshot_reserve_percent",
        "used_percent",
        "volume_deduplication_shared_count",
        "volume_deduplication_space_saved",
        "volume_deduplication_space_saved_percent",
        "volume_footprints_percent",
    ]
    """aggregate_metadata,aggregate_metadata_percent,available,data_compacted_count,data_compaction_space_saved,data_compaction_space_saved_percent,full_threshold_percent,inactive_user_data,inactive_user_data_percent,physical_used,physical_used_percent,size,used,used_including_snapshot_reserve,used_including_snapshot_reserve_percent,used_percent,volume_deduplication_shared_count,volume_deduplication_space_saved,volume_deduplication_space_saved_percent,volume_footprints_percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateSpaceBlockStorage(Resource):

    _schema = AggregateSpaceBlockStorageSchema
