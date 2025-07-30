r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["ShelfTemperatureSensors", "ShelfTemperatureSensorsSchema"]
__pdoc__ = {
    "ShelfTemperatureSensorsSchema.resource": False,
    "ShelfTemperatureSensorsSchema.opts": False,
    "ShelfTemperatureSensors": False,
}


class ShelfTemperatureSensorsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ShelfTemperatureSensors object"""

    ambient = marshmallow_fields.Boolean(data_key="ambient", allow_none=True)
    r""" Sensor that measures the ambient temperature

Example: false """

    id = Size(data_key="id", allow_none=True)
    r""" The id field of the shelf_temperature_sensors.

Example: 1 """

    installed = marshmallow_fields.Boolean(data_key="installed", allow_none=True)
    r""" The installed field of the shelf_temperature_sensors.

Example: true """

    location = marshmallow_fields.Str(data_key="location", allow_none=True)
    r""" The location field of the shelf_temperature_sensors.

Example: temp sensor on midplane left """

    state = marshmallow_fields.Str(data_key="state", allow_none=True)
    r""" The state field of the shelf_temperature_sensors.

Valid choices:

* ok
* error """

    temperature = Size(data_key="temperature", allow_none=True)
    r""" Temperature, in degrees Celsius

Example: 32 """

    threshold = marshmallow_fields.Nested("netapp_ontap.models.shelf_temperature_sensors_threshold.ShelfTemperatureSensorsThresholdSchema", unknown=EXCLUDE, data_key="threshold", allow_none=True)
    r""" The threshold field of the shelf_temperature_sensors. """

    @property
    def resource(self):
        return ShelfTemperatureSensors

    gettable_fields = [
        "ambient",
        "id",
        "installed",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,installed,location,state,temperature,threshold,"""

    patchable_fields = [
        "ambient",
        "id",
        "installed",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,installed,location,state,temperature,threshold,"""

    postable_fields = [
        "ambient",
        "id",
        "installed",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,installed,location,state,temperature,threshold,"""


class ShelfTemperatureSensors(Resource):

    _schema = ShelfTemperatureSensorsSchema
