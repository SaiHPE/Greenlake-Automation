---
title: "POST /virtualization/v1beta1/virtual-machines"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtual-machines/hcideployvm.md"
scraped_at: "2026-06-07T06:16:32.936243+00:00Z"
---

# Deploy virtual machine

Deploys one or more virtual machines in HCI environment with specified template and storage provisioning policy.

Endpoint: POST /virtualization/v1beta1/virtual-machines
Version: 1.2.0
Security: bearer

## Request fields (application/json):

  - `vmConfig` (object, required)
    Defines the virtual machine configurations

  - `vmConfig.name` (string, required)
    Name of the virtual machine to be deployed

  - `vmConfig.acceptEula` (boolean, required)
    Accept EULA by default or not

  - `vmConfig.annotation` (string)
    The description of the image

  - `vmConfig.locale` (string)
    Locale to use for parsing OVF descriptor

  - `vmConfig.numberOfVms` (integer)
    Number of virtual machines to be created.

  - `vmConfig.powerOn` (boolean)
    Power on/off the virtual machine

  - `vmConfig.propertyConfig` (array)
    Properties which can be set to a virtual machine during deployment

  - `vmConfig.propertyConfig.key` (string)
    Name of the property to be set to the virtual machine

  - `vmConfig.propertyConfig.value` (string)
    Value of the property to be set to the virtual machine

  - `storageConfig` (object, required)
    Specifies the storage configurations for a virtual machine

  - `storageConfig.defaultDatastoreId` (string, required)
    The UUID of the hypervisor datastore where the virtual machine is to be deployed

  - `storageConfig.provisioningType` (string)
    Specifies whether datastore is THIN or THICK to provision the virtual machine
    Enum: "THIN", "THICK"

  - `destination` (object)
    Specifies where to deploy the virtual machine

  - `destination.clusterId` (string)
    The UUID of the hypervisor cluster where the virtual machine can be deployed

  - `destination.folderId` (string)
    The UUID of the hypervisor folder where the virtual machine can be deployed

  - `destination.hostId` (string)
    The UUID of the hypervisor host where the virtual machine can be deployed

  - `destination.resourcePoolId` (string)
    The UUID of the hypervisor resource pool where the virtual machine can be deployed

  - `imageSource` (object)
    Specifies the hypervisor image information using which the virtual machine is deployed

  - `imageSource.imageId` (string)
    The UUID of the hypervisor image using which a virtual machine is deployed

  - `imageSource.imageName` (string)
    The name of the hypervisor image using which a virtual machine is deployed

  - `imageSource.imageSourceType` (string)
    The source of the image where it was hosted
    Enum: "HYPERVISOR_IMAGE_LIBRARY"

  - `networkConfig` (object)
    Specifies name and the target network to use for deployment

  - `networkConfig.ipAllocationPolicy` (string)
    Specifies whether IP addresses are allocated by DHCP or static address
    Enum: "DHCP_POLICY", "FIXED_POLICY"

  - `networkConfig.networkMapping` (array)
    Specifies name and the target network to be used for deployment

  - `networkConfig.networkMapping.name` (string)
    Identifier for the network mapping

  - `networkConfig.networkMapping.network` (string)
    Target network to be used for deployment

  - `vmPolicy` (array)
    Specifies the policies which can be attached to the virtual machine

  - `vmPolicy.id` (string)
    The UUID of the policy

  - `vmPolicy.type` (string)
    Type of the policy which needs to be attached to the virtual machine
    Enum: "VM_PROTECTION_POLICY", "VM_PROVISIONING_POLICY"

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


