r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

##  Overview
Cluster peering allows administrators of ONTAP systems to establish relationships between two or more independent clusters. When a relationship exists between two clusters, the clusters can exchange user data and configuration information, and coordinate operations. The /cluster/peers endpoint supports create, get, modify, and delete operations using GET, PATCH, POST and DELETE HTTP requests.
## Create a cluster peer
You can set up a new cluster peer relationship by issuing a POST request to /cluster/peers. Parameters in the POST body define the settings of the peering relationship. A successful POST request that succeeds in creating a peer returns HTTP status code "201", along with the details of the created peer, such as peer UUID, name, and authentication information. A failed POST request returns an HTTP error code along with a message indicating the reason for the error. This can include malformed requests and invalid operations.
## Examples of creating cluster peers
### Creating a cluster peer request with an empty request to accept the defaults
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {
            "passphrase": "pLznaom1ctesJFq4kt5Qfghf",
            "expiry_time": "2021-05-25T20:04:15-04:00",
        },
        "uuid": "86de6c46-bdad-11eb-83cd-005056bb267e",
        "ip_address": "0.0.0.0",
        "_links": {
            "self": {"href": "/api/cluster/peers/86de6c46-bdad-11eb-83cd-005056bb267e"}
        },
        "name": "Clus_fghf",
    }
)

```
</div>
</div>

### Creating a cluster peer request with a system-generated passphrase that will expire on 05/26/2021 at 12:34:56
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.authentication = {
        "expiry_time": "05/26/2021 12:34:56",
        "generate_passphrase": True,
    }
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {
            "passphrase": "dZNOKkpVfntNZHf3MjpNF6ht",
            "expiry_time": "2021-05-26T12:34:56-04:00",
        },
        "uuid": "14c817c7-bdad-11eb-83cd-005056bb267e",
        "ip_address": "0.0.0.0",
        "_links": {
            "self": {"href": "/api/cluster/peers/14c817c7-bdad-11eb-83cd-005056bb267e"}
        },
        "name": "Clus_F6ht",
    }
)

```
</div>
</div>

### Creating a cluster peer request with a peer address and the generated passphrase is returned in the response
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.remote = {"ip_addresses": ["1.2.3.4"]}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {
            "passphrase": "yDhdOteVGEOhkeXF+DJYwDro",
            "expiry_time": "2021-05-25T20:28:12-04:00",
        },
        "uuid": "b404cc52-bdae-11eb-812c-005056bb0af1",
        "_links": {
            "self": {"href": "/api/cluster/peers/b404cc52-bdae-11eb-812c-005056bb0af1"}
        },
        "name": "",
    }
)

```
</div>
</div>

### Creating a cluster peer request with a peer name and the generated passphrase is returned in the response
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.name = "cp_xyz123"
    resource.authentication = {"generate_passphrase": True}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {
            "passphrase": "eeGTerZlh2qSAt2akpYEcM1c",
            "expiry_time": "2021-05-25T20:29:38-04:00",
        },
        "uuid": "125f8dc6-bdb1-11eb-83cd-005056bb267e",
        "ip_address": "1.2.3.5",
        "_links": {
            "self": {"href": "/api/cluster/peers/125f8dc6-bdb1-11eb-83cd-005056bb267e"}
        },
        "name": "cp_xyz123",
    }
)

```
</div>
</div>

### Creating a cluster peer request with a name, a peer address, and a passphrase
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.name = "cp_xyz123"
    resource.remote = {"ip_addresses": ["1.2.3.4"]}
    resource.authentication = {"passphrase": "xyz12345"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {"expiry_time": "2021-05-25T20:32:49-04:00"},
        "uuid": "b404cc52-bdae-11eb-812c-005056bb0af1",
        "_links": {
            "self": {"href": "/api/cluster/peers/b404cc52-bdae-11eb-812c-005056bb0af1"}
        },
    }
)

```
</div>
</div>

### Creating a cluster peer request with a proposed encryption protocol
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.encryption = {"proposed": "tls-psk"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {
            "passphrase": "Gy8SqsXVhcUkS1AfepH7Pslc",
            "expiry_time": "2021-05-25T20:34:07-04:00",
        },
        "uuid": "b33a23a6-bdb1-11eb-83cd-005056bb267e",
        "ip_address": "1.2.3.5",
        "_links": {
            "self": {"href": "/api/cluster/peers/b33a23a6-bdb1-11eb-83cd-005056bb267e"}
        },
        "name": "Clus_Pslc",
    }
)

```
</div>
</div>

