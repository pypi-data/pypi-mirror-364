r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SnapmirrorDestinationCreationStorageService", "SnapmirrorDestinationCreationStorageServiceSchema"]
__pdoc__ = {
    "SnapmirrorDestinationCreationStorageServiceSchema.resource": False,
    "SnapmirrorDestinationCreationStorageServiceSchema.opts": False,
    "SnapmirrorDestinationCreationStorageService": False,
}


class SnapmirrorDestinationCreationStorageServiceSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SnapmirrorDestinationCreationStorageService object"""

    enabled = marshmallow_fields.Boolean(data_key="enabled", allow_none=True)
    r""" This property indicates whether to create the destination endpoint using storage service. This property is supported for Unified ONTAP destination endpoints only. """

    enforce_performance = marshmallow_fields.Boolean(data_key="enforce_performance", allow_none=True)
    r""" Optional property to enforce storage service performance on the destination endpoint. This property is applicable to FlexVol volume, FlexGroup volume, and Consistency Group endpoints. This property is supported for Unified ONTAP destination endpoints only. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Optional property to specify the storage service name for the destination endpoint. This property is considered when the property "create_destination.storage_service.enabled" is set to "true". When the property "create_destination.storage_service.enabled" is set to "true" and the "create_destination.storage_service.name" for the endpoint is not specified, then ONTAP selects the highest storage service available on the cluster to provision the destination endpoint. This property is applicable to FlexVol volume, FlexGroup volume, and Consistency Group endpoints. This property is supported for Unified ONTAP destination endpoints only.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return SnapmirrorDestinationCreationStorageService

    gettable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""

    patchable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""

    postable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""


class SnapmirrorDestinationCreationStorageService(Resource):

    _schema = SnapmirrorDestinationCreationStorageServiceSchema
