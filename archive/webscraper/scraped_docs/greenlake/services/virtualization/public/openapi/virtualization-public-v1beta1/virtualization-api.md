---
title: "Virtualization API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api.md"
scraped_at: "2026-06-07T06:13:41.423145+00:00Z"
---

# Virtualization API

Virtualization API

Version: 1.2.0
License: HPE End User License Agreement

## Servers

```
https://us-west.api.greenlake.hpe.com
```

```
https://eu-west.api.greenlake.hpe.com
```

```
https://eu-central.api.greenlake.hpe.com
```

```
https://ap-northeast.api.greenlake.hpe.com
```

## Security

### bearer

The Data Service Cloud Console API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Virtualization API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api.yaml)

## csp-machine-images

Operations on cloud service provider (CSP) machine images.

### Get a list of CSP machine images

 - [GET /virtualization/v1beta1/csp-machine-images](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-images/cspmachineimagelist.md): Returns a list of cloud service provider (CSP) machine images based on the query
parameters for paging, filtering, and sorting.

### Get details of a CSP machine image

 - [GET /virtualization/v1beta1/csp-machine-images/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-images/cspmachineimageget.md): Returns details of a specified cloud service provider (CSP) machine image.

## csp-machine-instance-types

Operations on cloud service provider (CSP) machine instance types.

### Get a list of CSP machine instance types

 - [GET /virtualization/v1beta1/csp-machine-instance-types](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instance-types/cspmachineinstancetypelist.md): Returns a list of cloud service provider (CSP) machine instance types based on the query
parameters for paging, filtering, and sorting.

### Get details of a CSP machine instance type

 - [GET /virtualization/v1beta1/csp-machine-instance-types/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instance-types/cspmachineinstancetypeget.md): Returns details of a specified cloud service provider (CSP) machine instance type.

## csp-machine-instances

Operations on cloud service provider (CSP) machine instances.

### Create CSP Machine Instance

 - [POST /virtualization/v1beta1/csp-machine-instances](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instances/createcspmachineinstance.md): Create CSP Machine Instance

### Terminate a CSP Machine Instance

 - [DELETE /virtualization/v1beta1/csp-machine-instances/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instances/terminatecspvminstance.md): Deletes the cloud service provider (CSP) machine instance.

### Power Off CSP Machine Instance

 - [POST /virtualization/v1beta1/csp-machine-instances/{id}/power-off](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instances/poweroffcspvminstance.md): Powers off the cloud service provider (CSP) machine instance.

### Power On CSP Machine Instance

 - [POST /virtualization/v1beta1/csp-machine-instances/{id}/power-on](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-instances/poweroncspvminstance.md): Powers on cloud service provider (CSP) machine instance.

## datastores

The datastores API allows the registration and management of datastores.

### Get all datastores across registered hypervisor managers.

 - [GET /virtualization/v1beta1/datastores](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/datastores/datastoreslist.md): List all the datastores across registered hypervisor managers.

### Create datastore

 - [POST /virtualization/v1beta1/datastores](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/datastores/createds.md): Create datastore

