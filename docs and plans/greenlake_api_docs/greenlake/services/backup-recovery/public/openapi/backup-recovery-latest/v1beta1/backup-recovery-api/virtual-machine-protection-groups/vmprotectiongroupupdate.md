---
title: "PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroupupdate.md"
scraped_at: "2026-06-07T06:14:18.081430+00:00Z"
---

# Update a virtual machine Protection Group.

Update attributes for a virtual machine Protection Group.

Endpoint: PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/merge-patch+json):

  - `assets` (array)
    Captures the list of assets that would be part of the protection group.

  - `assets.displayName` (string)
    Name provided for the asset.

  - `assets.id` (string)
    Asset identifier.

  - `assets.name` (string)
    Name provided for the asset.

  - `assets.type` (string)
    type of the asset.

  - `description` (string)
    A brief description of the Protection Group.

  - `dynamicMemberFilter` (object)

  - `dynamicMemberFilter.members` (array)
    Tags associated with the Protection Group.

  - `dynamicMemberFilter.members.name` (string)
    Name of the Tag.
    Example: "Tag name"

  - `dynamicMemberFilter.members.resourceUri` (string)
    Resource uri of the Tag.
    Example: "/virtualization/v1beta1/hypervisor-managers/17f83a4d-bfac-4a92-a009-ac3167fdd83b/tags/651de0d6-9b15-5dd0-b466-1fd4da410200"

  - `dynamicMemberFilter.members.type` (string)
    Type of the Tag.

  - `name` (string)
    A user-friendly name to identify Virtual Machine protection group.

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


