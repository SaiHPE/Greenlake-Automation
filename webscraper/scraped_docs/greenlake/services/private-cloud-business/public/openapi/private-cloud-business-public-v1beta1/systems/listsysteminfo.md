---
title: "GET /private-cloud-business/v1beta1/systems"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/systems/listsysteminfo.md"
scraped_at: "2026-06-07T06:15:38.434674+00:00Z"
---

# Get information about all systems subject to query parameters.

Returns the systems and their properties defined by the query parameters. Retrieving all of the properties for 
the system can take a long time because the amount of data is large. Use the ‘select’ query parameter to choose 
only the properties you want to retrieve for a system. For example, to get details of the id, name and software 
information for each system, use ‘?select=id,name,softwareInfo’

Endpoint: GET /private-cloud-business/v1beta1/systems
Version: 1.1.0
Security: bearer

## Query parameters:

  - `select` (string)
    Query parameter listing the properties of system information to fetch.
Although Hypervisor Clusters collection (property hypervisorClusters) can be selected, selecting elements of the collection is not supported.
Similarly, hypervisor clusters update status collection (property softwareInfo.hypervisorClusters) can be selected, but, selecting elements of the collection is not supported in the select query parameter.
Although systemVms collection can be selected, selecting elements of the collection is not supported.
    Example: "id,name,softwareInfo"

  - `offset` (integer)
    Use offset in conjunction with limit for paging, e.g.: offset=30&&limit=10. Offset is the number of items from the beginning of the result set to the first item included in the response.
    Example: 30

  - `limit` (integer)
    Use limit in conjunction with offset for paging, e.g.: offset=30&&limit=10. Limit is the maximum number of items to include in the response.
    Example: 10

  - `filter` (string)
    The expression to filter responses.
This API doesn't support filtering based on hypervisorClusters collection property, softwareInfo.hypervisorClusters and systemVms collection property.
Request with filter based on the above mentioned properties will be treated as a Bad Request with 400 Error.
    Example: "health/overallHealth eq OK"

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified the
default order is ascending.
This API doesn't support sorting based on hypervisorClusters collection property, softwareInfo.hypervisorClusters collection property and systemVms collection property.
Request with sort based on the above mentioned properties will be treated as a Bad Request with 400 Error.
    Example: "id desc,name asc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.associatedResourceCounts` (object)
    Associated Resource Information of system.

  - `items.associatedResourceCounts.datastoreCount` (number)
    Total Datastore Count of the system

  - `items.associatedResourceCounts.hypervisorClusterCount` (number)
    Total Hypervisor Cluster Count of the system

  - `items.associatedResourceCounts.serversCount` (number)
    Total Servers Count of the system

  - `items.associatedResourceCounts.storageArrayCount` (number)
    Total Storage Array Count of the system

  - `items.associatedResourceCounts.switchesCount` (number)
    Total Switches Count of the system

  - `items.associatedResourceCounts.vmCount` (number)
    Total Virtual Machine Count of the system

  - `items.computeUsage` (object)
    System Compute Usage Information.

  - `items.computeUsage.cpuCapacityMhz` (number)
    CPU Capacity in Mhz of system

  - `items.computeUsage.cpuUsedMhz` (number)
    CPU Usage in Mhz by system

  - `items.computeUsage.memoryCapacityBytes` (number)
    Memory Capacity in Bytes of system

  - `items.computeUsage.memoryUsedBytes` (number)
    Memory Usage in Bytes by system

  - `items.configAnalysisStatus` (object)
    Status of last run of configuration analysis job.

  - `items.configAnalysisStatus.createdAt` (string)
    Time when configuration analysis job was created.

  - `items.configAnalysisStatus.createdBy` (string)
    Configuration analysis job was created by.

  - `items.configAnalysisStatus.nextScheduledRunTime` (string)
    Time when configuration analysis job was next scheduled.

  - `items.configAnalysisStatus.ruleRunStartTime` (string)
    Time when configuration analysis job was started.

  - `items.configAnalysisStatus.totalFailed` (number)
    Count of failed checks.

  - `items.configAnalysisStatus.totalPassed` (number)
    Count of passed checks.

  - `items.configAnalysisStatus.totalWarning` (number)
    Count of warning checks.

  - `items.health` (object)
    Aspects of system health.

Deduced health of storage subsystem based on associated arrays, controllers, disks,
shelves, power supply, network interfaces, fan and temperature sensors.

Aggregated health of servers based on health statuses of multiple servers in the system.

Aggregated health of network based on health statues of multiple switches used in the system.

