r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SnaplockLogVolume", "SnaplockLogVolumeSchema"]
__pdoc__ = {
    "SnaplockLogVolumeSchema.resource": False,
    "SnaplockLogVolumeSchema.opts": False,
    "SnaplockLogVolume": False,
}


class SnaplockLogVolumeSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SnaplockLogVolume object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the snaplock_log_volume. """

    max_log_size = Size(data_key="max_log_size", allow_none=True)
    r""" Maximum size of log file in bytes

Example: 20971520 """

    retention_period = marshmallow_fields.Str(data_key="retention_period", allow_none=True)
    r""" Specifies the default log record retention period. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours, minutes and seconds. A period specified for years, months and days is represented in the ISO-8601 format as "P<num>Y", "P<num>M", "P<num>D" respectively. For example "P10Y" represents a duration of 10 years. A duration in hours, minutes and seconds is represented by "PT<num>H", "PT<num>M", and "PT<num>S" respectively. The period string must contain only a single time element i.e. either years, months, days, hours, minutes or seconds. A duration which combines different periods is not supported, example "P1Y10M" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the string "infinite".

Example: P30M """

    volume = marshmallow_fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume", allow_none=True)
    r""" The volume field of the snaplock_log_volume. """

    @property
    def resource(self):
        return SnaplockLogVolume

    gettable_fields = [
        "links",
        "max_log_size",
        "retention_period",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,max_log_size,retention_period,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "max_log_size",
        "retention_period",
        "volume.name",
        "volume.uuid",
    ]
    """max_log_size,retention_period,volume.name,volume.uuid,"""

    postable_fields = [
        "max_log_size",
        "retention_period",
        "volume.name",
        "volume.uuid",
    ]
    """max_log_size,retention_period,volume.name,volume.uuid,"""


class SnaplockLogVolume(Resource):

    _schema = SnaplockLogVolumeSchema
