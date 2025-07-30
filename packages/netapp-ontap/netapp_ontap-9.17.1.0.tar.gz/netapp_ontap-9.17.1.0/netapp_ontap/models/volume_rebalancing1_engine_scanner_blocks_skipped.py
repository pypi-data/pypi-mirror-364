r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeRebalancing1EngineScannerBlocksSkipped", "VolumeRebalancing1EngineScannerBlocksSkippedSchema"]
__pdoc__ = {
    "VolumeRebalancing1EngineScannerBlocksSkippedSchema.resource": False,
    "VolumeRebalancing1EngineScannerBlocksSkippedSchema.opts": False,
    "VolumeRebalancing1EngineScannerBlocksSkipped": False,
}


class VolumeRebalancing1EngineScannerBlocksSkippedSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeRebalancing1EngineScannerBlocksSkipped object"""

    efficiency_blocks = Size(data_key="efficiency_blocks", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because storage efficiency lost, in blocks, would be too high. """

    efficiency_percent = Size(data_key="efficiency_percent", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because storage efficiency lost, in percent, would be too high. """

    fast_truncate = Size(data_key="fast_truncate", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because fast truncate is currently running on files. """

    footprint_invalid = Size(data_key="footprint_invalid", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of files with invalid space footprints. """

    in_snapshot = Size(data_key="in_snapshot", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of files in snapshots. """

    incompatible = Size(data_key="incompatible", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of incompatible files. """

    metadata = Size(data_key="metadata", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of metadata files. """

    on_demand_destination = Size(data_key="on_demand_destination", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of on demand destination files. """

    other = Size(data_key="other", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent for all other reasons. """

    remote_cache = Size(data_key="remote_cache", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of remote caches. """

    too_large = Size(data_key="too_large", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of files that are larger than rebalancing.max_file_size. """

    too_small = Size(data_key="too_small", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of files that are smaller than rebalancing.min_file_size. """

    write_fenced = Size(data_key="write_fenced", allow_none=True)
    r""" Number of blocks skipped by the scanner on this constituent because of files fenced for write operations. """

    @property
    def resource(self):
        return VolumeRebalancing1EngineScannerBlocksSkipped

    gettable_fields = [
        "efficiency_blocks",
        "efficiency_percent",
        "fast_truncate",
        "footprint_invalid",
        "in_snapshot",
        "incompatible",
        "metadata",
        "on_demand_destination",
        "other",
        "remote_cache",
        "too_large",
        "too_small",
        "write_fenced",
    ]
    """efficiency_blocks,efficiency_percent,fast_truncate,footprint_invalid,in_snapshot,incompatible,metadata,on_demand_destination,other,remote_cache,too_large,too_small,write_fenced,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeRebalancing1EngineScannerBlocksSkipped(Resource):

    _schema = VolumeRebalancing1EngineScannerBlocksSkippedSchema
