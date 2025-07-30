r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["StorageUnitStatus", "StorageUnitStatusSchema"]
__pdoc__ = {
    "StorageUnitStatusSchema.resource": False,
    "StorageUnitStatusSchema.opts": False,
    "StorageUnitStatus": False,
}


class StorageUnitStatusSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the StorageUnitStatus object"""

    container_state = marshmallow_fields.Str(data_key="container_state", allow_none=True)
    r""" The state of the storage unit and aggregate that contains it. Storage units are only available when their containers are available.


Valid choices:

* online
* aggregate_offline
* volume_offline """

    mapped = marshmallow_fields.Boolean(data_key="mapped", allow_none=True)
    r""" Reports if the storage unit is mapped to one or more hosts.<br/>
There is an added computational cost to retrieving this property's value. It is not populated for a GET request unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. """

    read_only = marshmallow_fields.Boolean(data_key="read_only", allow_none=True)
    r""" Reports if the storage unit allows only read access. """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" The state of the storage unit. Normal states for a storage unit are _online_ and _offline_. Other states indicate errors.


Valid choices:

* foreign_lun_error
* nvfail
* offline
* online
* space_error """

    @property
    def resource(self):
        return StorageUnitStatus

    gettable_fields = [
        "container_state",
        "mapped",
        "read_only",
        "state",
    ]
    """container_state,mapped,read_only,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class StorageUnitStatus(Resource):

    _schema = StorageUnitStatusSchema
