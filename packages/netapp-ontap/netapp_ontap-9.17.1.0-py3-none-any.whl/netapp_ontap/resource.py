# pylint: disable=line-too-long
"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This module defines the base Resource class. This class is implemented by each
resource object for the system. The methods here allow the client application to
perform actions against the host (GET, POST, PATCH, DELETE) via its REST interface.
"""

# pylint: disable=too-many-lines

import collections.abc
import json
import logging
import operator
import re
import string
import time
from typing import (  # pylint: disable=unused-import
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
)
import urllib.parse
import datetime
from marshmallow import (  # type: ignore
    INCLUDE,
    RAISE,
    Schema,
    missing,
    post_load,
)
from marshmallow import fields as marshmallow_fields
from marshmallow.schema import SchemaMeta  # type: ignore
import requests
from requests_toolbelt.multipart import decoder  # type: ignore

from netapp_ontap import config, utils
from netapp_ontap.error import NetAppRestError
from netapp_ontap.host_connection import HostConnection
from netapp_ontap.response import NetAppResponse
from netapp_ontap.raw_resource import RawResource


# we don't really need to document the ResourceSchema class externally since no
# client application should use it directly
__all__ = ["Resource"]

# prevent "No handlers" message if consumer application doesn't configure logging at all
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class ResourceSchemaMeta(SchemaMeta, type):
    """This meta class sets __annotations__ on the schema instance that is created
    so that each of the schema's fields have typing info exposed. This is used in
    documentation generation.
    """

    def __new__(mcs, name, bases, attrs) -> "ResourceSchema":  # type: ignore
        """Construct the instance and then set the __annotations__ for each field
        that is declared for the schema
        """

        instance = super().__new__(mcs, name, bases, attrs)
        instance.__annotations__ = instance.__annotations__ = dict(
            instance._declared_fields.items()
        )  # pylint: disable=protected-access
        return instance

    def get_short_type_name(cls, field_name: str) -> str:
        """Return the short string representation of the type of the provided field"""

        if field_name not in cls._declared_fields:  # type: ignore
            raise NetAppRestError(
                f"{field_name} is not a valid field in {cls.__name__}"
            )

        def _get_nested_name(field) -> str:
            return field.nested.split(".")[-1].replace("Schema", "")

        def _get_scalar_name(type_) -> str:
            type_name = type_.__name__
            if type_ is marshmallow_fields.Str:
                type_name = "str"
            if type_ is marshmallow_fields.Boolean:
                type_name = "bool"
            if type_ is marshmallow_fields.Number:
                type_name = "float"
            return type_name

        field = cls._declared_fields[field_name]  # type: ignore
        type_ = type(field)
        type_name = type_.__name__

        if type_ is marshmallow_fields.Nested:
            type_name = _get_nested_name(field)
        elif type_ is marshmallow_fields.List:
            if isinstance(field.inner, marshmallow_fields.Nested):
                type_name = f"List[{_get_nested_name(field.inner)}]"
            else:
                type_name = f"List[{_get_scalar_name(type(field.inner))}]"
        else:
            type_name = _get_scalar_name(type_)

        return type_name


class ResourceSchema(Schema):
    """An abstract class which is the base of all resource schemas.

    A resource schema defines the fields of a resource with which the client can
    interact. When transforming to and from a REST request or response, the schema
    is responsible for validating and transforming the data.
    """

    patchable_fields = []  # type: List[str]
    """Only fields in this list will be considered when patching a resource"""

    postable_fields = []  # type: List[str]
    """Only fields in this list will be considered when posting a resource"""

    gettable_fields = []  # type: List[str]
    """The fields in this list may be queried and retrieved from the host"""

    @property
    def resource(self) -> "Type[Resource]":  # type: ignore
        """The resource class associated with this schema.

        Any time this schema is used to load/deserialize a dict, it will create
        an instance of the `netapp_ontap.resource.Resource` class provided.
        Typically, if the resource class name is "Foo", then the associated schema
        would be called "FooSchema".

        Returns:
            An instance of a `type` object which descends from `netapp_ontap.resource.Resource`
        """

    @post_load
    def make_resource(self, data: dict, **_kwargs) -> "Resource":
        """Automatically called by the library after we load data from a dict.

        A new instance of the associated `netapp_ontap.resource.Resource` is
        instantiated with all of the values which were verified and loaded.

        Args:
            data: A `dict` representing the state of a resource object
            _kwargs: Other arguments passed in by marshmallow (many and partial)

        Returns:
            A `netapp_ontap.resource.Resource` instance holding all of the state
            of the input dictionary.
        """

        return self.resource(**data)


class ImpreciseDateTime(marshmallow_fields.DateTime):
    """A customer DateTime field that serializes its value minus any microseconds
    that might exist on it. Microseconds are not accepted in a date-time formatted
    field in ONTAP.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        try:
            lossy_value = value.replace(microsecond=0)
            return super()._serialize(lossy_value, attr, obj, **kwargs)
        except Exception as erro:
            raise self.make_error(
                "invalid",
                input=value,
                obj_type=self.OBJ_TYPE,
            ) from erro


class Size(marshmallow_fields.Field):
    """A custom class that can interpret strings as integers assuming they are
    using a known suffix like G, M, K, etc"""

    SUFFIX_VALUES = {
        "K": 1024,
        "KB": 1024,
        "M": 1024**2,
        "MB": 1024**2,
        "G": 1024**3,
        "GB": 1024**3,
        "T": 1024**4,
        "TB": 1024**4,
        "P": 1024**5,
        "PB": 1024**5,
    }

    default_error_messages = {
        "invalid": (
            '"{input}" could not be interpreted as an integer or a valid size.'
            r" Valid size values are of the form \d+[KB|MB|GB|TB|PB]."
            "You must pass either a valid size string or an integer for {field}."
        )
    }

    def _serialize(self, value, attr, obj, **kwargs):
        return self._to_int(value, attr)

    def _deserialize(self, value, attr, data, **kwargs):
        return self._to_int(value, attr)

    def _to_int(self, value, attr):
        value = str(value).upper()
        size = 1
        for suffix, suffix_size in self.SUFFIX_VALUES.items():
            if value.endswith(suffix):
                value = value[: -len(suffix)]
                size = suffix_size
                break
        else:
            if value.endswith("B"):
                value = value[:-1]

        # now it must be parsable to an integer, or else it fails validation
        try:
            return int(value) * size
        except (ValueError, TypeError):
            raise self.make_error("invalid", input=value, field=attr) from None


class ResourceJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder for the Resource class"""

    def default(self, o):  # pylint: disable=method-hidden,arguments-differ
        if isinstance(o, Resource):
            return o.to_dict()
        if isinstance(o, datetime.datetime):
            return o.replace(microsecond=0).isoformat()
        return json.JSONEncoder.default(self, o)


class LazyFile:  # pylint: disable=too-few-public-methods
    """Class that handles open file handles"""

    def __init__(self, filename, mode):
        """Initialize variables"""
        self.filename = filename
        self.mode = mode

    def read(self):
        """Reads opened file, returns the object, and then closes the file"""
        # pylint: disable=unspecified-encoding
        with open(self.filename, self.mode) as file_name:
            return file_name.read()


class URLKeyFormatter(string.Formatter):
    """This formatter class is used to make sure that when location URLs are
    generated, the filled in keys are URL encoded to escape reserved characters
    """

    def convert_field(self, value, _conversion):
        """Override the string.Formatter.convert_field method to return the URL
        encoded form of the passed in value
        """
        return urllib.parse.quote_plus(str(value))


class Resource:  # pylint: disable=too-many-instance-attributes
    """An abstract class which is the base of all resources.

    A resource represents a moment in time snapshot of an object which exists on
    the connected host. This object can be fetched, updated, and returned to the
    host in order to perform meaningful work.
    """

    _schema = ResourceSchema
    _schema_instance = None  # type: ResourceSchema
    _schema_fields = None  # type: List[str]
    _path = ""
    _keys = []  # type: List[str]
    _post_form_data_parameters = {}  # type: dict
    _patch_form_data_parameters = {}  # type: dict

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the instance of the resource.

        Any keyword arguments are set on the instance as properties. For example,
        if the class was named 'MyResource', then this statement would be true:

            MyResource(name='foo').name == 'foo'

        Args:
            *args: Each positional argument represents a parent key as used in
                the URL of the object. That is, each value will be used to fill
                in a segment of the URL which refers to some parent object. The
                order of these arguments must match the order they are specified
                in the URL, from left to right.
            **kwargs: each entry will have its key set as an attribute name on
                the instance and its value will be the value of that attribute.
        """

        self._prevent_recurse = False
        self._connection = HostConnection.get_host_context()
        self._last_response = None  # type: Optional[NetAppResponse]
        self._required_queries = ""
        self.parent_keys = args
        self.response_files = []  # type: List[dict]
        self.response_parts = []  # type: List[Dict[str, Any]]
        if getattr(self.__class__, "_schema_instance", None) is None:
            self.__class__._schema_instance = (
                self._schema()
            )  # pylint: disable=protected-access
            self.__class__._schema_fields = list(  # pylint: disable=protected-access
                self._schema_instance.fields.keys()
            )
        for key, value in kwargs.items():
            self._attrsetter(key, value)
        self._last_state = self.to_dict()

    def __getitem__(self, name):
        """Emulate dictionary addressing"""

        return getattr(self, name)

    def __repr__(self) -> str:
        """Return the a representation of this resource as a dictionary"""

        return f"{self.__class__.__name__}({self.to_dict()})"

    def __dir__(self) -> List[str]:
        """Return a list of attributes that belong to the resource. This is useful
        for autocompletion of the otherwise dynamic fields since the list of
        attributes belongs to the associated schema object instead of the resource
        itself.

        https://docs.python.org/3/library/functions.html#dir
        """

        field_list = list(super().__dir__())
        if self._schema_fields:
            field_list += self._schema_fields
        return field_list

    def __getattribute__(self, name):
        """Here we will examine the name being retrieved. If it is a child resource
        then we will bind ourselves to it so that it has our context.
        """

        try:
            value = super().__getattribute__(name)
        except AttributeError:
            schema = super().__getattribute__("_schema_instance")
            if name in schema.fields:
                raise AttributeError(
                    f"The '{name}' field has not been set on the {super().__getattribute__('__class__').__name__}. "
                    f"Try refreshing the object by calling get() or set the field '{name}'."
                ) from None
            raise

        # Make sure we don't recurse into ourselves. That is, if we're already
        # trying to bind our keys into a sub object on property access, we don't
        # need to do it again.
        if super().__getattribute__("_prevent_recurse"):
            return value
        self._prevent_recurse = True

        # Get a list of the values of our keys and set them on our child object
        # so that they have access
        key_values = super().__getattribute__("_key_values")
        if isinstance(value, Resource):
            value.parent_keys = key_values
        if isinstance(value, collections.abc.Iterable) and not isinstance(value, str):
            for item in value:
                if isinstance(item, Resource):
                    item.parent_keys = key_values

        self._prevent_recurse = False
        return value

    @property
    def _key_values(self) -> List:
        """Return a list of values of the keys of the object.

        Returns:
            A list of values or Nones if the value is not currently set.
        """

        values = []
        for key in self._keys:
            try:
                values.append(operator.attrgetter(key)(self))
            except AttributeError:
                values.append(None)
        return values

    @property
    def path_keys(self) -> List[str]:
        """All keys that are not native to the object (foreign keys).

        In terms of URL, this would typically be all of the keys except for the
        last key. For example, if the path to the object was
        /api/storage/volumes/55be2443/snapshots/005056bb3fd7, then this value
        would be ['volume.uuid']

        Returns:
            A list of strings. Entries in the list are dotted which represent the object they belong to and the attribute on that object.
        """

        path_keys = []  # type: List[str]
        for key in self._keys:
            if "." in key:
                parent, prop = key.split(".")
                if f"{parent}[{prop}]" in self._path:
                    path_keys.append(key)
        return path_keys

    @property
    def _location(self) -> str:
        """The location of a resource is the API path to its collection.

        This can be seen in the Location header which is returned with any POST
        request. It is also the path for any GET/PATCH/DELETE on this object. It
        consists of fixed values and key values in the form /api/foos/{foo_key}/bars.

        Returns:
            A string representing the path to this resource's containing collection.
            When calling `netapp_ontap.resource.Resource.post`, this will be used
            as the target URL.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If not all required parent keys
                are present in the object.
        """

        try:
            format_keys = {}

            # if we were given parent_keys when the object was constructed, then
            # use those

            # URL encode the parent key values with character '/'
            if self.parent_keys:
                LOGGER.debug(
                    "Key values provided for the API endpoint: %s",
                    ", ".join(str(item) for item in self.parent_keys),
                )

            # If there are any None values in the list, clean them up
            parent_keys = [key for key in self.parent_keys if key is not None]

            if len(parent_keys) >= len(self.path_keys):
                for index, key in enumerate(self.path_keys):
                    if "." in key:
                        pieces = key.split(".")
                        format_keys[pieces[0]] = {pieces[1]: parent_keys[index]}
                    else:
                        format_keys[key] = parent_keys[index]
            else:
                representative = self
                if self._last_state:
                    representative = self.__class__.from_dict(self._last_state)
                for key in self.path_keys:
                    if "." in key:
                        key = key.split(".")[0]
                    format_keys[key] = operator.attrgetter(key)(representative)
            location = URLKeyFormatter().format(self._path, **format_keys)

            # If there are more parent keys than path keys, those should be child keys
            # appended to the url. This is an edge case where same endpoint is being
            # used for both GET instance and collection, which needs to be handled here.
            if (
                len(parent_keys) > len(self.path_keys)
                and self.__module__ == "netapp_ontap.resources.file_info"
            ):
                child_keys = "/".join(
                    [
                        urllib.parse.quote_plus(str(k))
                        for k in parent_keys[len(self.path_keys) :]
                    ],
                )
                location = "/".join([location, child_keys])

            return location
        except Exception as exc:
            msg = (
                f"Could not compute the location of the {self.__class__.__name__} collection."
                f"Values for {self.path_keys} are required."
            )
            raise NetAppRestError(message=msg, cause=exc) from None

    @property
    def instance_location(self) -> str:
        """Calculate this instance's location based on its key.

        For example:

            snapshot = Snapshot(volume=Volume(uuid='1234'), uuid='5678')
            assert snapshot._keys == ['volume.uuid', 'uuid']
            assert snapshot.volume.uuid == '1234'
            assert snapshot.uuid == '5678'
            assert snapshot.instance_location == '/api/storage/volumes/1234/snapshots/5678'

        Returns:
            A string representing the full path to this resource. When interacting with the host, this location is used as the URL.
        """

        if self.parent_keys and self.path_keys:
            if len(self.parent_keys) > len(self.path_keys):
                return self._location

        # a keyless resource looks more like a collection location
        if not self._keys:
            return self._location

        representative = self
        if self._last_state:
            representative = self.__class__.from_dict(self._last_state)
        keys = (
            self._keys.copy()
        )  # make a copy so that we can add svm.uuid the DNS resource
        if self.__module__ == "netapp_ontap.resources.dns" and not getattr(
            self, "uuid", None
        ):
            keys.append("svm.uuid")
        key_diff = set(keys) - set(self.path_keys)
        # get values for our keys if they are instance keys, preserving order
        key_vals = []
        for key in [key for key in keys if key in key_diff]:
            try:
                key_vals.append(
                    urllib.parse.quote_plus(
                        str(operator.attrgetter(key)(representative))
                    )
                )
            except AttributeError:
                pass

        if key_vals:
            return f"{self._location}/{'/'.join(key_vals)}"
        return self._location

    @classmethod
    def from_dict(
        cls, input_dict: dict, *args, strict: Optional[bool] = None
    ) -> "Resource":
        """Construct a resource from a dictionary.

        This is essentially a named constructor that returns a `netapp_ontap.resource.Resource`
        object from the values provided. It will verify that all required parent
        keys are present in the input.

        Args:
            input_dict: A set of key/value pairs which are set on the returned
                instance as attributes.
            *args: Each positional argument represents a parent key as used in
                the URL of the object. That is, each value will be used to fill
                in a segment of the URL which refers to some parent object. The
                order of these arguments must match the order they are specified
                in the URL, from left to right.
            strict: If set to True, any value in the input dictionary that is
                not part of the defined schema will cause an exception to be
                raised. If set to False, any value in the input schema will be
                accepted and set as a member of the object. If left unset, the
                library default set in netapp_ontap.config.STRICT_FIELD_ACCEPTANCE
                will be used.

        Returns:
            A resource object that can be used to interact with the host and contains the data from the input dictionary.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If not all required parent keys
                are present in the input or extra input is provided and strict
                is set to True.
        """

        if strict is None:
            strict = config.STRICT_FIELD_ACCEPTANCE

        for field in input_dict.keys():
            if isinstance(input_dict[field], datetime.datetime):
                input_dict[field] = input_dict[field].isoformat()

        if getattr(cls, "_schema_instance", None) is None:
            cls._schema_instance = cls._schema()

        unknown_policy = RAISE if strict else INCLUDE
        try:
            if cls.__module__ == "netapp_ontap.resources.software":
                input_dict = _cluster_software_fix(input_dict)
            resource = cls._schema_instance.load(input_dict, unknown=unknown_policy)
        except Exception as exc:
            raise NetAppRestError(cause=exc) from None

        resource.__init__(*args)  # pylint: disable=unnecessary-dunder-call
        return resource

    def to_dict(self, only: Optional[tuple] = None) -> dict:
        """Return a dictionary representing the object (and its sub-objects).

        Args:
            only: If a subset of fields are desired instead of all fields belonging
                to this object, `only` may be passed as a tuple of strings.
                Strings in this tuple can reference nested fields by separating
                nested levels using '.'

        Returns:
            A dictionary representing the state of this object and any child objects it may contain.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the current values stored in
                the resource don't match the schema defined for the resource, then
                an error will be raised. For example, if a field is supposed to
                be an integer and a non-integer value is set on it.
        """

        def unflatten_dict(data, keys: list):
            if not keys:
                return data
            current_key = keys.pop(0)
            try:
                new_data = data[current_key]
            except KeyError as exc:
                raise NetAppRestError(
                    message=f"Property {current_key} does not exist in {data}",
                    cause=exc,
                ) from None
            return {current_key: unflatten_dict(new_data, keys)}

        def update(full_dict, new_dict):
            for key, value in new_dict.items():
                if isinstance(value, dict):
                    full_dict[key] = update(full_dict.get(key, {}), value)
                else:
                    full_dict[key] = value
            return full_dict

        try:
            data = self._schema_instance.dump(self)
            if only:
                filtered_dict: Dict[str, Any] = {}
                for item in only:
                    nested_keys = item.split(".")
                    path_dict = unflatten_dict(data, nested_keys)
                    update(filtered_dict, path_dict)
                return filtered_dict
            return data
        except Exception as exc:
            raise NetAppRestError(cause=exc) from None

    def get_connection(self) -> HostConnection:
        """Returns the `netapp_ontap.host_connection.HostConnection` for this object.

        If there is a `netapp_ontap.host_connection.HostConnection` active as the
        current context (i.e. using a with statement), then that connection will
        be returned. Second, if a connection has been associated with this resource
        (by calling `netapp_ontap.resource.Resource.set_connection`), then that
        connection will be returned. Finally, it will return the connection that
        is associated with `netapp_ontap.config.CONNECTION`.

        Returns:
            A connection to be used for API calls.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If there is no connection
                available to use either set on the object or on the library.
        """

        host_context = HostConnection.get_host_context()

        if self._connection:
            return self._connection
        if host_context is not None:
            return host_context
        if config.CONNECTION:
            return config.CONNECTION

        values = [getattr(self, key, "") for key in self._keys]
        raise NetAppRestError(
            f"No connection is setup for {self.__class__.__name__} {','.join(values)}. Either call set_connection() on"
            " the resource or set a global connection object for the library."
        )

    def set_connection(self, connection: HostConnection) -> None:
        """Sets a HostConnection object on the resource.

        This connection will be used for all host operation (GET, PATCH, etc.)
        and overrides any connection that might be set at the library level.

        Args:
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for all future API calls on this object.
        """

        self._connection = connection

    def get_collection_url(self, connection: Optional[HostConnection] = None) -> str:
        """Return the URL for collection-based actions (GET, PATCH, DELETE).

        Args:
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Returns:
            A URL to perform the action on in the form of a string.
        """

        host_context = HostConnection.get_host_context()
        if connection:
            self.set_connection(connection)
        elif host_context is not None:
            self.set_connection(host_context)

        return f"{self.get_connection().origin}{self._location}"

    @classmethod
    @utils.api
    def _get_collection(
        cls,
        *args,
        connection: Optional[HostConnection] = None,
        max_records: Optional[int] = None,
        raw: bool = False,
        **kwargs,
    ) -> Iterable[Union["Resource", "RawResource"]]:
        """Fetch a list of all objects of this type from the host.

            This is a lazy fetch, making API calls only as necessary when the result
            of this call is iterated over. For instance, if max_records is set to 5,
            then iterating over the collection causes an API call to be sent to the
            server once for every 5 records. If the client stops iterating before
            getting to the 6th record, then no additional API calls are made.

        Args:
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to get the collection of bars
                for a particular foo, the foo.name value should be passed.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            max_records: The maximum number of records to return per call
            raw: return a list of `netapp_ontap.resource.RawResource` objects
                that require to be promoted before any RESTful operations can be
                used on them. Setting this argument to True makes get_collection
                substantially quicker when many records are returned from the server.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host.

        Returns:
            A list of `netapp_ontap.resource.Resource` objects

        Raises:
            `netapp_ontap.error.NetAppRestError`: If there is no connection
                available to use either passed in or on the library. This would
                be not be raised when get_collection() is called, but rather
                when the result is iterated.
        """

        params = dict(kwargs)
        params["max_records"] = max_records
        sample = cls.from_dict({}, *args)
        url = sample.get_collection_url(connection=connection)
        try:
            while url:
                response = sample.get_connection().session.get(url, params=params)
                response.raise_for_status()
                body = response.json()
                next_link = body.get("_links", {}).get("next", {}).get("href", None)
                if next_link:
                    url = f"{sample.get_connection().origin}{next_link}"
                    # the next link will give us all our params back, so don't
                    # add them to the URL a second time
                    params = {}
                else:
                    url = ""

                for record in body.get("records", []):
                    obj: Union[Resource, RawResource, None] = None
                    if raw:
                        obj = RawResource(record, cls, *args)
                    else:
                        obj = cls.from_dict(record, *args)
                    if connection is not None:
                        obj.set_connection(connection)
                    yield obj
        except requests.exceptions.RequestException as erro:
            # our @utils.api wrapper cannot help us generically catch this error
            # since this is a generator function and not a normal function
            utils.on_api_fail(erro)

    @classmethod
    def _count_collection(
        cls, *args, connection: Optional[HostConnection] = None, **kwargs
    ) -> int:
        """This calls GET on the object to determine the number of records. It
           is more efficient than calling get_collection() because it will not
           construct any objects. Query parameters can be passed in as kwargs
           to determine a count of objects that match some filtered criteria.

        Args:
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to get the count of bars
                for a particular foo, the foo.name value should be passed.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host. These query parameters can affect the count. A
                return_records query param will be ignored.

        Returns:
            On success, returns an integer count of the objects of this type.
            On failure, returns -1.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400, or if there is no connection available to use either
                passed in or on the library.
        """

        kwargs["return_records"] = "false"
        sample = cls.from_dict({}, *args)
        url = sample.get_collection_url(connection=connection)

        # we don't return a NetAppResponse, so handle errors manually
        try:
            response = sample.get_connection().session.get(url, params=kwargs)
            response.raise_for_status()
            return response.json().get("num_records", -1)
        except requests.exceptions.RequestException as erro:
            if config.RAISE_API_ERRORS:
                raise NetAppRestError(cause=erro) from None
            return -1

    # pylint: disable=too-many-arguments
    @classmethod
    @utils.api
    def _patch_collection(
        cls,
        body: dict,
        *args,
        records: Optional[Iterable["Resource"]] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Patch all objects in a collection which match the given query.

        All records on the host which match the query will be patched with the
        provided body.

        Args:
            body: A dictionary of name/value pairs to set on all matching members
                of the collection. The body argument will be ignored if records
                is provided.
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to patch the collection of bars
                for a particular foo, the foo.name value should be passed.
            records: Can be provided in place of a query. If so, this list of objects
                will be patched on the host.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host. Only resources matching this query will be patched.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        sample = cls.from_dict({}, *args)
        params = dict(kwargs)
        url = sample.get_collection_url(connection=connection)
        responses = []
        if records:
            record_data = _get_patch_collection_record_data(records)
            response = sample.get_connection().session.patch(
                url,
                data=record_data,
                params=params,
            )
            response.raise_for_status()
            responses.append(response)
        else:
            responses = _get_patch_collection_responses(url, params, sample, body)

        if poll:
            responses.extend(
                [
                    cls._check_collection_jobs(
                        r,
                        *args,
                        poll_interval=poll_interval,
                        poll_timeout=poll_timeout,
                        connection=connection,
                    )
                    for r in responses
                ]
            )

        return NetAppResponse(responses[-1], connection=connection)

    # pylint: disable=too-many-arguments,too-many-locals
    @classmethod
    @utils.api
    def _delete_collection(
        cls,
        *args,
        records: Optional[Iterable["Resource"]] = None,
        body: Optional[Union["Resource", dict]] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Delete all objects in a collection which match the given query.

        All records on the host which match the query will be deleted.

        Args:
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to delete the collection of bars
                for a particular foo, the foo.name value should be passed.
            records: Can be provided in place of a query. If so, this list of objects
                will be deleted from the host.
            body: The body of the delete request. This could be a Resource instance
                or a dictionary object.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host. Only resources matching this query will be deleted.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        sample = cls.from_dict({}, *args)
        params = dict(kwargs)
        url = sample.get_collection_url(connection=connection)
        responses = []
        if records:
            response = sample.get_connection().session.delete(
                url,
                json={
                    "records": [
                        r.to_dict(
                            only=tuple(r._keys)  # pylint: disable=protected-access
                        )
                        for r in records
                    ]
                },
                params=params,
            )
            response.raise_for_status()
            responses.append(response)
        else:
            while url:
                body_data = sample._get_body_data(  # pylint: disable=protected-access
                    body
                )
                response = sample.get_connection().session.delete(
                    url,
                    json=body_data,
                    params=params,
                )
                response.raise_for_status()
                responses.append(response)
                next_link = (
                    response.json().get("_links", {}).get("next", {}).get("href", None)
                )
                if next_link:
                    url = f"{sample.get_connection().origin}{next_link}"
                    # the next link will give us all our params back, so don't
                    # add them to the URL a second time
                    params = {}
                else:
                    url = ""

        if poll:
            responses.extend(
                [
                    cls._check_collection_jobs(
                        r,
                        *args,
                        poll_interval=poll_interval,
                        poll_timeout=poll_timeout,
                        connection=connection,
                    )
                    for r in responses
                ]
            )

        return NetAppResponse(responses[-1], connection=connection)

    # pylint: disable=too-many-arguments,too-many-locals
    @classmethod
    @utils.api
    def _post_collection(
        cls,
        records: Iterable["Resource"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> Union[List["Resource"], NetAppResponse]:
        """Send this collection of objects to the host as a creation request.

        Args:
            records: A list of `netapp_ontap.resource.Resource` objects to send
                to the server to be created.
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to create a bar for a particular
                foo, the foo.name value should be passed.
            hydrate: If set to True, after the response is received from
                the call, a a GET call will be made to refresh all fields of each
                object. When hydrate is set to True, poll must also be set to True.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host. Only resources matching this query will be patched.

        Returns:
            A list of `netapp_ontap.resource.Resource` objects matching the provided
            type which have been created by the host and returned. This is _not_
            the same list that was provided, so to continue using the object, you
            should save this list. If poll is set to False, then a `netapp_ontap.response.NetAppResponse`
            object is returned instead.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        sample = cls.from_dict({}, *args)
        body_data = {
            "records": [
                r._get_postable_data()  # pylint: disable=protected-access
                for r in records
            ]
        }
        url = sample.get_collection_url(connection=connection)
        post_response = sample.get_connection().session.post(
            url,
            json=body_data,
            params=dict(kwargs),
        )
        post_response.raise_for_status()
        if not poll:
            return NetAppResponse(post_response, connection=connection)

        job_response = cls._check_collection_jobs(
            post_response,
            *args,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            connection=connection,
        )
        # If empty response is returned from _check_collection_jobs, then no records could be identified
        # as part of the job. Log a warning and return an empty list.
        if job_response.status_code is None or job_response.json() == {}:
            LOGGER.warning(
                "No records could be identified as part of post_collection. Returning an empty list."
            )
            return []

        return_resources = []
        for resource_dict in job_response.json().get("records", []):
            resource = cls.from_dict(resource_dict, *args)
            if connection is not None:
                resource.set_connection(connection)
            return_resources.append(resource)

        if hydrate:
            for resource in return_resources:
                resource.get()
        return return_resources

    @classmethod
    def _check_collection_jobs(
        cls,
        response: requests.Response,
        *args,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
    ) -> requests.Response:
        """Checks to see if the collection operation resulted in any jobs being
        launched on the server. If so, wait for their results.

        Args:
            response: The response received from the API after all of the collection
                operations are complete
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to create a bar for a particular
                foo, the foo.name value should be passed.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If one or more jobs have an
                ending state of "failed"
        """

        response_body = response.json()

        # if the response body has a single "job" object, then the request was
        # made with ONTAP's multi-record operation functionality. In this case,
        # we need to query the status of that job to see the sub-jobs
        #
        # else, it might have a "jobs" array. If so, let's check each subjob
        # for its status
        #
        # else it was a synchronous response, so nothing to do
        if "jobs" in response_body:
            return cls._check_query_record_response(
                response,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
                connection=connection,
            )
        if "job" in response_body:
            return cls._check_multi_record_response(
                response,
                *args,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
                connection=connection,
            )
        return response

    @classmethod
    def _check_query_record_response(
        cls,
        response: requests.Response,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
    ) -> requests.Response:
        """Checks the status of any jobs that were run as part of a collection
        query operation. If any of the jobs failed, this function will raise an
        exception with the error message of all of the failures (if more than 1).

        Args:
            response: The response received from the API after all of the collection
                operations are complete
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If one or more jobs have an
                ending state of "failed"
        """

        response_body = response.json()
        errors = []
        for job in response_body["jobs"]:
            job_link = job.get("_links", {}).get("self", {}).get("href")
            if not job_link:
                continue
            try:
                utils.watch_job(
                    job_link,
                    interval=poll_interval,
                    timeout=poll_timeout,
                    connection=connection,
                )
            except NetAppRestError as exc:
                # collect all error messages
                errors.append(str(exc))

        if errors:
            raise NetAppRestError(f"One or more jobs failed: {errors}")

        return response

    @classmethod
    def _check_multi_record_response(
        cls,
        response: requests.Response,
        *args,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
    ) -> requests.Response:
        """Checks the status of the multi-record job (if there was one) and all
        of the sub-jobs that it contains.

        Args:
            response: The response received from the API after all of the collection
                operations are complete
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to create a bar for a particular
                foo, the foo.name value should be passed.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If one or more jobs have an
                ending state of "failed"
        """

        response_body = response.json()
        job_results_url = (
            response_body.get("job", {})
            .get("_links", {})
            .get("results", {})
            .get("href")
        )
        job_link = (
            response_body.get("job", {}).get("_links", {}).get("self", {}).get("href")
        )
        if not job_link:
            return response

        try:
            utils.watch_job(
                job_link,
                interval=poll_interval,
                timeout=poll_timeout,
                connection=connection,
            )
        except NetAppRestError as err:
            # if the job failed, we should look at the job_results via the resource
            # specific URL since that's where the meaningful failure messages will be
            # But if there is no job_results_url, then we should raise the exception
            if not job_results_url:
                raise err
        # Job succeeded but we don't have access to the results, we can't get the records
        if not job_results_url:
            # return an empty response with a None status code
            return requests.Response()

        job_results_query = urllib.parse.urlparse(job_results_url).query
        job_results_uuid = urllib.parse.parse_qs(job_results_query)["job_results_uuid"][
            0
        ]
        sample = cls.from_dict({}, *args)
        params = {"job_results_uuid": job_results_uuid}
        connected_url = sample.get_collection_url(connection=connection)
        response = sample.get_connection().session.get(connected_url, params=params)
        response.raise_for_status()

        # check to see if there were any errors reported. If so, construct a single
        # error message and raise an exception
        cls._check_multi_record_error(response)

        return response

    @classmethod
    def _check_multi_record_error(cls, response: requests.Response):
        """If there were any errors, create a new error message and raise it

        Args:
            response: The response to examine

        Raises:
            `netapp_ontap.error.NetAppRestError`: If there are any errors while
                the resources were being created or rolled back
        """

        response_body = response.json()
        errors = response_body.get("errors", [])
        rollback_errors = response_body.get("rollback_errors", [])
        error_message = ""
        for error_list in [("Operation", errors), ("Rollback", rollback_errors)]:
            if error_list[1]:
                error_message += f"{error_list[0]} errors: "
                for error in error_list[1]:
                    error_message += error["message"] + "\n"
        error_message = error_message.strip()
        if error_message:
            raise NetAppRestError(f"One or more jobs failed: {error_message}")

    @classmethod
    @utils.api
    def _find(
        cls, *args, connection: Optional[HostConnection] = None, **kwargs
    ) -> Optional["Resource"]:
        """Find an instance of an object on the host given a query.

        The host will be queried with the provided key/value pairs to find a
        matching resource. If 0 are found, None will be returned.
        If more than 1 is found, an error will be raised or returned.
        If there is exactly 1 matching record, then it will be returned.

        Args:
            *args: Each entry represents a parent key which is used to build the
                path to the child object. If the URL definition were
                /api/foos/{foo.name}/bars, then to find a bar for a particular
                foo, the foo.name value should be passed.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host.

        Returns:
            A `netapp_ontap.resource.Resource` object containing the
            details of the object or None if no matches were found.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned more
                than 1 matching resource.
        """
        if "fields" not in kwargs:
            kwargs["fields"] = "*"
        results = list(
            cls._get_collection(*args, connection=connection, **_flatten_dict(kwargs))
        )
        if not results:
            return None
        if len(results) != 1:
            msg = (
                f"Only 1 resource was expected. Found {len(results)} with query "
                f"{','.join(f'{key}={value}' for key, value in kwargs.items())}"
            )
            raise NetAppRestError(message=msg)

        resource = results[0]
        if connection is not None:
            resource.set_connection(connection)

        return resource

    @utils.api
    def _get(self, **kwargs) -> NetAppResponse:
        """Fetch the details of the object from the host.

        Requires the keys to be set (if any). After returning, new or changed
        properties from the host will be set on the instance.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status code >= 400
            or if not all of the keys required are present and config.STRICT_GET has been set to True.
        """

        url = f"{self.get_connection().origin}{self.instance_location}"

        # If ONTAP returned query parameters in the Location header from a post(),
        # then we should consider those required for all future get() calls.
        for query in urllib.parse.parse_qsl(self._required_queries):
            kwargs[query[0]] = str(query[1])

        if config.STRICT_GET:
            key_diff = set(self._keys) - set(self.path_keys)
            for key in [key for key in self._keys if key in key_diff]:
                try:
                    operator.attrgetter(key)(self)
                except AttributeError:
                    raise NetAppRestError(
                        message=f"Not all of the keys required are present. Missing a value for '{key}'."
                    ) from None

        response = self.get_connection().session.get(url, params=kwargs)
        response.raise_for_status()
        if response.content.decode("utf-8").startswith("{"):
            self._parse_json_response(response)
        else:
            self._parse_multipart_response(response)
        self._set_last_state()
        self._last_response = NetAppResponse(response)
        return self._last_response

    @utils.api
    def _post(  # pylint: disable=too-many-positional-arguments
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Send this object to the host as a creation request.

        Args:
            hydrate: If set to True, after the response is received from
                the call, a a GET call will be made to refresh all fields of the object.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will normally be sent as query parameters
                to the host. If any of these pairs are parameters that are sent as formdata then
                only parameters of that type will be accepted and all others will be discarded.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        my_connection = connection if connection is not None else self.get_connection()
        url = f"{my_connection.origin}{self._location}"
        body_data = self._get_postable_data()
        # trim out any keys from the body which are present as part of the path
        for key in self.path_keys:
            body_data.pop(key.split(".")[0], None)

        self._check_for_post_collection_treatment()  # pylint: disable=protected-access

        # holds a list of valid formdata parameters that the user passed in -
        # if user tries to pass parameters that aren't valid they will just be ignored
        valid_formdata_parameters_list = set()  # type: ignore
        if hasattr(self, "_post_form_data_parameters"):
            valid_formdata_parameters_list = set(self._post_form_data_parameters) & set(
                kwargs
            )

        # if no valid formdata parameters are passed into the request - send application/json request
        if not valid_formdata_parameters_list:
            response = my_connection.session.post(
                url,
                data=json.dumps(
                    body_data, cls=ResourceJSONEncoder, ensure_ascii=False
                ).encode("utf-8"),
                params=kwargs,
                headers={"Content-Type": "application/json"},
            )

        # if valid formdata parameters are passed into the request - send multipart/form-data request
        else:
            file_objects = self._populate_file_objects(kwargs, "post")
            kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in valid_formdata_parameters_list
            }
            response = my_connection.session.post(
                url,
                files=file_objects,
                params=kwargs,
                stream=True,
            )
        response.raise_for_status()

        if not "Location" in response.headers:
            # if a resource wasn't created, this must be some sort of action
            if poll:
                return utils.poll(
                    response,
                    connection=my_connection,
                    interval=poll_interval,
                    timeout=poll_timeout,
                )
            return NetAppResponse(response, connection=my_connection)
        self._set_keys(response, interval=poll_interval, timeout=poll_timeout)
        self._clone_from_dict(self.to_dict())
        self._set_last_state()
        self._last_response = NetAppResponse(response, connection=my_connection)

        if poll:
            return self._poll(
                hydrate=hydrate,
                interval=poll_interval,
                timeout=poll_timeout,
                connection=my_connection,
            )
        return self._last_response

    @utils.api
    def _patch(  # pylint: disable=too-many-positional-arguments
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Send the difference in the object's state to the host as a modification request.

        Calculates the difference in the object's state since the last time we
        interacted with the host and sends this in the request body.

        Args:
            hydrate: If set to True, after the response is received from
                the call, a a GET call will be made to refresh all fields of the object.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will normally be sent as query parameters
                to the host. If any of these pairs are parameters that are sent as formdata then
                only parameters of that type will be accepted and all others will be discarded.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        my_connection = connection if connection is not None else self.get_connection()
        url = f"{my_connection.origin}{self.instance_location}"

        # holds a list of valid formdata parameters that the user passed in - if user tries to pass parameters that aren't valid they will just be ignored
        valid_formdata_parameters_list = set()  # type: ignore
        if hasattr(self, "_patch_form_data_parameters"):
            valid_formdata_parameters_list = set(
                self._patch_form_data_parameters
            ) & set(kwargs)

        # if no valid formdata parameters are passed into the request - send application/json request
        if not valid_formdata_parameters_list:
            response = my_connection.session.patch(
                url,
                data=json.dumps(
                    self._get_changed_data(),
                    cls=ResourceJSONEncoder,
                    ensure_ascii=False,
                ).encode("utf-8"),
                params=kwargs,
                headers={"Content-Type": "application/json"},
            )
        else:
            file_objects = self._populate_file_objects(kwargs, "patch")
            kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in valid_formdata_parameters_list
            }
            response = my_connection.session.patch(
                url,
                files=file_objects,
                params=kwargs,
                stream=True,
            )
        response.raise_for_status()
        self._set_last_state()
        self._last_response = NetAppResponse(response, connection=my_connection)

        if poll:
            return self._poll(
                hydrate=hydrate,
                interval=poll_interval,
                timeout=poll_timeout,
                connection=my_connection,
            )
        return self._last_response

    @utils.api
    def _delete(  # pylint: disable=too-many-positional-arguments
        self,
        body: Optional[Union["Resource", dict]] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: Optional[HostConnection] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Send a deletion request to the host for this object.

        Args:
            body: The body of the delete request. This could be a Resource instance
                or a dictionary object.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        my_connection = connection if connection is not None else self.get_connection()

        url = f"{my_connection.origin}{self.instance_location}"
        response = my_connection.session.delete(
            url, json=self._get_body_data(body), params=kwargs
        )
        response.raise_for_status()
        self._last_response = NetAppResponse(response, connection=my_connection)

        if poll:
            return self._poll(
                interval=poll_interval, timeout=poll_timeout, connection=my_connection
            )
        return self._last_response

    # pylint: disable=too-many-arguments
    @utils.api
    def _action(  # pylint: disable=too-many-positional-arguments
        self,
        path: str,
        body: Optional[Union["Resource", dict]] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs,
    ) -> NetAppResponse:
        """Perform a custom action on this resource which is not a simple CRUD action

        Args:
            path: The action verb for this request. This will be added as a postfix
                to the instance location of the resource.
            body: The body of the action request. This should be a Resource instance.
                The connection and URL will be determined based on the values from
                this object.
            poll: If set to True, the call will not return until the
                asynchronous job on the host has completed. Has no effect if the
                host did not return a job response.
            poll_interval: If the operation returns a job, this specifies how
                often to query the job for updates.
            poll_timeout: If the operation returns a job, this specifies how
                long to continue monitoring the job's status for completion.
            **kwargs: Any key/value pairs passed will be sent as query parameters
                to the host.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        url = f"{self.get_connection().origin}{self.instance_location}/{path}"

        # holds a list of valid formdata parameters that the user passed in - if user tries to pass parameters that aren't valid they will just be ignored
        valid_formdata_parameters_list = set()  # type: ignore
        if hasattr(self, "_action_form_data_parameters"):
            valid_formdata_parameters_list = set(
                self._action_form_data_parameters
            ) & set(kwargs)

        # if no valid formdata parameters are passed into the request - send application/json request
        if not valid_formdata_parameters_list:
            response = self.get_connection().session.post(
                url, json=self._get_body_data(body), params=kwargs
            )

        # if valid formdata parameters are passed into the request - send multipart/form-data request
        else:
            file_objects = self._populate_file_objects(kwargs, "action")
            kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in valid_formdata_parameters_list
            }
            response = self.get_connection().session.post(
                url, files=file_objects, params=kwargs, stream=True
            )

        response.raise_for_status()
        if poll:
            return utils.poll(
                response,
                connection=self.get_connection(),
                interval=poll_interval,
                timeout=poll_timeout,
            )
        return NetAppResponse(response, connection=self.get_connection())

    @utils.api
    def poll(
        self,
        hydrate: bool = False,
        timeout: Optional[int] = None,
        interval: Optional[int] = None,
        connection: Optional[HostConnection] = None,
    ) -> NetAppResponse:
        """Wait for a job which is running for this resource is complete.

        This function may be called when the client knows there was a job
        started after a previous API call was made for this object. It will go
        get the state of that job and then block until it is complete. If hydrate
        is set to True, this function will continue to block until a subsequent
        GET call on the resource completes and refreshes the attributes of the
        resource.

        Args:
            hydrate: If set to True, after the response is received from
                the call, a GET call will be made to refresh all fields of the object.
            timeout: Seconds to wait before timing out of poll request. If set,
                the value overrides the timeout set in the active HostConnection.
                Otherwise, the timeout set in the active HostConnection is used.
            interval: How long to wait between making REST API calls to check the
                job status. If set, the value overrides the interval set in the
                active HostConnection. Otherwise, the interval set in the active
                HostConnection is used.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        return self._poll(
            hydrate=hydrate, timeout=timeout, interval=interval, connection=connection
        )

    def _poll(
        self,
        hydrate: bool = False,
        timeout: Optional[int] = None,
        interval: Optional[int] = None,
        connection: Optional[HostConnection] = None,
    ) -> NetAppResponse:
        """Non-decorated internal implementation of the poll function. Used for
        calling from other actions (post, patch).

        Args:
            hydrate: If set to True, after the response is received from
                the call, a GET call will be made to refresh all fields of the object.
            timeout: Seconds to wait before timing out of poll request. If set,
                the value overrides the timeout set in the active HostConnection.
                Otherwise, the timeout set in the active HostConnection is used.
            interval: How long to wait between making REST API calls to check the
                job status. If set, the value overrides the interval set in the
                active HostConnection. Otherwise, the interval set in the active
                HostConnection is used.
            connection: The `netapp_ontap.host_connection.HostConnection` object
                to use for this API call. If unset, tries to use the connection
                which is set globally for the library or from the current context.

        Returns:
            A `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400 or if there has not been any requests made for this
                resource (and therefore no jobs to track).
        """

        my_connection = connection if connection is not None else self.get_connection()
        if not self._last_response:
            values = [getattr(self, key, "") for key in self._keys]
            raise NetAppRestError(
                message=f"No requests have been made for {self.__class__.__name__} {','.join(values)}."
            )
        response = self._last_response.poll(
            connection=my_connection, timeout=timeout, interval=interval
        )
        if hydrate:
            old_connection = self._connection
            self._connection = my_connection
            response = self._get(fields="*")
            self._connection = old_connection
        self._set_last_state()
        self._last_response = response
        return self._last_response

    def _parse_json_response(self, response: requests.Response) -> None:
        """Parse the response as JSON and update the resource state"""

        response_dict = response.json()
        if "record" in response_dict:
            response_dict = response_dict["record"]
        elif "records" in response_dict:
            if response_dict.get("num_records", 0) == 1:
                response_dict = response_dict["records"][0]
            else:
                num_records = (
                    "more than one record"
                    if response_dict.get("num_records", 0) > 1
                    else "no records"
                )
                raise NetAppRestError(
                    message=f"Received {num_records} in the response {self.__class__.__name__}."
                )
        self._clone_from_dict(response_dict)

    def _parse_multipart_response(self, response: requests.Response) -> None:
        """Parse the response as a multipart/form-data response and set the
        response_files and response_parts members accordingly"""

        multipart_data = decoder.MultipartDecoder.from_response(response)
        for part in multipart_data.parts:
            content_disposition = part.headers[b"Content-Disposition"].decode("utf-8")
            content_type = content_disposition.split(";")[0].strip()
            part_name = re.search(r'name="(.+?)"', content_disposition)
            file_name = re.search(r'filename="(.+?)"', content_disposition)
            part_data = {
                "name": part_name[1] if part_name else "<unknown>",
                "content": part.content,
            }
            if file_name:
                part_data["filename"] = file_name[1]
            self.response_parts.append(part_data)

            if content_type == "attachment" or file_name:
                file_data = dict(part_data)
                file_data["name"] = file_name[1] if file_name else "unknown"
                file_data.pop("filename", None)
                self.response_files.append(file_data)

    def _get_body_data(self, body: Optional[Union["Resource", dict]]) -> dict:
        """Returns a dictionary meant to be used as the body of the request. If
        None is provided, then an empty dict is returned. Any keys for the resource
        are trimmed out of the body dict in case they are provided.
        """

        if body is not None:
            if isinstance(body, Resource):
                body_data = body.to_dict()
            else:
                body_data = dict(body)
            # trim out any keys from the body which are present as part of the path
            for key in self.path_keys:
                body_data.pop(key.split(".")[0], None)
        else:
            body_data = {}

        return body_data

    def _clone_from_dict(self, input_dict: dict) -> None:
        """Refresh almost all fields of the object by replacing with just fetched
        version. We should keep the connection around though.

        Args:
            input_dict: We read the object from the response, inflate it and then
                steal all of its fields.
        """

        connection = self._connection
        parent_keys = self.parent_keys
        req_queries = self._required_queries
        self.__dict__ = (
            self.from_dict(  # pylint: disable=attribute-defined-outside-init
                input_dict
            ).__dict__
        )
        self.parent_keys = parent_keys
        self._connection = connection
        self._required_queries = req_queries

    def _set_keys(
        self,
        post_response: requests.Response,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """Parse the Location header from a response and set keys on the object.

        Based on the response to a POST call, we should set the keys on our
        instance so that the user can use this for GET/PATCH/DELETE.

        If the Location header contains a query string, this method will loop for
        10 seconds (waiting 1 second inbetween) and follow that query to try and
        determine the full location of the resource.

        Args:
            post_response: The response returned from a POST API call to the host
            interval: Seconds to wait between REST API calls when checking the job
                status. If set, the value overrides the interval in the connection
                object. Otherwise, the interval set in connection object is used.
            timeout: Seconds to wait before timing out of a poll request. If set,
                the value overrides the timeout set in the connection. Otherwise, the
                timeout set in the connection is used.
        Raises:
            `netapp_ontap.error.NetAppRestError`: Will be raised if the object's
                final location could not be determined within the timeout.
        """

        location = post_response.headers["Location"]
        keys_set = self._set_keys_from_location(location)
        all_keys_set = keys_set >= len(self._keys) - len(self.path_keys) or len(
            self.parent_keys
        ) >= len(self._keys)
        if all_keys_set:
            return

        if utils.DEBUG:
            LOGGER.debug(
                "!!!FILE A DEFECT!!! Location returned for %s does not have all expected"
                " key values. Location was: %s",
                post_response.request.url,
                location,
            )
        # fail without polling based on the value of the global config
        if not config.RETRY_ON_INCOMPLETE_LOCATION:
            msg = f"Not able to find the full location of the posted resource. Location returned for {post_response.request.url} does not have all expected key values. Location was: {location}"
            raise NetAppRestError(message=msg)
        # if we didn't get enough keys back, let's continue to make requests for
        # a bit to the Location provided to see if ONTAP will eventually fill in
        # the rest.
        if json.loads(post_response.text).get("job", None):
            if utils.DEBUG:
                LOGGER.debug(
                    "Response contains a job body, waiting for the job to complete"
                    " before determining the keys for the newly created object."
                )
            job_response = json.loads(
                utils.poll(
                    post_response,
                    self.get_connection(),
                    timeout=timeout,
                    interval=interval,
                ).http_response.text,
            )
            if job_response["state"] != "success":
                msg = (
                    "The job to create the new resource failed for the following"
                    f" reason: {job_response.get('message', '<unknown>')}"
                )
                raise NetAppRestError(message=msg)

        url = f"{self.get_connection().origin}{location}"
        num_tries = 10
        tries = 0
        while tries < num_tries:
            response = self.get_connection().session.get(url)
            if response.json().get("records"):
                location = response.json()["records"][0]["_links"]["self"]["href"]
                break
            time.sleep(1)
            tries += 1
        if tries >= num_tries:
            msg = (
                "Not able to find the location of the posted resource after"
                f" {num_tries} seconds."
            )
            raise NetAppRestError(message=msg)

        self._set_keys_from_location(location)

    def _set_keys_from_location(self, location: str) -> int:
        """Parse a returned Location header and from it, find key values that
        should be set on this instance.

        Args:
            location: The Location header from a POST call

        Returns:
            The number of key values that were parsed and set on the instance
        """

        # pick apart the URL and fill in our keys
        base_location = location.split("?", 1)[0]
        base_location = base_location.replace(self._location, "").replace("/", "", 1)
        if not base_location:
            if "?" in location:
                self._required_queries = location.split("?")[1]
            return 0
        keys_set = 0
        for key_index in range(len(self._keys) - len(self.path_keys)):
            key_attr = self._keys[-key_index - 1]
            try:
                key_value = base_location.split("/")[-key_index - 1]
            except IndexError:
                continue
            if not key_value:
                continue
            self._attrsetter(key_attr, urllib.parse.unquote(key_value))
            keys_set += 1

        # if we've found all of the necessary keys and there is a query, then
        # set that as a required query (a sort of key that's not part of the path)
        if keys_set >= len(self._keys) - len(self.path_keys) and "?" in location:
            self._required_queries = location.split("?")[1]
        return keys_set

    def _attrsetter(self, attribute: str, value) -> None:
        """Set a complex property on the object

        Allows for setting something like this:

            self.owner.uuid = '12345'

        when the owner.uuid part is a string. Similar to the builtin setattr()
        function of Python.

        Args:
            attribute: The complex attribute to set on the object. This can be
                in a dotted notation. All parts of the attribute up to the final
                part must already exist in the object.
            value: The value to be set

        Raises:
            `AttributeError`: If the object tree cannot be navigated all the way
                to the final attribute.
        """

        obj = self
        attrs = attribute.split(".")
        for name in attrs[:-1]:
            if not hasattr(obj, name):
                setattr(obj, name, _EmptyObject())
            obj = getattr(obj, name)
        setattr(obj, attrs[-1], value)

    def _set_last_state(self) -> None:
        """Set the last known host state on the object as its dictionary representation.

        This is performed recursively for all of its sub-objects too. The last
        known state is used as part of future PATCH calls to determine the delta
        to send to the host.
        """

        for field in self._schema_instance.fields:
            value = getattr(self, field, None)
            if isinstance(value, Resource):
                value._set_last_state()  # pylint: disable=protected-access

        self._last_state = self.to_dict()

    def _get_changed_data(
        self,
        starting_value: Optional[dict] = None,
        ref_fields: Optional[List[str]] = None,
    ) -> dict:
        """Return a diff of the current state of the object vs. the last known state.

        Args:
            starting_value: Instead of comparing the object's last retrieved state
                vs. its current state, this value can be provided to compare
                against its current state. Useful for sub-objects.
            ref_fields: if provided, these fields will be considered patchable
                even if they are not normally. This would be used when posting
                an object that contains a ref to part of another object

        Returns:
            A diff in the form of a dictionary. This is meant to be sent to the
            PATCH API of the resource.
        """

        last_state = getattr(self, "_last_state", {})
        if starting_value is not None:
            last_state = starting_value
        changed_data = {}
        self._clone_from_dict(self.to_dict())
        schema = self._schema_instance
        for field in schema.fields:
            if self._should_skip_field(schema, field, "patch", ref_fields=ref_fields):
                continue
            # If the attribute doesn't exist, set it to missing
            # This is done to make a distinction between missing values and None values
            current_value = getattr(self, field, missing)
            if schema.fields[field].data_key is not None:
                previous_value = last_state.get(schema.fields[field].data_key, None)
            else:
                previous_value = last_state.get(field, None)
            # In these checks, we only recurse through the property if it's not missing or None
            # But we include it if it's explicitly set to None and it's different to its previous value
            if current_value is not None and current_value != missing:
                current_value = _get_current_value(
                    schema,
                    field,
                    current_value,
                    previous_value,
                )
                if current_value is not None and current_value != previous_value:
                    if isinstance(current_value, datetime.datetime):
                        current_value = schema.fields[field].serialize(field, self)
                    field_name = getattr(schema.fields[field], "data_key", field)
                    changed_data[field_name or field] = current_value
            elif current_value is None and current_value != previous_value:
                field_name = getattr(schema.fields[field], "data_key", field)
                changed_data[field_name or field] = current_value

        # round trip through marshmallow's encoder/decoder so that we get the
        # benefit of any field name mapping
        return self.from_dict(changed_data).to_dict()

    def _get_postable_data(
        self,
        ref_fields: Optional[List[str]] = None,
    ) -> dict:
        """Return a dict of only the postable fields for this resource.

        Args:
            ref_fields: if provided, these fields will be considered postable
                even if they are not normally. This would be used when posting
                an object that contains a ref to part of another object

        Returns:
            A fields in the form of a dictionary. This is meant to be sent to the
            POST API of the resource.
        """

        changed_data = {}
        self._clone_from_dict(self.to_dict())
        schema = self._schema_instance
        for field in schema.fields:
            if self._should_skip_field(schema, field, "post", ref_fields=ref_fields):
                continue

            current_value = getattr(self, field, None)

            if current_value is not None and current_value != missing:
                current_value = _get_postable_value(schema, field, current_value)
                if current_value is not None:
                    if isinstance(current_value, datetime.datetime):
                        current_value = schema.fields[field].serialize(field, self)
                    field_name = getattr(schema.fields[field], "data_key", field)
                    changed_data[field_name or field] = current_value

        # round trip through marshmallow's encoder/decoder so that we get the
        # benefit of any field name mapping
        return self.from_dict(changed_data).to_dict()

    def _should_skip_field(
        self,
        schema: ResourceSchema,
        field: str,
        action: str,
        ref_fields: Optional[List[str]] = None,
    ) -> bool:
        """Determine if we should skip sending this field in a POST or PATCH
        request and warn the user that we are doing so
        """

        if not config.STRICT_ACCESS_MODIFIERS:
            return False

        current_value = schema.fields[field].serialize(field, self)
        if current_value is None or current_value == missing:
            return False

        action_fields = getattr(schema, f"{action}able_fields")
        warning = "%s.%s is not a %sable field so it is not being sent."

        # if the field is not in the action list, then warn
        if not ref_fields:
            if not [f for f in action_fields if f.split(".")[0] == field]:
                LOGGER.debug(warning, self.__class__.__name__, field, action)
                return True
        elif not field in ref_fields:
            LOGGER.debug(warning, self.__class__.__name__, field, action)
            return True
        return False

    def _populate_file_objects(self, user_params: dict, method: str = "") -> dict:
        """Parse through all valid formdata parameters passed by user to generate
        a file object dictionary that contains either literal or file data types or both.

        Args:
            user_params: dictionary of possible valid formData parameters and their values
            method: a string that is used to determine which REST action is taking place.
                This is used to differentiate between the post and patch formdata parameters.

        Returns:
            a dictionary with all valid file objects, both literal and file.
        """
        _form_data = {}  # type: dict
        _form_data_values = getattr(self, f"_{method}_form_data_parameters").values()
        _form_data = getattr(self, f"_{method}_form_data_parameters")

        # dictionary that holds all multipart/form-data that will be sent in the request
        file_objects = {}  # type: Any
        # Whenever the user is sending a single file that may or may not be > 1GB
        send_single_large_file = True

        # populate the file_objects dictionary with parameters of type integer/boolean/string
        literal_types = {"string", "integer", "boolean"}
        if literal_types.intersection(set(_form_data_values)):
            send_single_large_file = False
            literal_list = [
                k for k in user_params if _form_data.get(k) in literal_types
            ]
            for param in literal_list:
                data_object = user_params.get(param)
                if data_object is not None:
                    file_objects[param] = (param, data_object)

        # if there exists a formdata parameter that is of type file
        if "file" in _form_data_values:
            # create string array with all parameters of type file
            file_list = [k for k in user_params if _form_data.get(k) == "file"]
            # if there is only 1 file being sent as multipart/form-data
            # to account for the possibility that this file may be > 1GB we must handle this use case differently
            # support for uploading multiple large files will be added in the future.
            if (
                send_single_large_file
                and len(file_list) == 1
                and list(user_params.values())[0].startswith("@")
            ):
                file_objects[file_list[0]] = (
                    list(user_params.values())[0][1:],
                    LazyFile(list(user_params.values())[0][1:], "rb"),
                    "application/octet-stream",
                )
                return file_objects
            # populate the file_objects dictionary with all parameters of type file
            for param in file_list:
                data_file = user_params.get(param)
                if data_file is not None:
                    if data_file.startswith("@"):
                        data_file = data_file[1:]
                        file_objects[param] = (
                            data_file,
                            LazyFile(data_file, "rb"),
                            "application/octet-stream",
                        )
                    else:
                        file_objects[param] = (param, data_file)

        return file_objects

    def _check_for_post_collection_treatment(self) -> None:
        """This is a check for some properties that change the behavior of a post
        to create multiple records, which resembles post_collection.
        If any of these properties are set on the current resource, an error is thrown.
        """
        # pylint: disable=protected-access
        for prop_name in config._TREAT_AS_POST_COLLECTION.get(self.__module__, []):
            sub_probs = prop_name.split(".")
            current_prop: Optional[Resource] = self
            for sub_prop in sub_probs:
                current_prop = getattr(current_prop, sub_prop, None)
                if current_prop is None:
                    break
            if current_prop:
                raise NetAppRestError(
                    message=f"post() cannot be used when '{prop_name}' is set since this "
                    "property is used to create multiple records. "
                    f"Use post_collection() instead."
                )


def _get_postable_value(schema: ResourceSchema, field: str, current_value: Any) -> Any:
    """Return the current value of the field. If the value is a Resource, recursively
    looks at its fields to determine the changed data. If it is a list, looks at
    each element to determine the changed data.
    """

    if not isinstance(current_value, (Resource, list)):
        return current_value

    if isinstance(current_value, Resource):
        ref_fields = [
            f.split(".")[1] for f in schema.postable_fields if f.startswith(field + ".")
        ]
        current_value = (
            current_value._get_postable_data(  # pylint: disable=protected-access
                ref_fields=ref_fields,
            )
        )
    elif isinstance(current_value, list):
        changed_items = []
        for value in current_value:
            if isinstance(value, Resource):
                ref_fields = [
                    f.split(".")[1]
                    for f in schema.postable_fields
                    if f.startswith(field + ".")
                ]
                changed = value._get_postable_data(  # pylint: disable=protected-access
                    ref_fields=ref_fields,
                )
                if changed:
                    changed_items.append(changed)
            else:
                changed_items.append(value)
        current_value = changed_items

    if not current_value:
        current_value = None

    return current_value


def _get_current_value(
    schema: ResourceSchema, field: str, current_value: Any, previous_value: Any
) -> Any:
    """Return the current value of the field. If the value is a Resource, recursively
    looks at its fields to determine the changed data.
    """

    if not isinstance(current_value, (list, Resource)):
        return current_value

    if isinstance(current_value, Resource):
        if not current_value.to_dict():
            return {}
        ref_fields = [
            f.split(".")[1]
            for f in schema.patchable_fields
            if f.startswith(field + ".")
        ]
        if previous_value is None:
            previous_value = {}
        current_value = (
            current_value._get_changed_data(  # pylint: disable=protected-access
                starting_value=previous_value,
                ref_fields=ref_fields,
            )
        )
        if not current_value:
            current_value = None
    else:
        new_list = []
        for thing in current_value:
            if isinstance(thing, Resource):
                new_list.append(thing.to_dict())
            else:
                new_list.append(thing)
        current_value = new_list

    return current_value


def _flatten_dict(initial: dict, parent_key: str = "") -> dict:
    """Flatten a nested dictionary structure so that nested elements are turned
    into compound keys.

    For example:

    {'foo': {'bar': 'baz'}, 'fizz': 'buzz'} => {'foo.bar': 'baz', 'fizz': 'buzz'}

    Args:
        initial: The dictionary to be flattened
        parent_key: Used for recursive calls

    Returns:
        A flattened dictionary where each key maps to a value non-dict value.
    """

    result = {}
    for key, value in initial.items():
        key = parent_key + key
        if isinstance(value, dict):
            result.update(_flatten_dict(value, key + "."))
        else:
            result[key] = value
    return result


def _cluster_software_fix(input_dict: dict) -> dict:
    """This returns the correct schema for the /cluster/software endpoint
    to fix the backwards compatibility issue due to the model changing after 9.6
    Once we no longer support ONTAP 9.6, this hardcoded fix can be removed.
    """

    for obj in ["validation_results", "status_details"]:
        if not obj in input_dict:
            continue
        items = input_dict[obj]
        for item in items:
            if isinstance(item.get("message", None), str):
                item["issue"] = {"message": item["message"]}
            if isinstance(item.get("action", None), str):
                item["action"] = {"message": item["action"]}
    return input_dict


def _get_patch_collection_record_data(records: Iterable["Resource"]) -> bytes:
    """Return the filtered list of records for a patch_collection function in
    bytes format."""

    def filter_keys(body: dict, path_keys: list):
        for key in path_keys:
            body.pop(key.split(".")[0], None)
        return body

    record_data = json.dumps(
        {
            "records": [
                # pylint: disable=protected-access
                {
                    **r._get_changed_data(),
                    **filter_keys(r.to_dict(only=tuple(r._keys)), r.path_keys),
                }
                for r in records
            ]
        },
        cls=ResourceJSONEncoder,
        ensure_ascii=False,
    ).encode("utf-8")
    return record_data


def _get_patch_collection_responses(
    url: str, params: dict, sample: Resource, body: dict
) -> List[requests.models.Response]:
    """Get the final response when doing patch_collection without records."""
    responses = []
    while url:
        response = sample.get_connection().session.patch(
            url,
            data=json.dumps(body, cls=ResourceJSONEncoder, ensure_ascii=False).encode(
                "utf-8"
            ),
            params=params,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        responses.append(response)
        next_link = response.json().get("_links", {}).get("next", {}).get("href", None)
        if next_link:
            url = f"{sample.get_connection().origin}{next_link}"
            # the next link will give us all our params back, so don't
            # add them to the URL a second time
            params = {}
        else:
            url = ""
    return responses


class _EmptyObject:  # pylint: disable=too-few-public-methods
    """This class is to be used to add dynamic, nested attributes to resources."""
