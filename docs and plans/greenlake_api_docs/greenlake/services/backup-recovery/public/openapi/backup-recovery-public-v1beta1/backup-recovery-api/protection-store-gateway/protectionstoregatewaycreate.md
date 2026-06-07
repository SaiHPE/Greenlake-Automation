---
title: "POST /backup-recovery/v1beta1/protection-store-gateways"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaycreate.md"
scraped_at: "2026-06-07T06:13:59.427290+00:00Z"
---

# Create a new Protection Store Gateway within DSCC

Create a Protection Store Gateway

Endpoint: POST /backup-recovery/v1beta1/protection-store-gateways
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `hypervisorManagerId` (string, required)
    Unique identifier, UUID.
    Example: "aa1974ec-3b28-406f-8d84-85528d590a6b"

  - `name` (string, required)
    The name of the Protection Store Gateway
    Example: "EG-172.31.57.71"

  - `vmConfig` (object, required)
    Example: {"datastoreIds":["70968004-886c-582e-b09a-c98396d0db68","098c18ff-ae3d-55a7-8967-00869c1ac71c"],"hostId":"234f54ab-e93c-5bc7-9daa-3dcd93fc0ae0","maxInCloudDailyProtectedDataInTiB":90,"maxInCloudRetentionDays":90,"maxOnPremDailyProtectedDataInTiB":5,"maxOnPremRetentionDays":5,"network":{"dns":[{"networkAddress":"172.31.56.9"},{"networkAddress":"172.31.56.10"},{"networkAddress":"172.31.35.101"}],"gateway":"172.31.63.254","name":"dvportgroup-30","networkAddress":"172.31.57.71","networkType":"STATIC","subnetMask":"255.255.248.0"}}

  - `vmConfig.clusterId` (string)
    Id of the cluster. Only required if host or resource pool is not given

  - `vmConfig.contentLibraryId` (string)
    Id of the datastore for the content library

  - `vmConfig.datastoreIds` (array)
    Example: ["70968004-886c-582e-b09a-c98396d0db68","098c18ff-ae3d-55a7-8967-00869c1ac71c"]

  - `vmConfig.folderId` (string)
    Id of the folder

  - `vmConfig.hostId` (string)
    Id of the Host. Only required if cluster or resource pool is not given
    Example: "234f54ab-e93c-5bc7-9daa-3dcd93fc0ae0"

  - `vmConfig.network` (object)
    Example: {"dns":[{"networkAddress":"172.31.56.9"},{"networkAddress":"172.31.56.10"},{"networkAddress":"172.31.35.101"}],"gateway":"172.31.63.254","name":"dvportgroup-30","networkAddress":"172.31.57.71","networkType":"STATIC","subnetMask":"255.255.248.0"}

  - `vmConfig.network.dns` (array)
    DNS servers of the appliance
    Example: [{"networkAddress":"172.31.56.9"},{"networkAddress":"172.31.56.10"},{"networkAddress":"172.31.35.101"}]

  - `vmConfig.network.dns.networkAddress` (string)
    DNS server configured on the appliance.

  - `vmConfig.network.gateway` (string)
    Gateway associated with the network interface.
    Example: "172.31.63.254"

  - `vmConfig.network.name` (string)
    Name of Network
    Example: "dvportgroup-30"

  - `vmConfig.network.networkAddress` (string)
    An IP address or FQDN address when static
    Example: "172.31.57.71"

  - `vmConfig.network.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `vmConfig.network.subnetMask` (string)
    Subnet mask.
    Example: "255.255.248.0"

  - `vmConfig.override` (object)
    Override automatic VM resource configuration with a fixed configuration.

  - `vmConfig.override.cpu` (number)
    Number of vCPU cores.
    Example: 8

  - `vmConfig.override.ramInGiB` (number)
    Amount of RAM in GiB.
    Example: 24

  - `vmConfig.override.storageInTiB` (number)
    Total storage capacity (TiB) of the Protection Store Gateway.
    Example: 2

  - `vmConfig.resourcePoolId` (string)
    Id of the resource pool. Only required if cluster or host is not given

  - `vmConfig.maxInCloudDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the Cloud Protection Stores.
    Example: 90

  - `vmConfig.maxInCloudRetentionDays` (number)
    The maximum retention period for cloud backups in days.
    Example: 90

  - `vmConfig.maxOnPremDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the On-Prem Protection Store.
    Example: 5

  - `vmConfig.maxOnPremRetentionDays` (number)
    The maximum retention period for local backups in days.
    Example: 5

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

## Response 403 fields (application/json):

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

## Response 412 fields (application/json):

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


