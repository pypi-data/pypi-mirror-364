# pylint: disable=line-too-long
"""
Copyright &copy; 2025 NetApp Inc. All rights reserved.

This module contains some of the common utility functions used in the library.
"""

import json
import logging
import os
import time
from functools import wraps
from ipaddress import IPv6Address, ip_address
from typing import Optional, Any, Callable, Dict, Tuple, List

import requests

from netapp_ontap import config, error
from netapp_ontap.error import NetAppRestError
from netapp_ontap.host_connection import HostConnection
from netapp_ontap.response import NetAppResponse

__all__ = ["poll"]

# prevent "No handlers" message if consumer application doesn't configure logging at all
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

DEBUG = os.getenv("DEBUG")
LOG_ALL_API_CALLS = os.getenv("LOG_ALL_API_CALLS")


def api(func: Callable) -> Callable:
    """A decorator for wrapping the library API calls.

    Args:
        func: The API function to call

    Returns:
        The result of the call if successful. Otherwise, if the library is configured to not raise errors, returns error responses.

    Raises:
        `netapp_ontap.error.NetAppRestError`: Will raise any API failure
        ErrorResponses if the library is configured to raise errors.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (MemoryError, OverflowError) as err:
            raise NetAppRestError(message=error.FILE_SIZE_WARNING) from err
        except requests.exceptions.RequestException as erro:
            return on_api_fail(erro)

    return wrapper


def on_api_fail(erro: requests.exceptions.RequestException) -> NetAppResponse:
    """Handles API failures according to the global library settings.

    Args:
        error: the error object corresponding to the request

    Returns:
        A `netapp_ontap.response.NetAppResponse` object if the library is configured to not raise errors.

    Raises:
        `netapp_ontap.error.NetAppRestError` if there is an API failure response
        and the library is configured to raise errors.
    """

    if config.RAISE_API_ERRORS:
        raise NetAppRestError(cause=erro) from None
    return NetAppResponse(erro.response)  # type: ignore


def poll(
    response: requests.Response,
    connection: Optional[HostConnection] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
) -> NetAppResponse:
    """Poll for a job to complete on the host.

    This function accepts an HTTP 202 response from the server and follows the
    associated job link. As long as the state of the job is not terminal,
    it continues retrieving the job and logs a status message as it changes.

    Args:
        response: The initial API response which contains 202 and the job link.
        connection: An optional `netapp_ontap.host_connection.HostConnection`
            object. This is required if there is no globally usable connection set
            for the library.
        timeout: Seconds to wait before timing out of a poll request. If set,
            the value overrides the timeout set in the connection. Otherwise, the
            timeout set in the connection is used.
        interval: Seconds to wait between REST API calls when checking the job
            status. If set, the value overrides the interval in the connection
            object. Otherwise, the interval set in connection object is used.

    Returns:
        The API response.

    Raises:
        `netapp_ontap.error.NetAppRestError`: If there was no connection available
            when the request was made (either passed in or set for the library),
            or if the job times out.
    """

    try:
        job_object = response.json()["job"]
        if "_links" in job_object:
            job_link = job_object["_links"]["self"]["href"]
        else:
            # this is a hard-coded hack. We should do better
            from netapp_deploy.resources import Job  # type: ignore # pylint: disable=import-outside-toplevel

            job_link = Job.from_dict(job_object).instance_location
    except (KeyError, ImportError, ValueError) as err:
        # It may have a job link if it is not a 202, but if it is a 202 and doesn't
        # have a job link, that seems certainly wrong
        if response.status_code == 202:
            raise NetAppRestError(
                "The API response does not have a valid job link"
            ) from err
        return NetAppResponse(response)

    return watch_job(
        job_link, connection=connection, timeout=timeout, interval=interval
    )


def watch_job(
    job_link: str,
    connection: Optional[HostConnection] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
) -> NetAppResponse:
    """The polling loop for the poll function. Takes in the job_link parsed from
    an API response

    Args:
        job_link: The string URL returned as part of a 202 status which
            gives the location of the running job
        connection: An optional `netapp_ontap.host_connection.HostConnection`
            object. This is required if there is no globally usable connection set
            for the library.
        timeout: Seconds to wait before timing out of a poll request. If set,
            the value overrides the timeout set in the connection. Otherwise, the
            timeout set in the connection is used.
        interval: Seconds to wait between REST API calls when checking the job
            status. If set, the value overrides the interval in the connection
            object. Otherwise, the interval set in connection object is used.

    Returns:
        The API response.

    Raises:
        `netapp_ontap.error.NetAppRestError`: If there was no connection available
            when the request was made (either passed in or set for the library),
            or if the job times out.
    """

    connection, timeout, interval = _get_job_param_defaults(
        connection, timeout, interval
    )

    job_complete = False
    last_message = None
    timeout_left = timeout
    while not job_complete and timeout_left > 0:
        response, response_body = _get_job_status(connection, job_link)
        response_body = response_body.get("record", response_body)
        current_message = response_body.get("message")
        if current_message != last_message:
            last_message = current_message
            LOGGER.info(
                "Job (%s): %s. Timeout remaining: %s.",
                response_body["state"],
                current_message,
                timeout_left,
            )

        try:
            job_complete = response_body["state"] in [
                "success",
                "failure",
                "cancelled",
                "expired",
            ]
        except KeyError as exc:
            raise NetAppRestError(
                "Unable to extract job state from the job response."
                f" Job response: {response_body}"
            ) from exc
        if not job_complete:
            time.sleep(interval)
            timeout_left -= interval

    if not job_complete:
        raise NetAppRestError(
            f"Job ({response_body['state']}): {response_body.get('message')}. "
            f"Polling timed out after {timeout} seconds."
        )

    if (
        response_body["state"] not in ["success", "cancelled"]
        and config.RAISE_API_ERRORS
    ):
        raise NetAppRestError(f"Job failed: {response_body['message']}")

    return NetAppResponse(response)


def _get_job_param_defaults(
    connection: Optional[HostConnection] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
) -> Tuple[HostConnection, int, int]:
    """Get the default parameters that should be used to monitor the job

    Args:
        connection: An optional `netapp_ontap.host_connection.HostConnection`
            object. This is required if there is no globally usable connection set
            for the library.
        timeout: Seconds to wait before timing out of a poll request. If set,
            the value overrides the timeout set in the connection. Otherwise, the
            timeout set in the connection is used.
        interval: Seconds to wait between REST API calls when checking the job
            status. If set, the value overrides the interval in the connection
            object. Otherwise, the interval set in connection object is used.

    Returns:
        The calculated parameters based on the input and the defaults

    Raises:
        `netapp_ontap.error.NetAppRestError`: If no valid values can be set
    """

    if not connection:
        host_context = HostConnection.get_host_context()
        if config.CONNECTION:
            connection = config.CONNECTION
        elif host_context:
            connection = host_context
    if not connection:
        raise NetAppRestError(
            "No connection was passed or globally set. In either case, provide a "
            "connection object or set a global connection object for the library."
        )
    if not timeout:
        timeout = connection.poll_timeout
    if not interval:
        interval = connection.poll_interval
    if not timeout or timeout < 0:
        raise NetAppRestError(
            "Invalid timeout value. The timeout must be a positive integer."
        )
    if not interval or interval < 0:
        raise NetAppRestError(
            "Invalid interval value. The interval must be a positive integer."
        )

    return connection, timeout, interval


def _get_job_status(
    connection: HostConnection, job_link: str
) -> Tuple[requests.Response, dict]:
    """Fetch and return the current job status.

    Args:
        connection: The connection object to send the request to
        job_link: The API path including the job ID to get info for

    Returns:
        The body of the API response that represents the current state of the job

    Raises:
        `netapp_ontap.error.NetAppRestError`: If the job status cannot be determined
            either because the API call was an error (> 399 status) or the response
            body was not in the right format.
    """

    url = f"{connection.origin}{job_link}"
    response = connection.session.get(url, params={"fields": "message,state,error"})
    try:
        response.raise_for_status()
        return response, response.json()
    except json.decoder.JSONDecodeError as exception:
        raise NetAppRestError(
            f"Unexpectedly failed to read the response body for job {job_link} as JSON."
            f" The response body was '{response.text}'."
        ) from exception
    except requests.exceptions.RequestException as exception:
        err_response = on_api_fail(exception)
        raise NetAppRestError(
            "Received an unexpected HTTP status while waiting for the job to"
            f" complete: ({err_response.http_response.status_code}) {err_response.http_response.text}"
        ) from exception


def _redact_sensitive_object(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields in a dictionary

    Args:
        obj (dict): dictionary to look through and redact

    Returns:
        dict: the input dictionary with redacted sensitive fields
    """
    if not isinstance(obj, dict):
        return obj
    for key, value in obj.items():
        if isinstance(value, str) and key.lower() in config.SENSITIVE_FIELDS:
            LOGGER.debug("Redacting the value of sensitive field '%s' from logs", key)
            obj[key] = "*****"
        elif isinstance(value, dict):
            obj[key] = _redact_sensitive_object(value)
    return obj


