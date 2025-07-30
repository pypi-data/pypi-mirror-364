r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ZappNvmeComponents", "ZappNvmeComponentsSchema"]
__pdoc__ = {
    "ZappNvmeComponentsSchema.resource": False,
    "ZappNvmeComponentsSchema.opts": False,
    "ZappNvmeComponents": False,
}


class ZappNvmeComponentsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ZappNvmeComponents object"""

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the application component. """

    namespace_count = Size(data_key="namespace_count", allow_none=True)
    r""" The number of namespaces supported per request, with a total limit of 1024 per volume. """

    os_type = marshmallow_fields.Str(data_key="os_type", allow_none=True)
    r""" The name of the host OS running the application.

Valid choices:

* aix
* linux
* vmware
* windows """

    performance = marshmallow_fields.Nested("netapp_ontap.models.zapp_nvme_components_performance.ZappNvmeComponentsPerformanceSchema", unknown=EXCLUDE, data_key="performance", allow_none=True)
    r""" The performance field of the zapp_nvme_components. """

    qos = marshmallow_fields.Nested("netapp_ontap.models.nas_application_components_qos.NasApplicationComponentsQosSchema", unknown=EXCLUDE, data_key="qos", allow_none=True)
    r""" The qos field of the zapp_nvme_components. """

    subsystem = marshmallow_fields.Nested("netapp_ontap.models.zapp_nvme_components_subsystem.ZappNvmeComponentsSubsystemSchema", unknown=EXCLUDE, data_key="subsystem", allow_none=True)
    r""" components.subsystem """

    tiering = marshmallow_fields.Nested("netapp_ontap.models.zapp_nvme_components_tiering.ZappNvmeComponentsTieringSchema", unknown=EXCLUDE, data_key="tiering", allow_none=True)
    r""" application-components.tiering """

    total_size = Size(data_key="total_size", allow_none=True)
    r""" The total size of the component, spread across member namespaces. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    @property
    def resource(self):
        return ZappNvmeComponents

    gettable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "qos",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,qos,subsystem,tiering,total_size,"""

    patchable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,subsystem,tiering,total_size,"""

    postable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "qos",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,qos,subsystem,tiering,total_size,"""


class ZappNvmeComponents(Resource):

    _schema = ZappNvmeComponentsSchema
