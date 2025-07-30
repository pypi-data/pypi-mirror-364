r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["IgroupConnectivityTrackingAlerts", "IgroupConnectivityTrackingAlertsSchema"]
__pdoc__ = {
    "IgroupConnectivityTrackingAlertsSchema.resource": False,
    "IgroupConnectivityTrackingAlertsSchema.opts": False,
    "IgroupConnectivityTrackingAlerts": False,
}


class IgroupConnectivityTrackingAlertsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the IgroupConnectivityTrackingAlerts object"""

    summary = marshmallow_fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="summary", allow_none=True)
    r""" The summary field of the igroup_connectivity_tracking_alerts. """

    @property
    def resource(self):
        return IgroupConnectivityTrackingAlerts

    gettable_fields = [
        "summary",
    ]
    """summary,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IgroupConnectivityTrackingAlerts(Resource):

    _schema = IgroupConnectivityTrackingAlertsSchema
