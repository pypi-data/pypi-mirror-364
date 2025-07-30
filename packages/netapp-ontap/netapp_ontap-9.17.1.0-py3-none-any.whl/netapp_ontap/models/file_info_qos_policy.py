r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FileInfoQosPolicy", "FileInfoQosPolicySchema"]
__pdoc__ = {
    "FileInfoQosPolicySchema.resource": False,
    "FileInfoQosPolicySchema.opts": False,
    "FileInfoQosPolicy": False,
}


class FileInfoQosPolicySchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FileInfoQosPolicy object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links", allow_none=True)
    r""" The links field of the file_info_qos_policy. """

    name = marshmallow_fields.Str(data_key="name", allow_none=True)
    r""" The name of the QoS policy. To remove the file from a QoS policy, set this property to an empty string "" or set it to "none" in a PATCH request. """

    uuid = marshmallow_fields.Str(data_key="uuid", allow_none=True)
    r""" The unique identifier of the QoS policy. Valid in PATCH. """

    @property
    def resource(self):
        return FileInfoQosPolicy

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class FileInfoQosPolicy(Resource):

    _schema = FileInfoQosPolicySchema
