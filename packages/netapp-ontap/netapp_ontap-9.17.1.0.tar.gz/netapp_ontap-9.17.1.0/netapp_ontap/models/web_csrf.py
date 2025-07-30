r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["WebCsrf", "WebCsrfSchema"]
__pdoc__ = {
    "WebCsrfSchema.resource": False,
    "WebCsrfSchema.opts": False,
    "WebCsrf": False,
}


class WebCsrfSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the WebCsrf object"""

    protection_enabled = marshmallow_fields.Boolean(data_key="protection_enabled", allow_none=True)
    r""" Indicates whether CSRF protection is enabled. """

    token = marshmallow_fields.Nested("netapp_ontap.models.web_csrf_token.WebCsrfTokenSchema", unknown=EXCLUDE, data_key="token", allow_none=True)
    r""" The token field of the web_csrf. """

    @property
    def resource(self):
        return WebCsrf

    gettable_fields = [
        "protection_enabled",
        "token",
    ]
    """protection_enabled,token,"""

    patchable_fields = [
        "protection_enabled",
        "token",
    ]
    """protection_enabled,token,"""

    postable_fields = [
        "protection_enabled",
        "token",
    ]
    """protection_enabled,token,"""


class WebCsrf(Resource):

    _schema = WebCsrfSchema
