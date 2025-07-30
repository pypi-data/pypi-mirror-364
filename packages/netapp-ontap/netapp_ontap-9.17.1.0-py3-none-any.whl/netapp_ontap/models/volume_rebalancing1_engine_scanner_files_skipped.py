r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeRebalancing1EngineScannerFilesSkipped", "VolumeRebalancing1EngineScannerFilesSkippedSchema"]
__pdoc__ = {
    "VolumeRebalancing1EngineScannerFilesSkippedSchema.resource": False,
    "VolumeRebalancing1EngineScannerFilesSkippedSchema.opts": False,
    "VolumeRebalancing1EngineScannerFilesSkipped": False,
}


class VolumeRebalancing1EngineScannerFilesSkippedSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeRebalancing1EngineScannerFilesSkipped object"""

    efficiency_blocks = Size(data_key="efficiency_blocks", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because storage efficiency lost, in blocks, would be too high. """

    efficiency_percent = Size(data_key="efficiency_percent", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because storage efficiency lost, in percent, would be too high. """

    fast_truncate = Size(data_key="fast_truncate", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because fast truncate is currently running on the file. """

    footprint_invalid = Size(data_key="footprint_invalid", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because their space footprints are invalid. """

    in_snapshot = Size(data_key="in_snapshot", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are trapped in snapshots. """

    incompatible = Size(data_key="incompatible", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are incompatible. """

    metadata = Size(data_key="metadata", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they metadata files. """

    on_demand_destination = Size(data_key="on_demand_destination", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are on demand destinations. """

    other = Size(data_key="other", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent for all other reasons. """

    remote_cache = Size(data_key="remote_cache", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are remote caches. """

    too_large = Size(data_key="too_large", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are larger than rebalancing.max_file_size. """

    too_small = Size(data_key="too_small", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are smaller than rebalancing.min_file_size. """

    write_fenced = Size(data_key="write_fenced", allow_none=True)
    r""" Number of files skipped by the scanner on this constituent because they are fenced for write operations. """

    @property
    def resource(self):
        return VolumeRebalancing1EngineScannerFilesSkipped

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


class VolumeRebalancing1EngineScannerFilesSkipped(Resource):

    _schema = VolumeRebalancing1EngineScannerFilesSkippedSchema
