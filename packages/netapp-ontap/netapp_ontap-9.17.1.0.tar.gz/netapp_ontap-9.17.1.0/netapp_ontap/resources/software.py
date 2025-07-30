r"""
Copyright &copy; 2025 NetApp Inc.
All rights reserved.

This file has been automatically generated based on the ONTAP REST API documentation.

## Overview
You can use the ONTAP cluster software API to retrieve and display relevant information about a software profile, software packages collection, software history collection, and firmware packages collection. This API retrieves the information about all software packages present in the cluster, or a specific software package, or firmware upgrade status.
<br/>You can use the POST request to download a software package/firmware from an HTTP or FTP server. The PATCH request provides the option to upgrade the cluster software version. Select the `validate_only` field to validate the package before triggering the update. Set the `version` field to trigger the installation of the package in the cluster. You can pause, resume, or cancel any ongoing software upgrade by selecting `action`. You can use the DELETE request to remove a specific software package present in the cluster.
---
## Examples
### Retrieving software profile information
The following example shows how to retrieve software and firmware profile information. You can check the validation results after selecting the `validate_only` field. Upgrade progress information is available after an upgrade has started.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.get(return_timeout=15)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Software(
    {
        "metrocluster": {
            "progress_details": {
                "message": 'Installing software image on cluster "sti70-vsim-ucs165n_siteA".'
            },
            "clusters": [
                {
                    "estimated_duration": 3480,
                    "elapsed_duration": 0,
                    "state": "waiting",
                    "name": "sti70-vsim-ucs165n_siteA",
                }
            ],
            "progress_summary": {"message": "Update paused by user"},
        },
        "validation_results": [
            {
                "status": "warning",
                "update_check": "NFS mounts",
                "issue": {"message": "Use NFS hard mounts, if possible."},
                "action": {"message": "Use NFS hard mounts, if possible."},
            }
        ],
        "version": "9.5.0",
        "_links": {"self": {"href": "/api/cluster/software/"}},
        "nodes": [
            {
                "version": "9.5.0",
                "firmware": {
                    "cluster_fw_progress": [
                        {
                            "update_type": "automatic_update",
                            "zip_file_name": "abc.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 2",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                        {
                            "update_type": "manual_update",
                            "zip_file_name": "xyz.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 2",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                    ],
                    "shelf": {"in_progress_count": 2, "update_status": "idle"},
                    "disk": {
                        "num_waiting_download": 0,
                        "total_completion_estimate": 0,
                        "average_duration_per_disk": 120,
                        "update_status": "idle",
                    },
                    "dqp": {
                        "version": "3.17",
                        "revision": "20200117",
                        "record_count": {
                            "drive": 680,
                            "system": 3,
                            "alias": 200,
                            "device": 29,
                        },
                        "file_name": "qual_devices_v2",
                    },
                    "sp_bmc": {
                        "start_time": "2018-05-21T09:53:04+05:30",
                        "is_current": True,
                        "in_progress": False,
                        "fw_type": "SP",
                        "running_version": "1.2.3.4",
                        "image": " primary",
                        "autoupdate": False,
                        "end_time": "2018-05-21T09:53:04+05:30",
                        "percent_done": 100,
                    },
                },
            }
        ],
        "status_details": [
            {
                "start_time": "2018-05-21T09:53:04+05:30",
                "issue": {"message": "Image update complete", "code": 0},
                "state": "completed",
                "node": {"name": "sti70-vsim-ucs165n"},
                "end_time": "2018-05-21T11:53:04+05:30",
                "name": "do-download-job",
            }
        ],
        "state": "in_progress",
        "update_details": [
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "state": "in_progress",
                "node": {"name": "sti70-vsim-ucs165n"},
                "elapsed_duration": 29,
            }
        ],
        "pending_version": "9.6.0",
    }
)

```
</div>
</div>

---
### Upgrading the software version
The following example shows how to upgrade cluster software. Set the `version` field to trigger the installation of the package. You can select the `validate_only` field to validate the package before the installation starts. Setting `skip_warning` as `true` ignores the validation warning before the installation starts. Setting the `action` field performs a `pause`, `resume`, or `cancel' operation on an ongoing upgrade. An upgrade can only be resumed if it is in the paused state. Setting `stabilize_minutes` allows each node a specified amount of time to stabilize after a reboot; the default is 8 minutes. If `show_validation_details` is set to "true", all validation details will be shown in the output.
<br/>You can start the upgrade process at the cluster level. There are no options available to start the upgrade for a specific node or HA pair.
#### 1. Validating the package and verifying the validation results
The following example shows how to validate a cluster software package. You must validate the package before the software upgrade. Set the `validate_only` field to `true` to start the validation. You can check for validation results in the GET /cluster/software endpoint.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt_ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.version = "9.5.0"
    resource.patch(hydrate=True, validate_only=True)

```

---
The call to validate the software cluster version returns the job UUID, including a HAL link to retrieve details about the job. The job object includes a `state` field and a message to indicate the progress of the job. When the job is complete and the application is fully created, the message indicates success and the `state` field of the job is set to `success`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="f587d316-5feb-11e8-b0e0-005056956dfc")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Job(
    {
        "message": "success",
        "state": "success",
        "code": 0,
        "description": "PATCH /api/cluster/software",
        "uuid": "f587d316-5feb-11e8-b0e0-005056956dfc",
        "_links": {
            "self": {"href": "/api/cluster/jobs/f587d316-5feb-11e8-b0e0-005056956dfc"}
        },
    }
)

```
</div>
</div>

---
You can check for validation results in the GET /cluster/software endpoint. The following example shows how to check the validation warnings and errors after setting the `validate_only` field to `true`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Software(
    {
        "validation_results": [
            {
                "status": "error",
                "update_check": "High Availability status",
                "issue": {
                    "message": 'Cluster HA is not configured in the cluster. Storage failover is not enabled on node "node1", "node2".'
                },
                "action": {
                    "message": "Check cluster HA configuration. Check storage failover status."
                },
            },
            {
                "status": "warning",
                "update_check": "Manual checks",
                "issue": {
                    "message": 'Manual validation checks need to be performed. Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update. Failing to do so can result in an update failure or an I/O disruption.'
                },
                "action": {
                    "message": 'Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update.'
                },
            },
        ],
        "version": "9.7.0",
        "_links": {"self": {"href": "/api/cluster/software"}},
        "estimated_duration": 600,
        "nodes": [
            {
                "version": "9.5.0",
                "firmware": {
                    "cluster_fw_progress": [
                        {
                            "update_type": "automatic_update",
                            "zip_file_name": "abc.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 2",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                        {
                            "update_type": "automatic_update",
                            "zip_file_name": "xyz.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 2",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                    ],
                    "shelf": {"in_progress_count": 2, "update_status": "idle"},
                    "disk": {
                        "num_waiting_download": 0,
                        "total_completion_estimate": 0,
                        "average_duration_per_disk": 120,
                        "update_status": "idle",
                    },
                    "dqp": {
                        "version": "3.17",
                        "revision": "20200117",
                        "record_count": {
                            "drive": 680,
                            "system": 3,
                            "alias": 200,
                            "device": 29,
                        },
                        "file_name": "qual_devices_v2",
                    },
                    "sp_bmc": {
                        "start_time": "2018-05-21T09:53:04+05:30",
                        "is_current": True,
                        "in_progress": False,
                        "fw_type": "SP",
                        "running_version": "1.2.3.4",
                        "image": " primary",
                        "autoupdate": False,
                        "end_time": "2018-05-21T09:53:04+05:30",
                        "percent_done": 100,
                    },
                },
            }
        ],
        "state": "failed",
        "elapsed_duration": 56,
    }
)

```
</div>
</div>

---
#### 2. Updating the cluster
The following example shows how to initiate a cluster software upgrade. You must validate the package before the software upgrade starts. Set the `skip_warnings` field to `true` to skip validation warnings and start the software package upgrade. You can specify the `stabilize_minutes` value between 1 to 60 minutes. Setting `stabilize_minutes` allows each node a specified amount of time to stabilize after a reboot; the default is 8 minutes. If the value of `show_validation_details` is set to "true", then all validation details will be shown in the output. By default, on non-MetroCluster configurations, nodes at the target release will be skipped over. However, this can be disabled by setting `skip_nodes_at_target_version` to `false`. Note: it is invalid to set `skip_nodes_at_target_version` to `true` in pause, resume, or cancel actions. `skip_nodes_at_target_version` cannot be set to `true` in MetroCluster configurations.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt_ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.version = "9.5.0"
    resource.patch(hydrate=True, skip_warnings=True)

```

---
The call to update the software cluster version returns the job UUID, including a HAL link to retrieve details about the job. The job object includes a `state` field and a message to indicate the progress of the job. When the job is complete and the application is fully created, the message indicates success and the `state` field of the job is set to `success`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="f587d316-5feb-11e8-b0e0-005056956dfc")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Job(
    {
        "message": "success",
        "state": "success",
        "code": 0,
        "description": "PATCH /api/cluster/software",
        "uuid": "f587d316-5feb-11e8-b0e0-005056956dfc",
        "_links": {
            "self": {"href": "/api/cluster/jobs/f587d316-5feb-11e8-b0e0-005056956dfc"}
        },
    }
)

```
</div>
</div>

---
You can check the update progress information in the GET /cluster/software endpoint. The following example shows how to check the progress of an update after setting the `skip_warnings` field to `true`. Each node's object also includes information about the firmware update status on the node.      <br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
Software(
    {
        "validation_results": [
            {
                "status": "warning",
                "update_check": "Manual checks",
                "issue": {
                    "message": 'Manual validation checks need to be performed. Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update. Failing to do so can result in an update failure or an I/O disruption.'
                },
                "action": {
                    "message": 'Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update.'
                },
            }
        ],
        "version": "9.7.0",
        "_links": {"self": {"href": "/api/cluster/software"}},
        "estimated_duration": 5220,
        "nodes": [
            {
                "version": "9.5.0",
                "firmware": {
                    "cluster_fw_progress": [
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "abc.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 3",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3498",
                                        "name": "Node 4",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "xyz.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 2",
                                    },
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                    ],
                    "shelf": {"in_progress_count": 2, "update_status": "idle"},
                    "disk": {
                        "num_waiting_download": 0,
                        "total_completion_estimate": 0,
                        "average_duration_per_disk": 120,
                        "update_status": "idle",
                    },
                    "dqp": {
                        "version": "3.17",
                        "revision": "20200117",
                        "record_count": {
                            "drive": 680,
                            "system": 3,
                            "alias": 200,
                            "device": 29,
                        },
                        "file_name": "qual_devices_v2",
                    },
                    "sp_bmc": {
                        "start_time": "2018-05-21T09:53:04+05:30",
                        "is_current": True,
                        "in_progress": False,
                        "fw_type": "SP",
                        "running_version": "1.2.3.4",
                        "image": " primary",
                        "autoupdate": False,
                        "end_time": "2018-05-21T09:53:04+05:30",
                        "percent_done": 100,
                    },
                },
            }
        ],
        "status_details": [
            {
                "start_time": "2019-01-14T23:12:14+05:30",
                "issue": {"message": "Installing software image.", "code": 10551400},
                "node": {"name": "node1"},
                "end_time": "2019-01-14T23:12:14+05:30",
                "name": "do-download-job",
            },
            {
                "start_time": "2019-01-14T23:12:14+05:30",
                "issue": {"message": "Installing software image.", "code": 10551400},
                "node": {"name": "node2"},
                "end_time": "2019-01-14T23:12:14+05:30",
                "name": "do-download-job",
            },
        ],
        "state": "in_progress",
        "elapsed_duration": 63,
        "update_details": [
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "node": {"name": "node1"},
                "elapsed_duration": 10,
            },
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "node": {"name": "node2"},
                "elapsed_duration": 10,
            },
        ],
        "pending_version": "9.7.0",
    }
)

```
</div>
</div>

---
In the case of a post update check failure, the details are available under the heading "post_update_checks" in the GET /cluster/software endpoint.
The following example shows how to check the progress of an update after a post update check has failed. Each node's object also includes information about the firmware update status on the node.      <br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
Software(
    {
        "validation_results": [
            {
                "status": "warning",
                "update_check": "Manual checks",
                "issue": {
                    "message": 'Manual validation checks need to be performed. Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update. Failing to do so can result in an update failure or an I/O disruption.'
                },
                "action": {
                    "message": 'Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update.'
                },
            }
        ],
        "version": "9.7.0",
        "_links": {"self": {"href": "/api/cluster/software"}},
        "estimated_duration": 5220,
        "nodes": [
            {
                "version": "9.5.0",
                "firmware": {
                    "cluster_fw_progress": [
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "abc.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "working",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "<message catalog text>",
                                    "code": 3,
                                },
                                {
                                    "status": "completed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 2",
                                    },
                                    "message": "Error message",
                                    "code": 0,
                                },
                            ],
                        },
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "xyz.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "completed",
                                    "attempts": 1,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Error message",
                                    "code": 0,
                                },
                                {
                                    "status": "completed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 2",
                                    },
                                    "message": "Error message",
                                    "code": 0,
                                },
                            ],
                        },
                    ],
                    "shelf": {"in_progress_count": 2, "update_status": "idle"},
                    "disk": {
                        "num_waiting_download": 0,
                        "total_completion_estimate": 0,
                        "average_duration_per_disk": 120,
                        "update_status": "idle",
                    },
                    "dqp": {
                        "version": "3.17",
                        "revision": "20200117",
                        "record_count": {
                            "drive": 680,
                            "system": 3,
                            "alias": 200,
                            "device": 29,
                        },
                        "file_name": "qual_devices_v2",
                    },
                    "sp_bmc": {
                        "start_time": "2018-05-21T09:53:04+05:30",
                        "is_current": True,
                        "in_progress": True,
                        "fw_type": "SP",
                        "running_version": "1.2.3.4",
                        "image": " primary",
                        "autoupdate": False,
                        "end_time": "2018-05-21T09:53:04+05:30",
                        "percent_done": 100,
                    },
                },
            }
        ],
        "status_details": [
            {
                "start_time": "2019-01-14T23:12:14+05:30",
                "issue": {"message": "Image update complete.", "code": 0},
                "node": {"name": "node1"},
                "end_time": "2019-01-14T23:12:14+05:30",
                "name": "do-download-job",
            },
            {
                "start_time": "2019-01-14T23:12:14+05:30",
                "issue": {"message": "Image update complete.", "code": 0},
                "node": {"name": "node2"},
                "end_time": "2019-01-14T23:12:14+05:30",
                "name": "do-download-job",
            },
        ],
        "post_update_checks": [
            {
                "status": "error",
                "update_check": "Aggregate Health Status",
                "issue": {"message": "Not all aggregates are online"},
                "action": {"message": "Ensure all aggregates are online."},
            },
            {
                "status": "error",
                "update_check": "HA Health Status",
                "issue": {
                    "message": "Storage failover is not enabled on nodes of the cluster."
                },
                "action": {
                    "message": "Ensure storage failover is enabled on all nodes of the cluster."
                },
            },
        ],
        "state": "in_progress",
        "elapsed_duration": 63,
        "update_details": [
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "node": {"name": "node1"},
                "elapsed_duration": 3120,
            },
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "node": {"name": "node2"},
                "elapsed_duration": 3210,
            },
            {
                "estimated_duration": 600,
                "phase": "Post-update checks",
                "node": {"name": "node2"},
                "elapsed_duration": 10,
            },
        ],
        "pending_version": "9.7.0",
    }
)

```
</div>
</div>

---
#### 3. Pausing, resuming or canceling an upgrade
The following example shows how to `pause` an ongoing cluster software package upgrade. Set the `action` field to `pause`, `resume`, or `cancel` to pause, resume or cancel the upgrade respectively. Not all update operations support these actions. An update can only be resumed if it is in the paused state.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt_ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.version = "9.5.0"
    resource.patch(hydrate=True, action="pause")

```

---
The call to update the software cluster version and/or firmware version returns the job UUID, including a HAL link to retrieve details about the job. The job object includes a `state` field and a message to indicate the progress of the job. When the job is complete and the application is fully created, the message indicates success and the `state` field of the job is set to `success`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="f587d316-5feb-11e8-b0e0-005056956dfc")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Job(
    {
        "message": "success",
        "state": "success",
        "code": 0,
        "description": "PATCH /api/cluster/software",
        "uuid": "f587d316-5feb-11e8-b0e0-005056956dfc",
        "_links": {
            "self": {"href": "/api/cluster/jobs/f587d316-5feb-11e8-b0e0-005056956dfc"}
        },
    }
)

```
</div>
</div>

---
You can check the progress of the upgrade in the GET /cluster/software endpoint. The following example shows how to check the progress of the pause upgrade state after setting the `action` field to `pause`.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Software()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example10_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example10_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example10_result" class="try_it_out_content">
```
Software(
    {
        "validation_results": [
            {
                "status": "warning",
                "update_check": "Manual checks",
                "issue": {
                    "message": 'Manual validation checks need to be performed. Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update. Failing to do so can result in an update failure or an I/O disruption.'
                },
                "action": {
                    "message": 'Refer to the Upgrade Advisor Plan or the "What should I verify before I upgrade with or without Upgrade Advisor" section in the "Upgrade ONTAP" documentation for the remaining validation checks that need to be performed before update.'
                },
            }
        ],
        "version": "9.7.0",
        "_links": {"self": {"href": "/api/cluster/software"}},
        "estimated_duration": 5220,
        "nodes": [
            {
                "version": "9.5.0",
                "firmware": {
                    "cluster_fw_progress": [
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "abc.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                        {
                            "update_type": "automated_update",
                            "zip_file_name": "xyz.zip",
                            "job": {
                                "uuid": "5a21663c-a9a0-11ea-af9a-005056bb44d7",
                                "_links": {
                                    "self": {
                                        "href": "/api/cluster/jobs/5a21663c-a9a0-11ea-af9a-005056bb44d7"
                                    }
                                },
                            },
                            "update_state": [
                                {
                                    "status": "failed",
                                    "attempts": 3,
                                    "worker_node": {
                                        "uuid": "fcd40f70-f531-11eb-b235-005056bb3497",
                                        "name": "Node 1",
                                    },
                                    "message": "Cannot open the local staging zip file.",
                                    "code": 2228325,
                                },
                                {
                                    "status": "complete",
                                    "attempts": 3,
                                    "message": "Success",
                                    "code": 0,
                                },
                            ],
                        },
                    ],
                    "shelf": {"in_progress_count": 2, "update_status": "idle"},
                    "disk": {
                        "num_waiting_download": 0,
                        "total_completion_estimate": 0,
                        "average_duration_per_disk": 120,
                        "update_status": "idle",
                    },
                    "dqp": {
                        "version": "3.17",
                        "revision": "20200117",
                        "record_count": {
                            "drive": 680,
                            "system": 3,
                            "alias": 200,
                            "device": 29,
                        },
                        "file_name": "qual_devices_v2",
                    },
                    "sp_bmc": {
                        "start_time": "2018-05-21T09:53:04+05:30",
                        "is_current": True,
                        "in_progress": False,
                        "fw_type": "SP",
                        "running_version": "1.2.3.4",
                        "image": " primary",
                        "autoupdate": False,
                        "end_time": "2018-05-21T09:53:04+05:30",
                        "percent_done": 100,
                    },
                },
            }
        ],
        "status_details": [
            {
                "start_time": "2019-01-08T02:54:36+05:30",
                "issue": {"message": "Installing software image.", "code": 10551400},
                "node": {"name": "node1"},
            },
            {
                "start_time": "2019-01-08T02:54:36+05:30",
                "issue": {"message": "Installing software image.", "code": 10551400},
                "node": {"name": "node2"},
            },
        ],
        "state": "pause_pending",
        "elapsed_duration": 103,
        "update_details": [
            {
                "estimated_duration": 600,
                "phase": "Pre-update checks",
                "node": {"name": "node1"},
                "elapsed_duration": 54,
            },
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "node": {"name": "node2"},
                "elapsed_duration": 49,
            },
            {
                "estimated_duration": 4620,
                "phase": "Data ONTAP updates",
                "elapsed_duration": 49,
            },
        ],
        "pending_version": "9.7.0",
    }
)

```
</div>
</div>

---
### Uploading a software/firmware package
The following example shows how to upload a software package.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Software

with HostConnection(
    "<mgmt-ip>", username="username", password="password", verify=False
):
    resource = Software()
    resource.upload()

```
<div class="try_it_out">
<input id="example11_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example11_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example11_result" class="try_it_out_content">
```
Software({})

```
</div>
</div>

---"""

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


