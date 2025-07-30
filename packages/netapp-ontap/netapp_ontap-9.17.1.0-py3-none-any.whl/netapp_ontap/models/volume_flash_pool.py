r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["VolumeFlashPool", "VolumeFlashPoolSchema"]
__pdoc__ = {
    "VolumeFlashPoolSchema.resource": False,
    "VolumeFlashPoolSchema.opts": False,
    "VolumeFlashPool": False,
}


class VolumeFlashPoolSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the VolumeFlashPool object"""

    cache_eligibility = marshmallow_fields.Str(data_key="cache_eligibility", allow_none=True)
    r""" If this parameter is specified, the command displays information only about the volume or volumes with the specified Flash Pool caching attributes.

Valid choices:

* read
* read_write
* none """

    cache_retention_priority = marshmallow_fields.Str(data_key="cache_retention_priority", allow_none=True)
    r""" If this parameter is specified, the command displays the volumes that match the specified cache retention priority policy. A cache retention priority defines how long the blocks of a volume will be cached in the Flash Pool once they become cold.

Valid choices:

* normal
* low
* high """

    caching_policy = marshmallow_fields.Str(data_key="caching_policy", allow_none=True)
    r""" This optionally specifies the caching policy to apply to the volume. A caching policy defines how the system caches a volume's data in Flash Cache modules. If a caching policy is not assigned to a volume, the system uses the caching policy that is assigned to the containing SVM. If a caching policy is not assigned to the containing SVM, the system uses the default cluster-wide policy.

Valid choices:

* none
* auto
* meta
* random_read
* random_read_write
* all_read
* all_read_random_write
* all
* noread_random_write
* meta_random_write
* random_read_write_random_write
* all_read_random_write_random_write
* all_random_write """

    @property
    def resource(self):
        return VolumeFlashPool

    gettable_fields = [
        "cache_eligibility",
        "cache_retention_priority",
        "caching_policy",
    ]
    """cache_eligibility,cache_retention_priority,caching_policy,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeFlashPool(Resource):

    _schema = VolumeFlashPoolSchema
