r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsSpace", "ApplicationStatisticsSpaceSchema"]
__pdoc__ = {
    "ApplicationStatisticsSpaceSchema.resource": False,
    "ApplicationStatisticsSpaceSchema.opts": False,
    "ApplicationStatisticsSpace": False,
}


class ApplicationStatisticsSpaceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationStatisticsSpace object"""

    available = Size(data_key="available", allow_none=True)
    r""" The available amount of space left in the application. Note that this field has limited meaning for SAN applications. Space may be considered used from ONTAP's perspective while the host filesystem still considers it available. """

    logical_used = Size(data_key="logical_used", allow_none=True)
    r""" The amount of space that would currently be used if no space saving features were enabled. For example, if compression were the only space saving feature enabled, this field would represent the uncompressed amount of space used. """

    provisioned = Size(data_key="provisioned", allow_none=True)
    r""" The originally requested amount of space that was provisioned for the application. """

    reserved_unused = Size(data_key="reserved_unused", allow_none=True)
    r""" The amount of space reserved for system features such as Snapshot copies that has not yet been used. """

    savings = Size(data_key="savings", allow_none=True)
    r""" The amount of space saved by all enabled space saving features. """

    used = Size(data_key="used", allow_none=True)
    r""" The amount of space that is currently being used by the application. Note that this includes any space reserved by the system for features such as Snapshot copies. """

    used_excluding_reserves = Size(data_key="used_excluding_reserves", allow_none=True)
    r""" The amount of space that is currently being used, excluding any space that is reserved by the system for features such as Snapshot copies. """

    used_percent = Size(data_key="used_percent", allow_none=True)
    r""" The percentage of the originally provisioned space that is currently being used by the application. """

    @property
    def resource(self):
        return ApplicationStatisticsSpace

    gettable_fields = [
        "available",
        "logical_used",
        "provisioned",
        "reserved_unused",
        "savings",
        "used",
        "used_excluding_reserves",
        "used_percent",
    ]
    """available,logical_used,provisioned,reserved_unused,savings,used,used_excluding_reserves,used_percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationStatisticsSpace(Resource):

    _schema = ApplicationStatisticsSpaceSchema
