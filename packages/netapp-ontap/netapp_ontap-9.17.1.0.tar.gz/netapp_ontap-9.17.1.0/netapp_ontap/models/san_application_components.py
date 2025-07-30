r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["SanApplicationComponents", "SanApplicationComponentsSchema"]
__pdoc__ = {
    "SanApplicationComponentsSchema.resource": False,
    "SanApplicationComponentsSchema.opts": False,
    "SanApplicationComponents": False,
}


class SanApplicationComponentsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the SanApplicationComponents object"""

    igroup_name = marshmallow_fields.Str(data_key="igroup_name", allow_none=True)
    r""" The name of the initiator group through which the contents of this application will be accessed. Modification of this parameter is a disruptive operation. All LUNs in the application component will be unmapped from the current igroup and re-mapped to the new igroup. """

    lun_count = Size(data_key="lun_count", allow_none=True)
    r""" The number of LUNs in the application component. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the application component. """

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

    qos = marshmallow_fields.Nested("netapp_ontap.models.nas_application_components_qos.NasApplicationComponentsQosSchema", unknown=EXCLUDE, data_key="qos", allow_none=True)
    r""" The qos field of the san_application_components. """

    storage_service = marshmallow_fields.Nested("netapp_ontap.models.nas_application_components_storage_service.NasApplicationComponentsStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service", allow_none=True)
    r""" The storage_service field of the san_application_components. """

    tiering = marshmallow_fields.Nested("netapp_ontap.models.san_application_components_tiering.SanApplicationComponentsTieringSchema", unknown=EXCLUDE, data_key="tiering", allow_none=True)
    r""" application-components.tiering """

    total_size = Size(data_key="total_size", allow_none=True)
    r""" The total size of the application component, split across the member LUNs. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    @property
    def resource(self):
        return SanApplicationComponents

    gettable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "qos",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,qos,storage_service,tiering,total_size,"""

    patchable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,storage_service,tiering,total_size,"""

    postable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "qos",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,qos,storage_service,tiering,total_size,"""


class SanApplicationComponents(Resource):

    _schema = SanApplicationComponentsSchema