__all__ = ["Software", "SoftwareSchema"]
__pdoc__ = {
    "SoftwareSchema.resource": False,
    "SoftwareSchema.opts": False,
}


class SoftwareSchema(ResourceSchema, metaclass=ResourceSchemaMeta):
    """The fields of the Software object"""

    links = marshmallow_fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE, allow_none=True)
    r""" The links field of the software."""

    action = marshmallow_fields.Str(
        data_key="action",
        validate=enum_validation(['pause', 'cancel', 'resume']),
        allow_none=True,
    )
    r""" User triggered action to apply to the install operation

Valid choices:

* pause
* cancel
* resume"""

    elapsed_duration = Size(
        data_key="elapsed_duration",
        allow_none=True,
    )
    r""" Elapsed time during the upgrade or validation operation

Example: 2140"""

    estimated_duration = Size(
        data_key="estimated_duration",
        allow_none=True,
    )
    r""" Overall estimated time for completion of the upgrade or validation operation.

Example: 5220"""

    metrocluster = marshmallow_fields.Nested("netapp_ontap.models.software_reference_metrocluster.SoftwareReferenceMetroclusterSchema", data_key="metrocluster", unknown=EXCLUDE, allow_none=True)
    r""" The metrocluster field of the software."""

    nodes = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.software_node.SoftwareNodeSchema", unknown=EXCLUDE, allow_none=True), data_key="nodes", allow_none=True)
    r""" List of nodes, active versions, and firmware update progressions."""

    pending_version = marshmallow_fields.Str(
        data_key="pending_version",
        allow_none=True,
    )
    r""" Version being installed on the system.

Example: ONTAP_X_1"""

    post_update_checks = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.software_validation.SoftwareValidationSchema", unknown=EXCLUDE, allow_none=True), data_key="post_update_checks", allow_none=True)
    r""" List of failed post-update checks' warnings, errors, and advice."""

    state = marshmallow_fields.Str(
        data_key="state",
        validate=enum_validation(['in_progress', 'waiting', 'paused_by_user', 'paused_on_error', 'completed', 'canceled', 'failed', 'pause_pending', 'cancel_pending']),
        allow_none=True,
    )
    r""" Operational state of the upgrade

Valid choices:

* in_progress
* waiting
* paused_by_user
* paused_on_error
* completed
* canceled
* failed
* pause_pending
* cancel_pending"""

    status_details = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.software_status_details.SoftwareStatusDetailsSchema", unknown=EXCLUDE, allow_none=True), data_key="status_details", allow_none=True)
    r""" Display status details."""

    update_details = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.software_update_details.SoftwareUpdateDetailsSchema", unknown=EXCLUDE, allow_none=True), data_key="update_details", allow_none=True)
    r""" Display update progress details."""

    validation_results = marshmallow_fields.List(marshmallow_fields.Nested("netapp_ontap.models.software_validation.SoftwareValidationSchema", unknown=EXCLUDE, allow_none=True), data_key="validation_results", allow_none=True)
    r""" List of validation warnings, errors, and advice."""

    version = marshmallow_fields.Str(
        data_key="version",
        allow_none=True,
    )
    r""" Version of ONTAP installed and currently active on the system. During PATCH, using the 'validate_only' parameter on the request executes pre-checks, but does not perform the full installation.

Example: ONTAP_X"""

    @property
    def resource(self):
        return Software

    gettable_fields = [
        "links",
        "action",
        "elapsed_duration",
        "estimated_duration",
        "metrocluster",
        "nodes",
        "pending_version",
        "post_update_checks",
        "state",
        "status_details",
        "update_details",
        "validation_results",
        "version",
    ]
    """links,action,elapsed_duration,estimated_duration,metrocluster,nodes,pending_version,post_update_checks,state,status_details,update_details,validation_results,version,"""

    patchable_fields = [
        "action",
        "metrocluster",
        "version",
    ]
    """action,metrocluster,version,"""

    postable_fields = [
        "action",
        "metrocluster",
        "version",
    ]
    """action,metrocluster,version,"""