---
## Creating local intercluster LIFs
The local cluster must have an intercluster LIF on each node for the correct operation of cluster peering. If no local intercluster LIFs exist, you can optionally specify LIFs to be created for each node in the local cluster. These local interfaces, if specified, are created on each node before proceeding with the creation of the cluster peering relationship. Cluster peering relationships are not established if there is an error preventing the LIFs from being created.
After local interfaces have been created, do not specify them for subsequent cluster peering relationships.
### Local LIF creation fields

* local_network.ip_addresses - List of IP addresses to assign, one per node in the local cluster.
* local_network.netmask - IPv4 mask or subnet mask length.
* local_network.broadcast_domain - Broadcast domain that is in use within the IPspace.
* local_network.gateway - The IPv4 or IPv6 address of the default router.
### Additional information on network routes
When creating LIFs, the network route discovery mechanism might take additional time (1-5 seconds) to become visible in the network outside of the cluster. This delay in publishing the routes might cause an initial cluster peer "create" request to fail. This error disappears with a retry of the same request.
### This example shows the POST body when creating four intercluster LIFs on a 4-node cluster before creating a cluster peer relationship.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer()
    resource.local_network = {
        "interfaces": [
            {"ip_address": "1.2.3.4"},
            {"ip_address": "1.2.3.5"},
            {"ip_address": "1.2.3.6"},
        ],
        "netmask": "255.255.0.0",
        "broadcast_domain": "Default",
        "gateway": "1.2.0.1",
    }
    resource.remote = {"ip_addresses": ["1.2.9.9"]}
    resource.authentication = {"passphrase": "xyz12345"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {"expiry_time": "2021-05-25T21:28:26-04:00"},
        "uuid": "b404cc52-bdae-11eb-812c-005056bb0af1",
        "local_network": {
            "interfaces": [
                {"ip_address": "1.2.3.4"},
                {"ip_address": "1.2.3.5"},
                {"ip_address": "1.2.3.6"},
            ]
        },
        "_links": {
            "self": {"href": "/api/cluster/peers/b404cc52-bdae-11eb-812c-005056bb0af1"}
        },
    }
)

```
</div>
</div>

---
## Examples of retrieving existing cluster peers
You can retrieve peers in a cluster by issuing a GET request to /cluster/peers. It is also possible to retrieve a specific peer when qualified by its UUID to /cluster/peers/{uuid}.
A GET request might have no query parameters or a valid cluster UUID. The former retrieves all records while the latter retrieves the record for the cluster peer with that UUID.
### Retrieving all cluster peer relationships, both established and pending
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ClusterPeer.get_collection()))

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
[
    ClusterPeer(
        {
            "uuid": "a6001076-bdb2-11eb-83cd-005056bb267e",
            "_links": {
                "interfaces": {
                    "href": "/api/network/ip/interfaces?services=intercluster_core&ipspace.uuid=0bac5ced-a911-11eb-83cd-005056bb267e"
                },
                "self": {
                    "href": "/api/cluster/peers/a6001076-bdb2-11eb-83cd-005056bb267e"
                },
            },
            "name": "Clus_bH6l",
        }
    ),
    ClusterPeer(
        {
            "uuid": "b404cc52-bdae-11eb-812c-005056bb0af1",
            "_links": {
                "interfaces": {
                    "href": "/api/network/ip/interfaces?services=intercluster_core&ipspace.uuid=0bac5ced-a911-11eb-83cd-005056bb267e"
                },
                "self": {
                    "href": "/api/cluster/peers/b404cc52-bdae-11eb-812c-005056bb0af1"
                },
            },
            "name": "remote-cluster",
        }
    ),
]

```
</div>
</div>

### Retrieving all cluster peer relationships which are not in an available state
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ClusterPeer.get_collection(**{"status.state": "!available"})))

```
<div class="try_it_out">
<input id="example8_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example8_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example8_result" class="try_it_out_content">
```
[
    ClusterPeer(
        {
            "status": {"state": "unidentified"},
            "uuid": "a6001076-bdb2-11eb-83cd-005056bb267e",
            "_links": {
                "interfaces": {
                    "href": "/api/network/ip/interfaces?services=intercluster_core&ipspace.uuid=0bac5ced-a911-11eb-83cd-005056bb267e"
                },
                "self": {
                    "href": "/api/cluster/peers/a6001076-bdb2-11eb-83cd-005056bb267e"
                },
            },
            "name": "Clus_bH6l",
        }
    )
]

