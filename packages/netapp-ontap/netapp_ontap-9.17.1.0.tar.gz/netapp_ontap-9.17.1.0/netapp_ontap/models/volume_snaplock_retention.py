r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeSnaplockRetention", "VolumeSnaplockRetentionSchema"]
__pdoc__ = {
    "VolumeSnaplockRetentionSchema.resource": False,
    "VolumeSnaplockRetentionSchema.opts": False,
    "VolumeSnaplockRetention": False,
}


class VolumeSnaplockRetentionSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeSnaplockRetention object"""

    default = marshmallow_fields.Str(data_key="default", allow_none=True)
    r""" Specifies the default retention period that is applied to files while committing them to the WORM state without an associated retention period. The retention value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours, and minutes. A duration specified for years, months, and days is represented in the ISO-8601 format as "P<num>Y", "P<num>M", "P<num>D" respectively, for example "P10Y" represents a duration of 10 years. A duration in hours and minutes is represented by "PT<num>H" and "PT<num>M" respectively. The retention string must contain only a single time element that is, either years, months, days, hours, or minutes. A duration which combines different periods is not supported, for example "P1Y10M" is not supported. Apart from the duration specified in the ISO-8601 format, the duration field also accepts the string "infinite" to set an infinite retention period and the string "unspecified" to set an unspecified retention period.

Example: P30Y """

    maximum = marshmallow_fields.Str(data_key="maximum", allow_none=True)
    r""" Specifies the maximum allowed retention period for files committed to the WORM state on the volume. The retention value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours, and minutes. A duration specified for years, months, and days is represented in the ISO-8601 format as "P<num>Y", "P<num>M", "P<num>D" respectively, for example "P10Y" represents a duration of 10 years. A duration in hours and minutes is represented by "PT<num>H" and "PT<num>M" respectively. The retention string must contain only a single time element that is, either years, months, days, hours, or minutes. A duration which combines different periods is not supported, for example "P1Y10M" is not supported. Apart from the duration specified in the ISO-8601 format, the duration field also accepts the string "infinite" to set an infinite retention period.

Example: P30Y """

    minimum = marshmallow_fields.Str(data_key="minimum", allow_none=True)
    r""" Specifies the minimum allowed retention period for files committed to the WORM state on the volume. The retention value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours, and minutes. A duration specified for years, month,s and days is represented in the ISO-8601 format as "P<num>Y", "P<num>M", "P<num>D" respectively, for example "P10Y" represents a duration of 10 years. A duration in hours and minutes is represented by "PT<num>H" and "PT<num>M" respectively. The retention string must contain only a single time element that is, either years, months, days, hours, or minutes. A duration which combines different periods is not supported, for example "P1Y10M" is not supported. Apart from the duration specified in the ISO-8601 format, the duration field also accepts the string "infinite" to set an infinite retention period.

Example: P30Y """

    @property
    def resource(self):
        return VolumeSnaplockRetention

    gettable_fields = [
        "default",
        "maximum",
        "minimum",
    ]
    """default,maximum,minimum,"""

    patchable_fields = [
        "default",
        "maximum",
        "minimum",
    ]
    """default,maximum,minimum,"""

    postable_fields = [
        "default",
        "maximum",
        "minimum",
    ]
    """default,maximum,minimum,"""


class VolumeSnaplockRetention(Resource):

    _schema = VolumeSnaplockRetentionSchema
