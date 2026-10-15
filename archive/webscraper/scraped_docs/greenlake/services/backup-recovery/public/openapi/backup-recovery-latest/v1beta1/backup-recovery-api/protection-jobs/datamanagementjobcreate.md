---
title: "POST /backup-recovery/v1beta1/protection-jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobcreate.md"
scraped_at: "2026-06-07T06:14:16.414256+00:00Z"
---

# Create a new Protection Job.

Assign a Protection Policy to an asset.

Endpoint: POST /backup-recovery/v1beta1/protection-jobs
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `protectionPolicyId` (string, required)
    UUID string uniquely identifying the Protection Policy.

  - `assetInfo` (object, required)

  - `assetInfo.id` (string, required)
    The UUID of either the asset or asset group.

  - `assetInfo.type` (string)
    Type of asset. Supported types are virtualization/virtual-machine, virtualization/datastore, backup-recovery/virtual-machine-protection-group, virtualization/csp-machine-instance, virtualization/csp-volume, backup-recovery/csp-protection-group, backup-recovery/mssql-database-protection-group, backup-recovery/volume-protection-group, virtualization/csp-rds-instance, virtualization/csp-k8s-application

  - `effectiveFromDateTime` (string)
    Time in UTC at which the Protection Policy assignment will be effective from.

  - `overrides` (object)

  - `overrides.protections` (array)
    An array of protection objectives.

  - `overrides.protections.id` (string, required)

  - `overrides.protections.protectionStoreId` (string)
    UUID string uniquely identifying the protection store.
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `overrides.protections.schedules` (array)
    Array of schedules attributes.

  - `overrides.protections.schedules.scheduleId` (integer, required)
    Client provided id for this schedule.

  - `overrides.protections.schedules.backupGranularity` (string)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `overrides.protections.schedules.consistency` (string)
    Specifies whether to create crash consistent or application consistent snapshot.
CrashConsistentOnFailure: If an application consistent snapshot fails for any reason,
with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `overrides.protections.schedules.createSnapshotOnFailure` (boolean)
    Specifies if the snapshot can be crash consistent in case of script execution failure.

  - `overrides.protections.schedules.expireAfter` (object)
    Copy expiration attribute, which specifies the expiration for the artifacts created.

  - `overrides.protections.schedules.expireAfter.unit` (string)
    Accepted units
    Enum: "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS"

  - `overrides.protections.schedules.expireAfter.value` (integer)
    Expiration value

  - `overrides.protections.schedules.lockFor` (object)
    Retention attribute, which specifies the retention period for the artifacts created. Artifacts are locked for deletion for the specified period of time.

  - `overrides.protections.schedules.lockFor.value` (integer)
    Retention value

  - `overrides.protections.schedules.namePattern` (object)
    Format for the snapshot names

  - `overrides.protections.schedules.namePattern.format` (string)
    Format for the name with combination of the tokens and alphabets and numbers. "snapprefix-{SourceAssetName}-snapsuffix-{DateFormat}". Total length will be 255 characters. Possible tokens: {SourceAssetName} - Name of the source asset (DB or VM) {DateFormat} - User friendly date and time of artifact creation
    Example: "Test_{SourceAssetName}_Copy_{DateFormat}"

  - `overrides.protections.schedules.postScriptInfo` (object)

  - `overrides.protections.schedules.postScriptInfo.params` (string, required)
    Parameters required to run the post-script file.

  - `overrides.protections.schedules.preScriptInfo` (object)

  - `overrides.protections.schedules.preScriptInfo.params` (string, required)
    Parameters required to run the pre-script file.

  - `overrides.protections.schedules.vmwareOptions` (object)

  - `overrides.protections.schedules.vmwareOptions.includeRdmDisks` (boolean)
    Option to include RDM disks of VMs for protection.
Option needed only for datastore protection.
By default RDM disks of VMs are not included for protection
when protection is applied at datastore level.
Only RDM disks of VMs completely residing in the datastore
disks are included protection.
    Example: true

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