def _redact_sensitive_list(lst: List[Any], parent_name: str) -> List[Any]:
    """Redact sensitive fields in a list

    Args:
        lst (list): list of items to look through
        parent_name (str): name of the parent property

    Returns:
        list: the input list with redacted sensitive fields
    """
    list_to_return: List[Any] = []
    for item in lst:
        if isinstance(item, dict):
            list_to_return.append(_redact_sensitive_object(item))
        elif isinstance(item, list):
            list_to_return.append(_redact_sensitive_list(item, parent_name))
        elif isinstance(item, str) and parent_name in config.SENSITIVE_FIELDS:
            list_to_return.append("*****")
        else:
            list_to_return.append(item)
    return list_to_return


def redact_sensitive_fields(body: str) -> str:
    """Recursively go through the request/response body and overwrite all
    sensitive string fields with asterisk.


    Args:
        body (str): string representation of the request/response body

    Returns:
        str: the request/response body but with sensitive string fields redacted
    """
    try:
        body_dict = json.loads(body)
    except json.JSONDecodeError:
        # If the body is cannot be parsed using JSON, return it as is without redacting anything
        return body
    for key, value in body_dict.items():
        if isinstance(value, str) and key.lower() in config.SENSITIVE_FIELDS:
            LOGGER.debug("Redacting the value of sensitive field '%s' from logs", key)
            body_dict[key] = "*****"
        elif isinstance(value, dict):
            body_dict[key] = _redact_sensitive_object(value)
        elif isinstance(value, list):
            body_dict[key] = _redact_sensitive_list(value, key)
    return json.dumps(body_dict, indent=2, sort_keys=True)


def _is_ip_v6(ip_addr: str) -> bool:
    """Check if the used IP is IPv6"""
    try:
        return isinstance(ip_address(ip_addr), IPv6Address)
    except ValueError:
        return False
