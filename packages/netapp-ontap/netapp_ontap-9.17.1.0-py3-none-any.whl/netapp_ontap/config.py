"""
Copyright &copy; 2025 NetApp Inc. All rights reserved.

This module contains the global configuration options and related functions for the library.
"""

from typing import Dict, List, Optional
import netapp_ontap.host_connection  # pylint: disable=unused-import,cyclic-import

CONNECTION = None  # type: Optional[netapp_ontap.host_connection.HostConnection]
"""This `netapp_ontap.host_connection.HostConnection` object, if set, is used
as the default connection for all library operations if no other connection is set
at a more specific level. The hierarchy of lookups is:

- Any connection being used as a context manager (i.e. inside a with block)
- The connection set on a resource using `netapp_ontap.resource.Resource.set_connection`
- The global connection set here.

If none of these are set, an exception will be raised when a request is attempted.
"""

ENABLE_VALIDATIONS = True
"""If set to True, the library will enforce validations, e.g. minimum and maximum values,
for object fields as specified in the API spec. If a field does not meet the validation
criteria when being sent to the API host, a `netapp_ontap.error.NetAppRestError` will be
raised with the reason for the violation. If this value is set to False, then no
validation will take place prior to sending the values to the API host.
"""

STRICT_FIELD_ACCEPTANCE = False
"""If set to True, the library will not accept fields as part of a response that are not
included in the documented object model for that endpoint. If a field is returned from
the host that is not documented, a `netapp_ontap.error.NetAppRestError` will be raised
specifying which field(s) are invalid. If False (default), no exception will be raised
and the undocumented field will be set on the resource just like any other.
"""

STRICT_ACCESS_MODIFIERS = True
"""If set to True (default), fields marked as readOnly won't be sent in patch() or
post() requests. Fields marked as readModify or modifyOnly won't be sent in post()
requests. Fields marked as readCreate or createOnly won't be sent in patch() requests.
If set to False, the access modifier for a field will be ignored and it will be sent
if required."""

STRICT_GET = False
"""If set to True, before performing a `get()` on a resource, the resource will make
sure that all required keys are properly set. If a required key is missing, it will
throw an exception before sending out the REST GET request. If set to False (default),
the `get()` call would incorrectly behave like a `get_collection()` call returning
multiple records. This would result in an exception."""

RAISE_API_ERRORS = True
"""If set to True, the library will raise an exception if a request fails. If set
to false, the library will not raise an exception and the application is responsible
to check if the response was an error or not.
"""

RETRY_ON_INCOMPLETE_LOCATION = True
"""If set to True, the library will attempt to poll the resource if it cannot
determine its location after a call to post() due to an incomplete
'Location' header in the response. Setting this option to
False causes the library to throw an exception without polling if a full
address to the resource is not included in the `Location` response header.
"""

RETRY_API_ON_ERROR = False
"""If set to True, more granular retry functionality will
 be enabled for this library.  An exception will only be
 raised when retry attempts are exhausted."""

RETRY_API_ERROR_CODES = [429, 500, 502, 503, 504]
"""If the status code returned does not exist in this
list, no additional retry attempts will be made."""

RETRY_API_HTTP_METHODS = ["GET", "PATCH"]
"""If a request is made with an HTTP method not in this
list, no retry attempts will be made."""

RETRY_API_ATTEMPTS = 5
"""The number of retry attempts that will be made before
raising an exception to propagate the failure."""

RETRY_API_BACKOFF_FACTOR = 1.0
"""This setting configures the delay between retry attempts
according to the following formula:
    {backoff factor} * (2 ** ({number of total retries} - 1))
"""

REDACT_AUTHORIZATION_HEADER = True
"""If set to True, authorization headers will be redacted and replaced with `*****`
in the library's debug logs."""

REDACT_SENSITIVE_FIELDS = True
"""If set to True, fields marked as sensitive in `config.SENSITIVE_FIELDS` will be
redacted and replaced with `*****` in the library's debug logs."""

SENSITIVE_FIELDS = ["password", "key", "certificate", "token"]
"""List of sensitive field names to redact from the library's debug logs.
By default "password", "key", "certificate", "token", are set as
sensitive fields."""

_TREAT_AS_POST_COLLECTION: Dict[str, List[str]] = {
    "netapp_ontap.resources.lun": ["provisioning_options.count"],
    "netapp_ontap.resources.nvme_namespace": ["provisioning_options.count"],
}


def set_error_model(raise_api_errors: bool = True) -> None:
    """Set the error model for the library.

    By default, operations (GET, POST, PATCH, DELETE) will raise an exception if
    the response code from the host is >= 400. The exception object will contain
    the response so that it can be handled in the client code.

    Optionally, settings raise_api_errors to False will return the response and
    the client will be responsible for checking and handling any errors.

    Args:
        raise_api_errors: If set to true, the library will raise errors back to the
            application. If set to false, errors will not be raised and the
            application must verify the responses itself.
    """

    global RAISE_API_ERRORS  # pylint: disable=global-statement
    RAISE_API_ERRORS = raise_api_errors
