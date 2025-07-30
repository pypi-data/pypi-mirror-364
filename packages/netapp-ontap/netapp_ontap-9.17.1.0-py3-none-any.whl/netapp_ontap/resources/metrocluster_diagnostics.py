r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
You can use this API to initiate a MetroCluster diagnostics operation and fetch the results of a completed diagnostics operation on a MetroCluster over IP configuration. The GET operation retrieves the results of a completed diagnostics operation for the MetroCluster over IP configuration. These can include the overall high level and details for the checks done for different components. By default, the response does not include the details. If the fields query is used in the request, the response will include the details. The POST request can be used to start a MetroCluster diagnostics operation or set up a schedule for the diagnostics to be run periodically.
## Details
Details provide a way to view all the checks done on a component and the result of each check. The details of the checks are not included
in the response by default. In order to fetch the details, use the `fields` query parameter.

* `node.details`
* `aggregate.details`
* `cluster.details`
* `volume.details`
* `connection.details`
## Starting a MetroCluster diagnostics operation
A new MetroCluster diagnostics operation can be started by issuing a POST to /cluster/metrocluster/diagnostics. There are no extra parameters required to initiate a diagnostics operation.
### Polling the POST job for status of diagnostics operation
After a successful POST /cluster/diagnostics operation is issued, an HTTP status code of 202 (Accepted) is returned along with a job UUID and a link in the body of the response. The POST job continues asynchronously and can be monitored by using the job UUID and the /cluster/jobs API. The "message" field in the response of the GET /cluster/jobs/{uuid} request shows the current step in the job, and the "state" field shows the overall state of the job.
<br/>
---
## Examples
### Running the diagnostics operation
This example shows the POST request for starting a diagnostic operation for a MetroCluster over IP configuration and the responses returned:
```
#API
/api/cluster/metrocluster/diagnostics
```
### POST Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.post(hydrate=True)
    print(resource)

```

### POST Response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:20:53 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Location: /api/cluster/metrocluster/diagnostics
Content-Length: 189
Content-Type: application/hal+json
{
  "job": {
    "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
      }
    }
  }
}
```
### Monitoring the job progress
Use the link provided in the response to the POST request to fetch information for the diagnostics operation job.
<br/>
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="f7d3804c-fcf7-11ea-acaf-005056bb47c1")
    resource.get()
    print(resource)

```

<br/>
#### Job status response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:21:12 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 345
Content-Type: application/hal+json
{
  "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
  "description": "POST /api/cluster/metrocluster/diagnostics",
  "state": "running",
  "message": "Checking nodes...",
  "code": 2432853,
  "start_time": "2020-09-22T13:20:53-04:00",
  "_links": {
    "self": {
      "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
    }
  }
}
```
#### Final status of the diagnostics job
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:29:04 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 372
Content-Type: application/hal+json
{
  "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
  "description": "POST /api/cluster/metrocluster/diagnostics",
  "state": "success",
  "message": "success",
  "code": 0,
  "start_time": "2020-09-22T13:20:53-04:00",
  "end_time": "2020-09-22T13:22:04-04:00",
  "_links": {
    "self": {
      "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
    }
  }
}
```
### Retrieving the diagnostics operation
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.get()
    print(resource)

```

#### Response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 18:04:28 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 1005
Content-Type: application/hal+json
{
  "node": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "interface": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "aggregate": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "cluster": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "connection": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "volume": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "config_replication": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "_links": {
    "self": {
      "href": "/api/cluster/metrocluster/diagnostics"
    }
  }
}
```
### Retrieving check details for the node component
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.get(fields="node.details")
    print(resource)

```

#### Response
```
HTTP/1.1 200 OK
Date: Thu, 10 Feb 2022 00:05:12 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 4506
Content-Type: application/hal+json
{
  "node": {
    "details": [
      {
        "node": {
          "uuid": "11111111-1111-1111-1111-111111111111",
          "name": "node1",
          "_links": {
            "self": {
              "href": "/api/cluster/nodes/11111111-1111-1111-1111-111111111111"
            }
          }
        },
        "cluster": {
          "uuid": "12121212-1212-1212-1212-121212121212",
          "name": "clusterA",
          "_links": {
            "self": {
              "href": "/api/cluster/12121212-1212-1212-1212-121212121212"
            }
          }
        },
        "timestamp": "2022-02-09T18:47:00-05:00",
        "checks": [
          {
            "name": "node_reachable",
            "result": "ok"
          },
          {
            "name": "metrocluster_ready",
            "result": "ok"
          },
          {
            "name": "local_ha_partner",
            "result": "ok"
          },
          {
            "name": "ha_mirroring_on",
            "result": "ok"
          },
          {
            "name": "ha_mirroring_op_state",
            "result": "ok"
          },
          {
            "name": "symmetric_ha_relationship",
            "result": "ok"
          },
          {
            "name": "remote_dr_partner",
            "result": "ok"
          },
          {
            "name": "dr_mirroring_on",
            "result": "ok"
          },
          {
            "name": "dr_mirroring_op_state",
            "result": "ok"
          },
          {
            "name": "symmetric_dr_relationship",
            "result": "ok"
          },
          {
            "name": "remote_dr_auxiliary_partner",
            "result": "ok"
          },
          {
            "name": "symmetric_dr_auxiliary_relationship",
            "result": "ok"
          },
          {
            "name": "storage_failover_enabled",
            "result": "ok"
          },
          {
            "name": "has_intercluster_lif",
            "result": "ok"
          },
          {
            "name": "node_object_limit",
            "result": "ok"
          },
          {
            "name": "automatic_uso",
            "result": "ok"
          }
        ]
      },
      {
        "node": {
          "uuid": "22222222-2222-2222-2222-222222222222",
          "name": "node2",
          "_links": {
            "self": {
              "href": "/api/cluster/nodes/22222222-2222-2222-2222-222222222222"
            }
          }
        },
        "cluster": {
          "uuid": "23232323-2323-2323-2323-232323232323",
          "name": "clusterB",
          "_links": {
            "self": {
              "href": "/api/cluster/23232323-2323-2323-2323-232323232323"
            }
          }
        },
        "timestamp": "2022-02-09T18:47:00-05:00",
        "checks": [
          {
            "name": "node_reachable",
            "result": "ok"
          },
          {
            "name": "metrocluster_ready",
            "result": "ok"
          },
          {
            "name": "local_ha_partner",
            "result": "ok"
          },
          {
            "name": "ha_mirroring_on",
            "result": "ok"
          },
          {
            "name": "ha_mirroring_op_state",
            "result": "ok"
          },
          {
            "name": "symmetric_ha_relationship",
            "result": "ok"
          },
          {
            "name": "remote_dr_partner",
            "result": "ok"
          },
          {
            "name": "dr_mirroring_on",
            "result": "ok"
          },
          {
            "name": "dr_mirroring_op_state",
            "result": "ok"
          },
          {
            "name": "symmetric_dr_relationship",
            "result": "ok"
          },
          {
            "name": "remote_dr_auxiliary_partner",
            "result": "ok"
          },
          {
            "name": "symmetric_dr_auxiliary_relationship",
            "result": "ok"
          },
          {
            "name": "storage_failover_enabled",
            "result": "ok"
          },
          {
            "name": "has_intercluster_lif",
            "result": "ok"
          },
          {
            "name": "node_object_limit",
            "result": "ok"
          },
          {
            "name": "automatic_uso",
            "result": "ok"
          }
        ]
      }
    ]
  },
  "_links": {
    "self": {
      "href": "/api/cluster/metrocluster/diagnostics"
    }
  }
}
```
### Retrieving check details for the volume component
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.get(fields="volume.details")
    print(resource)