class Software(Resource):
    """Allows interaction with Software objects on the host"""

    _schema = SoftwareSchema
    _path = "/api/cluster/software"
    _action_form_data_parameters = { 'file':'file', }






    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the software profile of a cluster.
### Related ONTAP commands
* `cluster image show`
* `cluster image show-update-progress`
* `system node image package show`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cluster software version.
Important note:
  * Setting 'version' triggers the package installation.
  * To validate the package for installation but not perform the installation, use the `validate_only` field on the request.
### Required properties
* `version` - Software version to be installed on the cluster.
### Recommended optional parameters
* `validate_only` - Required to validate a software package before an upgrade.
* `skip_warnings` - Used to skip validation warnings when starting a software upgrade.
* `action` - Used to pause, resume, or cancel an ongoing software upgrade.
* `stabilize_minutes` - Specifies a custom value between 1 to 60 minutes that allows each node a specified amount of time to stabilize after a reboot; the default is 8 minutes.
* `estimate_only` - Estimates the time duration; does not perform any update.
* `nodes_to_update` - Specifies a subset of the cluster's nodes for update.
* `show_validation_details` - If the value is set to true, then all validation details will be shown in the output.
* `skip_nodes_at_target_version` - If the value is set to true, then nodes already at the target version will not be upgraded. Defaults to true in non-MetroCluster configurations. Setting this option to false will force all the selected nodes of the cluster to undergo upgrade.
### Related ONTAP commands
* `cluster image validate`
* `cluster image update`
* `cluster image pause-update`
* `cluster image resume-update`
* `cluster image cancel-update`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)


    def upload(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Uploads a software or firmware package located on the local filesystem.
### Related ONTAP commands
* `cluster image package get`
### Learn more
* [`DOC /cluster/software`](#docs-cluster-cluster_software)
"""
        return super()._action(
            "upload", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    upload.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)