### Get a datastore identified by {datastore-id}

 - [GET /virtualization/v1beta1/datastores/{datastore-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/datastores/datastore.md): Details of a datastore

## hypervisor-clusters

The hypervisor clusters API enables you to get the details of the hypervisor clusters in a hypervisor manager.

### Get all clusters across registered hypervisor managers.

 - [GET /virtualization/v1beta1/hypervisor-clusters](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-clusters/hypervisorclusterlist.md): List all the hypervisors clusters across registered hypervisor managers.

### Get a hypervisor cluster resource identified by {cluster-id}

 - [GET /virtualization/v1beta1/hypervisor-clusters/{cluster-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-clusters/hypervisorcluster.md): Details of a hypervisors cluster.

## hypervisor-folders

The hypervisor folders API enables you to get the details of the hypervisor folders in a hypervisor manager.

### Get a hypervisor folder resource identified by {folder-id}

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/folders/{folder-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-folders/hypervisorfolder.md): Details of a hypervisors folder.

### Get all folders in a registered hypervisor manager.

 - [GET /virtualization/v1beta1/hypervisor-managers/{uuid}/folders](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-folders/hypervisorfolderlist.md): List all the hypervisors folders in a registered hypervisor manager.

## hypervisor-hosts

The hypervisor hosts API enables you to get the details of the hypervisor hosts in a hypervisor manager.

### Get all hosts across registered hypervisor managers.

 - [GET /virtualization/v1beta1/hypervisor-hosts](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-hosts/hypervisorhostlist.md): List all the hosts across registered hypervisor managers.

### Get a hypervisor host resource identified by {host-id}

 - [GET /virtualization/v1beta1/hypervisor-hosts/{host-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-hosts/hypervisorhost.md): Details of a hypervisors host.

## hypervisor-managers

The hypervisor managers API allows the registration and management of hypervisor managers.

### Get all registered hypervisor managers.

 - [GET /virtualization/v1beta1/hypervisor-managers](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/hypervisormanagerlist.md): List all the registered hypervisor managers.

### Get a hypervisor manager resource identified by {hypervisor-id}.

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/hypervisormanager.md): Get detailed information for a registered hypervisor manager qualified by hypervisor-id.

### Get all virtual machine images from the hypervisor library.

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/listvirtualmachineimages.md): List all virtual machine images from the hypervisor library.

### Get a hypervisor library image identified by {hypervisor-library-image-id}

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images/{hypervisor-library-image-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/getvirtualmachineimage.md): Details of a virtual machine image

### Refresh the specified hypervisor manager

 - [POST /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/hypervisorrefresh.md): Updates the properties of the specified hypervisor manager

## hypervisor-networks

The hypervisor networks API enables you to get the details of the hypervisor networks in a hypervisor manager.

### Get a hypervisor network resource identified by {network-id}

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/networks/{network-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-networks/hypervisornetwork.md): Details of a hypervisors network resource.

### Get all network resources in a registered hypervisor manager.

 - [GET /virtualization/v1beta1/hypervisor-managers/{uuid}/networks](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-networks/hypervisornetworklist.md): List all the network resources in a registered hypervisor manager.

## hypervisor-tags

The hypervisor tags API enables you to get the details of the hypervisor tags in a hypervisor manager.

### Get a hypervisor tag resource identified by {tag-id}

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/tags/{tag-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-tags/hypervisortag.md): Details of a hypervisors tag resource.

### Get all tag resources in a registered hypervisor manager.

 - [GET /virtualization/v1beta1/hypervisor-managers/{uuid}/tags](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-tags/hypervisortaglist.md): List all the tag resources in a registered hypervisor manager.

## resource-pools

The resource pool API enables you to get the details of the hypervisor resource pools in a hypervisor manager.

### Get a hypervisor resource pool identified by {pool-id}.

 - [GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/resource-pools/{pool-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/resource-pools/hypervisorresourcepool.md): Details of a hypervisors resource pool.

### Get all resource pools in a registered hypervisor manager (vCenter).

 - [GET /virtualization/v1beta1/hypervisor-managers/{uuid}/resource-pools](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/resource-pools/hypervisorresourcepoollist.md): List all the hypervisors resource pools in a registered hypervisor manager (vCenter).

## virtual-machines

The virtual machines API allows the registration and management of virtual machines.

### Get all virtual machines across registered hypervisor managers.

 - [GET /virtualization/v1beta1/virtual-machines](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/virtualmachineslist.md): List all the virtual machines across registered hypervisor managers.

### Deploy virtual machine

 - [POST /virtualization/v1beta1/virtual-machines](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/hcideployvm.md): Deploys one or more virtual machines in HCI environment with specified template and storage provisioning policy.

### Delete a virtual machine

 - [DELETE /virtualization/v1beta1/virtual-machines/{vm-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmdelete.md): Delete a virtual machine

### Get a virtual machine identified by {vm-id}

 - [GET /virtualization/v1beta1/virtual-machines/{vm-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/virtualmachine.md): Details of a virtual machine

### Power off a virtual machine

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/power-off](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmpoweroff.md): Power off a virtual machine

### Power on a virtual machine

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/power-on](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmpoweron.md): Power on a virtual machine

### Refresh the specified virtual machine instance

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmrefresh.md): Updates the properties of the specified virtual machine instance

### Reset a virtual machine

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/reset](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmpowerreset.md): Reset a virtual machine

### Restart guest OS of a virtual machine

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/restart-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmrestartguestos.md): Restart guest OS of a virtual machine

### Shutdown guest OS of a virtual machine

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/shutdown-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/vmshutdownguestos.md): Shutdown guest OS of a virtual machine

### Reconfigure virtual machine hardware configurations

 - [POST /virtualization/v1beta1/virtual-machines/{vm-id}/update-hardware](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/editvm.md): Updates CPU, memory, network adapters, and disks of a virtual machine. This operation can be performed when the virtual machine is powered off.

### Migrate virtual machines

 - [POST /virtualization/v1beta1/virtual-machines/migrate](https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/migratevm.md): Migrate virtual machines to another cluster or datastore

