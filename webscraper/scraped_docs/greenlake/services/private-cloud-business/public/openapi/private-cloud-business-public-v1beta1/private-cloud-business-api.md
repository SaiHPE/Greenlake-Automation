---
title: "HPE GreenLake for Private Cloud Business Edition System APIs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api.md"
scraped_at: "2026-06-07T06:13:38.093074+00:00Z"
---

# HPE GreenLake for Private Cloud Business Edition System APIs

HPE GreenLake for Private Cloud Business Edition System APIs

Version: 1.1.0
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

The HPE GreenLake for Private Cloud Business Edition Cloud Console API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake for Private Cloud Business Edition System APIs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api.yaml)

## configuration-analysis-reports

APIs to trigger and fetch configuration analysis rules execution
results for system


### Returns a list of config analysis rules execution results.

 - [GET /private-cloud-business/v1beta1/configuration-analysis-reports](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/configuration-analysis-reports/listlatestconfiganalysisreport.md): Returns the list of latest config analysis reports for all systems.
It also accepts 'filter' query parameter where if 'systemId' is provided as 'filter',
it returns the latest config analysis report for that system.

### Initiates config analysis rules execution.

 - [POST /private-cloud-business/v1beta1/configuration-analysis-reports](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/configuration-analysis-reports/executeconfiganalysisrules.md): Initiates execution of config analysis rules execution for the System
specified by 'systemId' in request body

### Returns a config analysis rules execution results for the provided reportId.

 - [GET /private-cloud-business/v1beta1/configuration-analysis-reports/{reportId}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/configuration-analysis-reports/listconfiganalysisreportbyid.md): Returns config analysis rules execution report identified by 'reportId'
parameter.

## systems

APIs for HPE GreenLake for Private Cloud Business Edition system operations.

### Get all System Software Catalogs.

 - [GET /private-cloud-business/v1beta1/system-software-catalogs](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/getsystemsoftwarecatalogs.md): Returns a list of all system software catalogs.
Use 'select' and 'filter' query parameters to customize the response returned by this API.
For example, to get the End User License Agreement (EULA) for catalog version 1.2.3.4, use '?select=eula&filter=version eq 1.2.3.4'. 
To get recommended systems for precheck to a given catalog version, use '?select=systemsWithUpdatePath&filter=version eq 1.2.3.4'.

### Get the System Software Catalog with specified id.

 - [GET /private-cloud-business/v1beta1/system-software-catalogs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/getsystemsoftwarecatalogbyid.md): Returns the system software catalog for the specified id.
Includes versions of the catalog and all constituent software components along with the End User License Agreement
and a list of systems with update path to the corresponding catalog version.

### Get information about all systems subject to query parameters.

 - [GET /private-cloud-business/v1beta1/systems](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/listsysteminfo.md): Returns the systems and their properties defined by the query parameters. Retrieving all of the properties for 
the system can take a long time because the amount of data is large. Use the ‘select’ query parameter to choose 
only the properties you want to retrieve for a system. For example, to get details of the id, name and software 
information for each system, use ‘?select=id,name,softwareInfo’

### Get information about the specified system subject to query parameters.

 - [GET /private-cloud-business/v1beta1/systems/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/getsysteminfo.md): Returns the system properties specified in the query parameters. 
Retrieving all of the properties for the system can take a long time because the 
amount of data is large. Use the  'select' query parameter to choose only the properties you want to retrieve.

For example, to get details of the system's id, name and software information, use '?select=id,name,softwareInfo'

### Modifies the system specified by systemId.

 - [PATCH /private-cloud-business/v1beta1/systems/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/patchsystem.md): Modify specified system.

### Initiates addition of a hypervisor cluster to system with the given id.

 - [POST /private-cloud-business/v1beta1/systems/{id}/add-hypervisor-cluster](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/addhypervisorclustertosystem.md): Adds the specified hypervisor cluster to the specified system. The user must have permissions to update this system. 
Returns a task identifier to be used by clients to track the progress of the operation.

### Initiate software update prechecks on the given System.

 - [POST /private-cloud-business/v1beta1/systems/{id}/software-prechecks](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/initiatesoftwareprechecks.md): Initiate a set of software update prechecks on the specified system and hypervisor clusters in it using the specified software catalog version.
This operation validates whether the software on system and its hypervisor clusters are ready to be updated to the target software catalog version.

### Initiate software update on the given System.

 - [POST /private-cloud-business/v1beta1/systems/{id}/software-update](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/initiatesoftwareupdate.md): Initiate a software update on the specified system and the hypervisor clusters in it using the specified software catalog version.
Before invoking this API, ensure that software update prechecks on the same parameters successfully completed and is valid.

### Resume the failed and paused software update on the selected System.

 - [POST /private-cloud-business/v1beta1/systems/{id}/software-update-resume](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/initiatesoftwareupdateresume.md): Resume the failed and paused software update on the specified system.
Invoke this API only after fixing the problems reported in software update.

### Refresh the Software Catalog versions available for the system identified by id.

 - [POST /private-cloud-business/v1beta1/systems/{id}/software-version-refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/systems/performsoftwareversionrefresh.md): Refresh the software catalogs and software versions on the specified system.
The current and available software catalog versions are recomputed based on the component versions running on the system and software catalogs available for update.

## vm-provisioning-policies

Virtual Machine Provisioning Policies operations

### Get a list of VM provisioning policies

 - [GET /private-cloud-business/v1beta1/vm-provisioning-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicieslist.md): Returns a list of VM provisioning policies according to the given query
parameters for paging, filtering, and sorting.

### Create VM provisioning policy

 - [POST /private-cloud-business/v1beta1/vm-provisioning-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicycreate.md): This API aids in creation of virtual machine provisioning policy

### Delete VM provisioning policy by policy id

 - [DELETE /private-cloud-business/v1beta1/vm-provisioning-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicydelete.md): Deletes the specified VM provisioning policy

### Get VM provisioning policy by policy id

 - [GET /private-cloud-business/v1beta1/vm-provisioning-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicy.md): Returns details for the specified VM provisioning policy.

### Update VM provisioning policy by policy id

 - [PATCH /private-cloud-business/v1beta1/vm-provisioning-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicyedit.md): Update attributes of the specified VM provisioning policy

## servers

### Get information about the specified system's servers.

 - [GET /private-cloud-business/v1beta1/systems/{id}/servers](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/servers/getsystemserversinfo.md): Get server information by system id 

Returns details about the servers for the specified system id. Retrieving all of the properties for all servers 
in a system can take a long time because the amount of data is large. Use the  'select' query parameter to choose 
only the properties you want to retrieve.

For example, to get the server id, name, serial number and hypervisor host, use ?select=id,name,serialNumber,hypervisorHost

### Get information about a system's specific server.

 - [GET /private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}](https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/servers/getsystemserverinfo.md): Get server details by system id and server id 

Returns information about a specific server on a specific system. Retrieving all of the properties for a server 
can take a long time because the amount of data is large. Use the select query parameter to choose only the 
properties you want to retrieve. 

For example, to get details of the server's id, name, serial number and hypervisor host, use ?select=id,name,serialNumber,hypervisorHost

