r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["San", "SanSchema"]
__pdoc__ = {
    "SanSchema.resource": False,
    "SanSchema.opts": False,
    "San": False,
}


class SanSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the San object"""

    application_components = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.san_application_components.SanApplicationComponentsSchema", unknown=EXCLUDE, allow_none=True), data_key="application_components", allow_none=True)
    r""" The application_components field of the san. """

    exclude_aggregates = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.nas_exclude_aggregates.NasExcludeAggregatesSchema", unknown=EXCLUDE, allow_none=True), data_key="exclude_aggregates", allow_none=True)
    r""" The exclude_aggregates field of the san. """

    new_igroups = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.san_new_igroups.SanNewIgroupsSchema", unknown=EXCLUDE, allow_none=True), data_key="new_igroups", allow_none=True)
    r""" The list of initiator groups to create. """

    os_type = marshmallow_fields.Str(data_key="os_type", allow_none=True)
    r""" The name of the host OS running the application.

Valid choices:

* aix
* hpux
* hyper_v
* linux
* netware
* openvms
* solaris
* solaris_efi
* vmware
* windows
* windows_2008
* windows_gpt
* xen """

    protection_type = marshmallow_fields.Nested("netapp_ontap.models.nas_protection_type.NasProtectionTypeSchema", unknown=EXCLUDE, data_key="protection_type", allow_none=True)
    r""" The protection_type field of the san. """

    @property
    def resource(self):
        return San

    gettable_fields = [
        "application_components",
        "exclude_aggregates",
        "os_type",
        "protection_type",
    ]
    """application_components,exclude_aggregates,os_type,protection_type,"""

    patchable_fields = [
        "application_components",
        "new_igroups",
        "protection_type",
    ]
    """application_components,new_igroups,protection_type,"""

    postable_fields = [
        "application_components",
        "exclude_aggregates",
        "new_igroups",
        "os_type",
        "protection_type",
    ]
    """application_components,exclude_aggregates,new_igroups,os_type,protection_type,"""


class San(Resource):

    _schema = SanSchema