```
</div>
</div>

### Retrieving information about a single cluster peer relationship
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example9_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example9_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example9_result" class="try_it_out_content">
```
ClusterPeer(
    {
        "authentication": {"state": "ok", "in_use": "ok"},
        "encryption": {"state": "tls_psk"},
        "version": {
            "generation": 9,
            "major": 10,
            "full": "NetApp Release 9.10.1: Tue May 25 08:08:44 UTC 2021",
            "minor": 1,
        },
        "status": {"update_time": "2021-05-25T19:38:55-04:00", "state": "available"},
        "remote": {
            "ip_addresses": ["1.2.3.4"],
            "serial_number": "1-80-000011",
            "name": "remote-cluster",
        },
        "uuid": "b404cc52-bdae-11eb-812c-005056bb0af1",
        "ipspace": {
            "uuid": "0bac5ced-a911-11eb-83cd-005056bb267e",
            "_links": {
                "self": {
                    "href": "/api/network/ipspaces/0bac5ced-a911-11eb-83cd-005056bb267e"
                }
            },
            "name": "Default",
        },
        "_links": {
            "interfaces": {
                "href": "/api/network/ip/interfaces?services=intercluster_core&ipspace.uuid=0bac5ced-a911-11eb-83cd-005056bb267e"
            },
            "self": {"href": "/api/cluster/peers/b404cc52-bdae-11eb-812c-005056bb0af1"},
        },
        "name": "remote-cluster",
    }
)

```
</div>
</div>

---
## Examples of updating an existing cluster peer
You can update a cluster peer relationship by issuing a PATCH request to /cluster/peers/{uuid}. As in the CLI mode, you can toggle the proposed encryption protocol, update the passphrase, or specify a new set of stable addresses. All PATCH requests take the parameters that are to be updated in the request body. If generate_passphrase is "true", the passphrase is returned in the PATCH response.
### Updating the proposed encryption protocol from tls-psk to none
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.authentication = {"passphrase": "xyz12345", "in_use": "ok"}
    resource.encryption = {"proposed": "none"}
    resource.patch()

```

### Updating the passphrase
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.authentication = {"passphrase": "xyz12345", "in_use": "ok"}
    resource.patch()

```

### Setting an auto-generated passphrase
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.authentication = {"generate_passphrase": True, "in_use": "ok"}
    resource.patch()

```

### Updating remote IP addresses
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.remote = {"ip_addresses": ["1.2.3.6"]}
    resource.patch()

```

---
## An example of deleting an existing cluster peer
You can delete a cluster peer using the HTTP DELETE request.
### Deleting a peer with peer UUID "8becc0d4-c12c-11e8-9ceb-005056bbd143"
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterPeer(uuid="b404cc52-bdae-11eb-812c-005056bb0af1")
    resource.delete()

```
"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

from marshmallow import fields as marshmallow_fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ResourceSchemaMeta, ImpreciseDateTime, Size
from netapp_ontap.raw_resource import RawResource

from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["ClusterPeer", "ClusterPeerSchema"]
__pdoc__ = {
    "ClusterPeerSchema.resource": False,
    "ClusterPeerSchema.opts": False,
}


class ClusterPeerSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the ClusterPeer object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_links.ClusterPeerLinksSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the cluster_peer."""

    authentication = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_authentication.ClusterPeerAuthenticationSchema", data_key="authentication", unknown=EXCLUDE, allow_none=True)
    r""" The authentication field of the cluster_peer."""

    encryption = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_encryption.ClusterPeerEncryptionSchema", data_key="encryption", unknown=EXCLUDE, allow_none=True)
    r""" The encryption field of the cluster_peer."""

    initial_allowed_svms = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, allow_none=True), data_key="initial_allowed_svms", allow_none=True)
    r""" The local SVMs allowed to peer with the peer cluster's SVMs. This list can be modified until the remote cluster accepts this cluster peering relationship."""

    ip_address = marshmallow_fields.Str(
        data_key="ip_address",
        allow_none=True,
    )
    r""" A local intercluster IP address that a remote cluster can use, together with the passphrase, to create a cluster peer relationship with the local cluster."""

    ipspace = marshmallow_fields.Nested("netapp_ontap.resources.ipspace.IpspaceSchema", data_key="ipspace", unknown=EXCLUDE, allow_none=True)
    r""" The ipspace field of the cluster_peer."""

    local_network = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_local_network.ClusterPeerLocalNetworkSchema", data_key="local_network", unknown=EXCLUDE, allow_none=True)
    r""" Cluster peering requires an intercluster LIF on each local node. These can be optionally created by specifying a list of IP addresses corresponding to each node."""

    name = marshmallow_fields.Str(
        data_key="name",
        allow_none=True,
    )
    r""" Optional name for the cluster peer relationship. By default, it is the name of the remote cluster, or a temporary name might be autogenerated for anonymous cluster peer offers.

Example: cluster2"""

    peer_applications = marshmallow_fields.List(marshmallow_fields.Str, data_key="peer_applications", allow_none=True)
    r""" Peering applications against which allowed SVMs are configured.

Example: ["snapmirror","flexcache"]"""

    remote = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_remote.ClusterPeerRemoteSchema", data_key="remote", unknown=EXCLUDE, allow_none=True)
    r""" The remote field of the cluster_peer."""

    status = marshmallow_fields.Nested("netapp_ontap.models.cluster_peer_status.ClusterPeerStatusSchema", data_key="status", unknown=EXCLUDE, allow_none=True)
    r""" The status field of the cluster_peer."""

    uuid = marshmallow_fields.Str(
        data_key="uuid",
        allow_none=True,
    )
    r""" UUID of the cluster peer relationship. For anonymous cluster peer offers, the UUID will change when the remote cluster accepts the relationship.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412"""

    version = marshmallow_fields.Nested("netapp_ontap.models.version.VersionSchema", data_key="version", unknown=EXCLUDE, allow_none=True)
    r""" This returns the cluster version information.  When the cluster has more than one node, the cluster version is equivalent to the lowest of generation, major, and minor versions on all nodes."""

    @property
    def resource(self):
        return ClusterPeer

    gettable_fields = [
        "links",
        "authentication",
        "encryption",
        "initial_allowed_svms.links",
        "initial_allowed_svms.name",
        "initial_allowed_svms.uuid",
        "ip_address",
        "ipspace.links",
        "ipspace.name",
        "ipspace.uuid",
        "name",
        "peer_applications",
        "remote",
        "status",
        "uuid",
        "version",
    ]
    """links,authentication,encryption,initial_allowed_svms.links,initial_allowed_svms.name,initial_allowed_svms.uuid,ip_address,ipspace.links,ipspace.name,ipspace.uuid,name,peer_applications,remote,status,uuid,version,"""

    patchable_fields = [
        "authentication",
        "encryption",
        "initial_allowed_svms.name",
        "initial_allowed_svms.uuid",
        "ipspace.name",
        "ipspace.uuid",
        "name",
        "peer_applications",
        "remote",
    ]
    """authentication,encryption,initial_allowed_svms.name,initial_allowed_svms.uuid,ipspace.name,ipspace.uuid,name,peer_applications,remote,"""

    postable_fields = [
        "authentication",
        "encryption",
        "initial_allowed_svms.name",
        "initial_allowed_svms.uuid",
        "ipspace.name",
        "ipspace.uuid",
        "local_network",
        "name",
        "peer_applications",
        "remote",
    ]
    """authentication,encryption,initial_allowed_svms.name,initial_allowed_svms.uuid,ipspace.name,ipspace.uuid,local_network,name,peer_applications,remote,"""

