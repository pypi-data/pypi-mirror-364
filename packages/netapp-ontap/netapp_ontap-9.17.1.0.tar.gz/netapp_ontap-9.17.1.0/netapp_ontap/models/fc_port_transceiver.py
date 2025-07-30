r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["FcPortTransceiver", "FcPortTransceiverSchema"]
__pdoc__ = {
    "FcPortTransceiverSchema.resource": False,
    "FcPortTransceiverSchema.opts": False,
    "FcPortTransceiver": False,
}


class FcPortTransceiverSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the FcPortTransceiver object"""

    capabilities = marshmallow_fields.List(Size, data_key="capabilities", allow_none=True)
    r""" The speeds of which the transceiver is capable in gigabits per second. """

    form_factor = marshmallow_fields.Str(data_key="form_factor", allow_none=True)
    r""" The form factor of the transceiver. Possible values are:
- _sfp_ - Small Form Factor - Pluggable
- _sff_ - Small Form Factor
- _unknown_ - Unknown


Valid choices:

* sfp
* sff
* unknown """

    manufacturer = marshmallow_fields.Str(data_key="manufacturer", allow_none=True)
    r""" The manufacturer of the transceiver.


Example: Acme, Inc. """

    part_number = marshmallow_fields.Str(data_key="part_number", allow_none=True)
    r""" The part number of the transceiver. """

    @property
    def resource(self):
        return FcPortTransceiver

    gettable_fields = [
        "capabilities",
        "form_factor",
        "manufacturer",
        "part_number",
    ]
    """capabilities,form_factor,manufacturer,part_number,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FcPortTransceiver(Resource):

    _schema = FcPortTransceiverSchema
