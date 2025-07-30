r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

"""

from marshmallow import EXCLUDE, fields as marshmallow_fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size


__all__ = ["WebCsrfToken", "WebCsrfTokenSchema"]
__pdoc__ = {
    "WebCsrfTokenSchema.resource": False,
    "WebCsrfTokenSchema.opts": False,
    "WebCsrfToken": False,
}


class WebCsrfTokenSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the WebCsrfToken object"""

    concurrent_limit = Size(data_key="concurrent_limit", allow_none=True)
    r""" Maximum number of concurrent CSRF tokens.

Example: 120 """

    idle_timeout = Size(data_key="idle_timeout", allow_none=True)
    r""" Time for which an unused CSRF token is retained, in seconds.

Example: 200 """

    max_timeout = Size(data_key="max_timeout", allow_none=True)
    r""" Time for which an unused CSRF token, regardless of usage is retained, in seconds.

Example: 1200 """

    @property
    def resource(self):
        return WebCsrfToken

    gettable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""

    patchable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""

    postable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""


class WebCsrfToken(Resource):

    _schema = WebCsrfTokenSchema