Deduced/Aggregated overall health of the system based on storage, servers and networking health.

  - `items.health.network` (string)
    Enum: "OK", "WARNING", "CRITICAL", "MISSING"

  - `items.health.overallHealth` (string)
    Enum: "OK", "WARNING", "CRITICAL", "MISSING"

  - `items.health.servers` (string)
    Enum: "OK", "WARNING", "CRITICAL", "MISSING"

  - `items.health.storage` (string)
    Enum: "OK", "WARNING", "CRITICAL", "MISSING"

  - `items.hypervisorClusters` (array)
    List of hypervisor clusters in the system with their software details.

  - `items.hypervisorClusters.hypervisorManagerAddress` (string)
    Address of Hypervisor Cluster Manager.

  - `items.hypervisorClusters.hypervisorManagerId` (string)
    Unique Identifier of Hypervisor Cluster Manager.

  - `items.hypervisorClusters.hypervisorManagerName` (string)
    Name of Hypervisor Cluster Manager.

  - `items.hypervisorClusters.id` (string)
    Unique Identifier of the Hypervisor Cluster, usually a UUID.

  - `items.hypervisorClusters.name` (string)
    Name of the Hypervisor Cluster

  - `items.hypervisorClusters.resourceUri` (string)
    Resource URI of the Hypervisor Cluster.

  - `items.location` (object)
    System Location Information.

  - `items.location.city` (string)
    City

  - `items.location.countryCode` (string)
    Country Code

  - `items.location.latitude` (string)
    Latitude coordinate of the system location

  - `items.location.longitude` (string)
    Longitude coordinate of the system location

  - `items.location.stateCode` (string)
    State Code

  - `items.location.zipCode` (string)
    Zip Code

  - `items.softwareInfo` (object)
    system software information.

  - `items.softwareInfo.currentUpdateStatus` (object)
    Details of the current software update status

  - `items.softwareInfo.currentUpdateStatus.catalogVersion` (string)
    Software Catalog version to which the update operation is in progress, if any.

  - `items.softwareInfo.currentUpdateStatus.parentTaskUri` (string)
    Uniform Resource Identifier (URI) of the parent software update task (asynchronous operation).

  - `items.softwareInfo.currentUpdateStatus.percentage` (integer)
    Percentage of the software update progress.

  - `items.softwareInfo.currentUpdateStatus.state` (string)
    Status of the software update:
  * UP_TO_DATE - Already up to date
  * UPDATE_AVAILABLE - One or more updates are available
  * PENDING - Waiting for update operation (precheck or update) to begin
  * PRECHECK_IN_PROGRESS - A software update precheck operation is in progress
  * PRECHECK_FAILED - The previous software update precheck operation has failed
  * PRECHECK_COMPLETE - The previous software update precheck operation has completed successfully
  * UPDATE_IN_PROGRESS - A software update operation is in progress
  * UPDATE_COMPLETE - The previous software update operation has completed successfully
  * UPDATE_FAILED - The previous software update operation has failed
  * NOT_READY - Not ready for update (e.g. when current version is not available, so no update paths exist)
    Enum: "UP_TO_DATE", "UPDATE_AVAILABLE", "PENDING", "PRECHECK_IN_PROGRESS", "PRECHECK_FAILED", "PRECHECK_COMPLETE", "UPDATE_IN_PROGRESS", "UPDATE_COMPLETE", "UPDATE_FAILED", "NOT_READY"

  - `items.softwareInfo.currentUpdateStatus.taskUri` (string)
    Uniform Resource Identifier (URI) of the software update task (asynchronous operation).

  - `items.softwareInfo.lastUpdatedOn` (string)
    Date on which the last software update was performed on this system.

  - `items.softwareInfo.precheckValidUntil` (string)
    If a software update precheck is completed recently, time until which that precheck is valid for software update to be initiated.

  - `items.stackType` (string)
    Stack Type of the system
    Enum: "DHCI", "SIMPLIVITY"

  - `items.state` (string)
    Current state of the system
    Enum: "OFFLINE", "ONLINE", "INITIALIZED", "UNINITIALIZED"

  - `items.storageSystem` (object)
    Storage Information of system.

  - `items.storageSystem.compressionRatio` (number)
    Compression ratio of the storage system.

  - `items.storageSystem.dedupeRatio` (number)
    Deduplication ratio of the storage system.

  - `items.storageSystem.groupLeaderName` (string)
    Name of the storage system array group leader.

  - `items.storageSystem.groupLeaderSerialNumber` (string)
    Serial number of the storage system array group leader.

  - `items.storageSystem.groupName` (string)
    Name of the storage system array group.

  - `items.storageSystem.groupState` (string)
    State of the storage system array group.

  - `items.storageSystem.id` (string)
    Storage system array Identifier, usually a UUID.

  - `items.storageSystem.name` (string)
    Name of the Storage system Array

  - `items.storageSystem.resourceUri` (string)
    Resource URI of the Storage system Array

  - `items.storageUsage` (object)
    Storage Usage Information of system.

  - `items.storageUsage.sizeInBytes` (number)
    Storage Capacity of the system

  - `items.storageUsage.usageInBytes` (number)
    Storage Usage of the system

  - `items.systemVms` (array)
    List of system virtual machine information.

  - `items.systemVms.name` (string)
    Name of the system Virtual Machine.

  - `items.systemVms.uuid` (string)
    Unique Identifier of the system virtual machine, usually a UUID.

  - `items.name` (string)
    A system specified name for the resource.

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