class ClusterPeer(Resource):
    """Allows interaction with ClusterPeer objects on the host"""

    _schema = ClusterPeerSchema
    _path = "/api/cluster/peers"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of cluster peers.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ClusterPeer resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def fast_get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["RawResource"]:
        """Returns a list of RawResources that represent ClusterPeer resources that match the provided query"""
        return super()._get_collection(
            *args, connection=connection, max_records=max_records, raw=True, **kwargs
        )

    fast_get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["ClusterPeer"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a cluster peer instance.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["ClusterPeer"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ClusterPeer"], NetAppResponse]:
        r"""Creates a peering relationship and, optionally, the IP interfaces it will use. There are two methods used to create a peering relationship:
* Provide a remote IP address - Used when creating a new cluster peer relationship with a specific remote cluster. This requires at least one remote intercluster IP address from the remote cluster.
* Do not provide a remote IP address - Used when the remote IP address is not provided and when the storage system is ready to accept peering requests from foreign clusters.
### Required properties
* `remote.ip_addresses` - Addresses of the remote peers. The local peer must be able to reach and connect to these addresses for the request to succeed in creating a peer. Only required when creating a peering relationship by providing a remote IP address.
* Either set `generate_passphrase` to "true" or provide a passphrase in the body of the request. Only one of these options is required.
### Recommended optional properties
* `name` - Name of the peering relationship or name of the remote peer.
* `passphrase` - User generated passphrase for use in authentication.
* `generate_passphrase` (true/false) - When "true", ONTAP automatically generates a passphrase to authenticate cluster peers.
* `ipspace` - IPspace of the local intercluster LIFs. Assumes Default IPspace if not provided.
* `initial_allowed_svms` - Local SVMs allowed to peer with the peer cluster's SVMs. Can be modified until the remote cluster accepts this cluster peering relationship.
* `local_network` - Fields to create a local intercluster LIF.
* `expiry_time` - Duration in ISO 8601 format for which the user-supplied or auto-generated passphrase is valid. Expiration time must not be greater than seven days into the future. ISO 8601 duration format is "PnDTnHnMnS" or "PnW" where n is a positive integer. The "nD", "nH", "nM" and "nS" fields can be dropped if zero. "P" must always be present and "T" must be present if there are any hours, minutes, or seconds fields.
* `encryption_proposed` (none/tls-psk) - Encryption mechanism of the communication channel between the two peers.
* `peer_applications` - SVM peering applications (SnapMirror, FlexCache or both) for which the SVM peering relationship is set up.
### Additional information
As with creating a cluster peer through the CLI, the combinations of options must be valid in order for the create operation to succeed. The following list shows the combinations that will succeed and those that will fail:
* A passphrase only (fail)
* A peer IP address (fail)
* A passphrase with an expiration time > 7 days into the future (fail)
* A peer IP address and a passphrase (OK)
* generate_passphrase=true (OK)
* Any proposed encryption protocol (OK)
* An IPspace name or UUID (OK)
* A passphrase, peer IP address, and any proposed encryption protocol (OK)
* A non empty list of initial allowed SVM peer names or UUIDs. (OK)

### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["ClusterPeer"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a cluster peer.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of cluster peers.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific cluster peer instance.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a peering relationship and, optionally, the IP interfaces it will use. There are two methods used to create a peering relationship:
* Provide a remote IP address - Used when creating a new cluster peer relationship with a specific remote cluster. This requires at least one remote intercluster IP address from the remote cluster.
* Do not provide a remote IP address - Used when the remote IP address is not provided and when the storage system is ready to accept peering requests from foreign clusters.
### Required properties
* `remote.ip_addresses` - Addresses of the remote peers. The local peer must be able to reach and connect to these addresses for the request to succeed in creating a peer. Only required when creating a peering relationship by providing a remote IP address.
* Either set `generate_passphrase` to "true" or provide a passphrase in the body of the request. Only one of these options is required.
### Recommended optional properties
* `name` - Name of the peering relationship or name of the remote peer.
* `passphrase` - User generated passphrase for use in authentication.
* `generate_passphrase` (true/false) - When "true", ONTAP automatically generates a passphrase to authenticate cluster peers.
* `ipspace` - IPspace of the local intercluster LIFs. Assumes Default IPspace if not provided.
* `initial_allowed_svms` - Local SVMs allowed to peer with the peer cluster's SVMs. Can be modified until the remote cluster accepts this cluster peering relationship.
* `local_network` - Fields to create a local intercluster LIF.
* `expiry_time` - Duration in ISO 8601 format for which the user-supplied or auto-generated passphrase is valid. Expiration time must not be greater than seven days into the future. ISO 8601 duration format is "PnDTnHnMnS" or "PnW" where n is a positive integer. The "nD", "nH", "nM" and "nS" fields can be dropped if zero. "P" must always be present and "T" must be present if there are any hours, minutes, or seconds fields.
* `encryption_proposed` (none/tls-psk) - Encryption mechanism of the communication channel between the two peers.
* `peer_applications` - SVM peering applications (SnapMirror, FlexCache or both) for which the SVM peering relationship is set up.
### Additional information
As with creating a cluster peer through the CLI, the combinations of options must be valid in order for the create operation to succeed. The following list shows the combinations that will succeed and those that will fail:
* A passphrase only (fail)
* A peer IP address (fail)
* A passphrase with an expiration time > 7 days into the future (fail)
* A peer IP address and a passphrase (OK)
* generate_passphrase=true (OK)
* Any proposed encryption protocol (OK)
* An IPspace name or UUID (OK)
* A passphrase, peer IP address, and any proposed encryption protocol (OK)
* A non empty list of initial allowed SVM peer names or UUIDs. (OK)

### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a cluster peer instance.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a cluster peer.
### Learn more
* [`DOC /cluster/peers`](#docs-cluster-cluster_peers)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)