```

#### Response
```
HTTP/1.1 200 OK
Cache-Control: no-cache,no-store,must-revalidate
Connection: close
Date: Fri, 08 Apr 2022 20:07:38 GMT
Server: libzapid-httpd
Vary: Accept-Encoding
Content-Length: 928
Content-Type: application/hal+json
{
  "volume": {
    "details": [
      {
        "checks": [
          {
            "name": "unmirrored_flexgroups",
            "result": "ok",
          }
        ]
      },
      {
        "checks": [
          {
            "name": "mixed_flexgroups",
            "result": "ok",
          }
        ]
      }
    ]
  },
  "_links": {
    "self": {
      "href": "/api/cluster/metrocluster/diagnostics"
    }
  }
}
```
### Related ONTAP Commands

* `metrocluster check run`
* `metrocluster check show`
* `metrocluster check node show`
* `metrocluster check aggregate show`
* `metrocluster check cluster show`
* `metrocluster check connection show`
* `metrocluster check volume show`"""

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


__all__ = ["MetroclusterDiagnostics", "MetroclusterDiagnosticsSchema"]
__pdoc__ = {
    "MetroclusterDiagnosticsSchema.resource": False,
    "MetroclusterDiagnosticsSchema.opts": False,
}


class MetroclusterDiagnosticsSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the MetroclusterDiagnostics object"""

    aggregate = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="aggregate", unknown=EXCLUDE, allow_none=True)
    r""" The aggregate field of the metrocluster_diagnostics."""

    cluster = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_cluster.MetroclusterDiagnosticsClusterSchema", data_key="cluster", unknown=EXCLUDE, allow_none=True)
    r""" The cluster field of the metrocluster_diagnostics."""

    config_replication = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_configreplication.MetroclusterDiagnosticsConfigreplicationSchema", data_key="config-replication", unknown=EXCLUDE, allow_none=True)
    r""" The config_replication field of the metrocluster_diagnostics."""

    connection = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_connection.MetroclusterDiagnosticsConnectionSchema", data_key="connection", unknown=EXCLUDE, allow_none=True)
    r""" The connection field of the metrocluster_diagnostics."""

    interface = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_interface.MetroclusterDiagnosticsInterfaceSchema", data_key="interface", unknown=EXCLUDE, allow_none=True)
    r""" The interface field of the metrocluster_diagnostics."""

    node = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_node.MetroclusterDiagnosticsNodeSchema", data_key="node", unknown=EXCLUDE, allow_none=True)
    r""" The node field of the metrocluster_diagnostics."""

    volume = marshmallow_fields.Nested("netapp_ontap.models.metrocluster_diagnostics_volume.MetroclusterDiagnosticsVolumeSchema", data_key="volume", unknown=EXCLUDE, allow_none=True)
    r""" The volume field of the metrocluster_diagnostics."""

    @property
    def resource(self):
        return MetroclusterDiagnostics

    gettable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

    patchable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

    postable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

class MetroclusterDiagnostics(Resource):
    """Allows interaction with MetroclusterDiagnostics objects on the host"""

    _schema = MetroclusterDiagnosticsSchema
    _path = "/api/cluster/metrocluster/diagnostics"






    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the results of a completed diagnostic operation for the MetroCluster configuration.

### Learn more
* [`DOC /cluster/metrocluster/diagnostics`](#docs-cluster-cluster_metrocluster_diagnostics)"""
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
        r"""Start a MetroCluster diagnostic operation or set up a schedule for the diagnostics to be run periodically.

### Learn more
* [`DOC /cluster/metrocluster/diagnostics`](#docs-cluster-cluster_metrocluster_diagnostics)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)




