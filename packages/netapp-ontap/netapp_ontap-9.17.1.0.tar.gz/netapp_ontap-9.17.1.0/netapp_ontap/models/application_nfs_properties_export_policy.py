r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ApplicationNfsPropertiesExportPolicy", "ApplicationNfsPropertiesExportPolicySchema"]
__pdoc__ = {
    "ApplicationNfsPropertiesExportPolicySchema.resource": False,
    "ApplicationNfsPropertiesExportPolicySchema.opts": False,
    "ApplicationNfsPropertiesExportPolicy": False,
}


class ApplicationNfsPropertiesExportPolicySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ApplicationNfsPropertiesExportPolicy object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" Export policy name """

    @property
    def resource(self):
        return ApplicationNfsPropertiesExportPolicy

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNfsPropertiesExportPolicy(Resource):

    _schema = ApplicationNfsPropertiesExportPolicySchema
