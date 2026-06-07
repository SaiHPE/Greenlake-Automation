---
title: "Backup and Recovery API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api.md"
scraped_at: "2026-06-07T05:46:28.450499+00:00Z"
---

# Backup and Recovery API

Backup and Recovery API

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

The Data Service Cloud Console API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Backup and Recovery API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/@v1beta1/backup-recovery-api.yaml)

## Protection Store Gateway

Protection Store Gateway APIs

### Returns the resource requirements that would be needed for a Protection Store Gateway.

 - [POST /backup-recovery/v1beta1/protection-store-gateway-sizer](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaysize.md): Returns the resource requirements that would be needed for a Protection Store Gateway. This API doesn't create the Protection Store Gateway. To create the Protection Store Gateway a call to POST /protection-store-gateways should be made.

### Get a list of the Protection Store Gateways that are registered with DSCC

 - [GET /backup-recovery/v1beta1/protection-store-gateways](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayslist.md): Gets the list of available Protection Store Gateways

### Create a new Protection Store Gateway within DSCC

 - [POST /backup-recovery/v1beta1/protection-store-gateways](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaycreate.md): Create a Protection Store Gateway

### Deletes a Protection Store Gateway within DSCC

 - [DELETE /backup-recovery/v1beta1/protection-store-gateways/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaydelete.md): Delete the Protection Store Gateway

### Get details of a Protection Store Gateway within DSCC

 - [GET /backup-recovery/v1beta1/protection-store-gateways/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaygetbyid.md): Get details of a Protection Store Gateway

### Modify the configuration of a Protection Store Gateway

 - [PATCH /backup-recovery/v1beta1/protection-store-gateways/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayupdate.md): Update a Protection Store Gateway.

### Gets the credentials of a Protection Store Gateway console user

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/consoleUser](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaygetconsoleuser.md): Get credentials of a Protection Store Gateway console user

### Creates a network interface on the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/createNic](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayniccreate.md): Create network interface on the Protection Store Gateway

### Deletes a network interface on the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/deleteNic](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaynicdelete.md): Delete the network interface on the Protection Store Gateway

### Generates a support bundle

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/generate-support-bundle](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaygeneratesupportbundle.md): Generate a support bundle

### Ping from the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/ping](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayping.md): Ping from the Protection Store Gateway

### Powers on the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/power-on](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaypoweron.md): Power on the Protection Store Gateway

### Recover a Protection Store Gateway within DSCC

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/recover](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayrecover.md): Recover a Protection Store Gateway

### Reconfigures the CPU, memory and storage requirements of the Protection Store Gateway.

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaystorage.md): Reconfigure the CPU, memory and storage requirements of the Protection Store Gateway.

### Restarts the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/restart-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayrestartguestos.md): Restart the Protection Store Gateway

### Enables remote support on the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/set-remote-support](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaysetremotesupport.md): Enable remote support on the Protection Store Gateway

### Shuts down the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/shutdown-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayshutdownguestos.md): Shutdown the Protection Store Gateway

### Returns the resource requirements that would be needed to resize an existing Protection Store Gateway.

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/sizer](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaypsgsize.md): Returns the resource requirements that would be needed to resize an existing Protection Store Gateway. This API doesn't perform any modifications to the Protection Store Gateway. To implement the modifications a call to POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize should be made.

### Traceroute from the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/traceroute](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaytraceroute.md): Traceroute from the Protection Store Gateway

### Modifies a network interface on the Protection Store Gateway

 - [POST /backup-recovery/v1beta1/protection-store-gateways/{id}/updateNic](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaynicupdate.md): Modify the network interface on the Protection Store Gateway

## StoreOnce

StoreOnce APIs

### Get the list of available StoreOnces.

 - [GET /backup-recovery/v1beta1/storeonces](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeonceslist.md): Get the list of all available and registered StoreOnce machines.

### Create a StoreOnce.

 - [POST /backup-recovery/v1beta1/storeonces](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeoncecreate.md): Register and create a new StoreOnce machine.

### Delete the StoreOnce.

 - [DELETE /backup-recovery/v1beta1/storeonces/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeoncedelete.md): Unregister and delete the StoreOnce.

### Get details of a StoreOnce.

 - [GET /backup-recovery/v1beta1/storeonces/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeoncegetbyid.md): Get all the details and information of registered StoreOnce.

### Update the StoreOnce.

 - [PATCH /backup-recovery/v1beta1/storeonces/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeonceupdate.md): Update already registered StoreOnce.

### Refresh the StoreOnce.

 - [POST /backup-recovery/v1beta1/storeonces/{id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeoncereferesh.md): Retrieve and update the latest information about the StoreOnce.

## application-hosts

The Application Hosts API allows the registration and management of Application Hosts.

### Get all registered Application Hosts.

 - [GET /backup-recovery/v1beta1/application-hosts](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhostlist.md): List all the registered Application Hosts.

### Register a new Application Host.

 - [POST /backup-recovery/v1beta1/application-hosts](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhostcreate.md): Register the Application Host for data management.

### Unregister an Application Host.

 - [DELETE /backup-recovery/v1beta1/application-hosts/{host-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/unregisterapplicationhost.md): Unregister an Application Host.

### Get an Application Host resource identified by {host-id}.

 - [GET /backup-recovery/v1beta1/application-hosts/{host-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhost.md): Get detailed information for a registered Application Host qualified by host-id.

### Update an Application Host.

 - [PATCH /backup-recovery/v1beta1/application-hosts/{host-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhostupdate.md): Update attributes for an Application Host.

### Refresh an Application Host and its sub-resources.

 - [POST /backup-recovery/v1beta1/application-hosts/{host-id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/refreshapplicationhost.md): Refresh an Application Host and its sub-resources.

## data-orchestrators

APIs for managing Data Orchestrator operations.

### Get a list of the Data Orchestrators that are registered with DSCC

 - [GET /backup-recovery/v1beta1/data-orchestrators](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorlist.md): This API returns a list of all the Data Orchestrators that are registered with the DSCC 
customer account.

### Register a new Data Orchestrator with DSCC

 - [POST /backup-recovery/v1beta1/data-orchestrators](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorcreate.md): This API is used to register a new Data Orchestrator with the DSCC customer account.

To register the Data Orchestrator, the unique Activation Code that 
is displayed on the Data Orchestrator must be provided.

### Unregister the Data Orchestrator from DSCC

 - [DELETE /backup-recovery/v1beta1/data-orchestrators/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratordelete.md): This API will unregister the Data Orchestrator from the DSCC customer account.

The unregistered Data Orchestrator will disable any scheduled jobs orchestrated by
the Data Orchestrator.

### Get details of a Data Orchestrator registered with DSCC

 - [GET /backup-recovery/v1beta1/data-orchestrators/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorlistbyid.md): This API returns details of the Data Orchestrator specified by id.

### Modify the configuration of a Data Orchestrator

 - [PATCH /backup-recovery/v1beta1/data-orchestrators/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratormodify.md): This API allows the configuration of the Data Orchestrator to be modified.

This configuration options include:
* Network
* Date & Time

### Generate a new support-bundle

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/generate-support-bundle](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/supportbundlecreate.md): Generate a new support-bundle.

### Generate a time-based one time passcode (TOTP) for Data Orchestrator access

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/generate-totp](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/otpcreate.md): Generate a time-based one time passcode (TOTP) for Data Orchestrator access.

### Recover a Data Orchestrator identified by id

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/recover](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorrecover.md): Recover a Data Orchestrator identified by id.

### Restart a Data Orchestrator

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/restart-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorreboot.md): This API will stop and restart the Data Orchestrator.

### Modify InfoSight Configuration for a Data Orchestrator

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/set-remote-support](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorinfosightconfigmodify.md): Modify InfoSight Configuration for a Data Orchestrator.

### Shutdown a Data Orchestrator

 - [POST /backup-recovery/v1beta1/data-orchestrators/{id}/shutdown-guest-os](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorshutdown.md): This API will power off the Data Orchestrator to allow for maintenance of the hypervisor.

## datastores

The datastores API allows the data management operations on datastores.

### Restore a datastore from snapshot or a backup.

 - [POST /backup-recovery/v1beta1/datastores/{id}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastores/datastorerestorefromcopy.md): Restores a datastore from selected snapshot or backup.

## mssql-database-backups

The MSSQL database backups API allows the creation and management of MSSQL database backups.

### Get information about all MSSQL database backups.

 - [GET /backup-recovery/v1beta1/mssql-databases/{db-id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-backups/mssqldatabasebackuplist.md): Get information about all MSSQL database backups.

### Delete an MSSQL database backup.

 - [DELETE /backup-recovery/v1beta1/mssql-databases/{db-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-backups/deletemssqldatabasebackup.md): Remove an MSSQL database backup.

### Get details of a MSSQL database backup.

 - [GET /backup-recovery/v1beta1/mssql-databases/{db-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-backups/mssqldatabasebackup.md): Get detailed information for a MSSQL database backup qualified by backup-id.

### Update a MSSQL database backup.

 - [PATCH /backup-recovery/v1beta1/mssql-databases/{db-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-backups/mssqldatabasebackupupdate.md): Update attributes for a MSSQL database backup.

## mssql-database-protection-groups

The MSSQL database Protection Groups API allows management of MSSQL database Protection Groups.

### Get all MSSQL database protection groups.

 - [GET /backup-recovery/v1beta1/mssql-database-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongrouplist.md): List all the MSSQL database protection groups.

### Create a new MSSQL Database Protection Group.

 - [POST /backup-recovery/v1beta1/mssql-database-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroupcreate.md): Create an MSSQL Database Protection Group for data management.

### Remove an MSSQL database protection group.

 - [DELETE /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/removemssqldatabaseprotectiongroup.md): Remove an MSSQL database protection group.

### Get an MSSQL database protection group resource identified by {group-id}.

 - [GET /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroup.md): Get detailed information for an MSSQL database protection group qualified by group-id.

### Update an MSSQL database protection group.

 - [PATCH /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroupupdate.md): Update attributes for an MSSQL database protection group.

## mssql-database-snapshots

The MSSQL database snapshots API allows the creation and management of MSSQL database snapshots.

### Get information about all MSSQL database snapshots.

 - [GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-snapshots/mssqldatabasesnapshotlist.md): Get information about all MSSQL database snapshots.

### Delete an MSSQL database snapshot.

 - [DELETE /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-snapshots/deletemssqldatabasesnapshot.md): Remove an MSSQL database snapshot.

### Get details of a MSSQL database snapshot.

 - [GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-snapshots/mssqldatabasesnapshot.md): Get detailed information for a MSSQL database snapshot qualified by snapshot-id.

### Update a MSSQL database snapshot.

 - [PATCH /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-snapshots/mssqldatabasesnapshotupdate.md): Update attributes for a MSSQL database snapshot.

## mssql-databases

The MSSQL Databases API allows management of MSSQL databases.

### Get all discovered MSSQL databases.

 - [GET /backup-recovery/v1beta1/mssql-databases](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-databases/mssqldatabaselist.md): List all the discovered MSSQL databases.

### Get an MSSQL database resource identified by {db-id}.

 - [GET /backup-recovery/v1beta1/mssql-databases/{db-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-databases/mssqldatabase.md): Get detailed information for a discovered MSSQL database qualified by db-id.

### Refresh an MSSQL database and its sub-resources.

 - [POST /backup-recovery/v1beta1/mssql-databases/{db-id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-databases/refreshmssqldatabase.md): Refresh an MSSQL database and its sub-resources.

### Restore an MSSQL database from snapshot or backup.

 - [POST /backup-recovery/v1beta1/mssql-databases/{db-id}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-databases/mssqldatabaserestore.md): Restores a virtual machine from selected snapshot.

## mssql-instances

The MSSQL Instances API allows management of MSSQL instances.

### Get all discovered MSSQL instances.

 - [GET /backup-recovery/v1beta1/mssql-instances](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-instances/mssqlinstancelist.md): List all the discovered MSSQL instances.

### Get an MSSQL instance resource identified by {instance-id}.

 - [GET /backup-recovery/v1beta1/mssql-instances/{instance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-instances/mssqlinstance.md): Get detailed information for a discovered MSSQL instance qualified by instance-id.

### Update an MSSQL instance.

 - [PATCH /backup-recovery/v1beta1/mssql-instances/{instance-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-instances/mssqlinstanceupdate.md): Update attributes of an MSSQL instance.

### Refresh an MSSQL Instance.

 - [POST /backup-recovery/v1beta1/mssql-instances/{instance-id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-instances/refreshmssqlinstance.md): Refresh the specified mssql-instance.

## protection-jobs

The Protection Jobs API allows the creation and management of Protection Jobs.

### Get all the Protection Jobs.

 - [GET /backup-recovery/v1beta1/protection-jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobslist.md): List all the Protection Jobs.

### Create a new Protection Job.

 - [POST /backup-recovery/v1beta1/protection-jobs](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobcreate.md): Assign a Protection Policy to an asset.

### Delete a Protection Job.

 - [DELETE /backup-recovery/v1beta1/protection-jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/deletedatamanagementjob.md): Delete the specified Protection Job.

### Get a Protection Job identified by {id}.

 - [GET /backup-recovery/v1beta1/protection-jobs/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobdetail.md): Get detailed information of a Protection Job qualified by id.

### Resume a Protection Job.

 - [POST /backup-recovery/v1beta1/protection-jobs/{id}/resume](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobresume.md): Resume a Protection Job.

### Run a Protection Job now.

 - [POST /backup-recovery/v1beta1/protection-jobs/{id}/run](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobrun.md): Run a Protection Job now.

### Suspend a Protection Job.

 - [POST /backup-recovery/v1beta1/protection-jobs/{id}/suspend](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobsuspend.md): Suspend a Protection Job.

## protection-policies

The Protection Policies API allows the creation and management of Protection Policies.

### Get all protection policies.

 - [GET /backup-recovery/v1beta1/protection-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/datamanagementtemplateslist.md): List all the protection policies.

### Create a new Protection Policy.

 - [POST /backup-recovery/v1beta1/protection-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/datamanagementtemplatecreate.md): Create a new Protection Policy.

### Delete a Protection Policy.

 - [DELETE /backup-recovery/v1beta1/protection-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/deletedatamanagementtemplate.md): Delete the Protection Policy.

### Get a Protection Policy identified by {id}.

 - [GET /backup-recovery/v1beta1/protection-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/datamanagementtemplatedetail.md): Get detailed information of a Protection Policy qualified by id.

### Update an assigned Protection Policy.

 - [PATCH /backup-recovery/v1beta1/protection-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/datamanagementtemplateupdate.md): Update an assigned Protection Policy for data protection.

### Replace a Protection Policy completely.

 - [PUT /backup-recovery/v1beta1/protection-policies/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-policies/datamanagementtemplatereplace.md): Update a Protection Policy for data protection before assignment.

## protection-stores

This API allows the creation and management of Protection Stores that represents the backup target for the copies.

### Get details of all the Protection Stores

 - [GET /backup-recovery/v1beta1/protection-stores](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstorelist.md): List all the Protection Stores.

### Create a Protection Store

 - [POST /backup-recovery/v1beta1/protection-stores](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstorecreate.md): Create a Protection Store.

### Delete a Protection Store

 - [DELETE /backup-recovery/v1beta1/protection-stores/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstoredelete.md): Delete a Protection Store.

### Get the details of the Protection Store specified by id

 - [GET /backup-recovery/v1beta1/protection-stores/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstorebyid.md): Details of a Protection Store.

### Modify a Protection Store

 - [PATCH /backup-recovery/v1beta1/protection-stores/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstoreedit.md): Modify a Protection Store.

### Reattach a Cloud Protection Store

 - [POST /backup-recovery/v1beta1/protection-stores/{id}/reattach](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/cloudprotectionstorereattach.md): Reattach a Cloud Protection Store.

## virtual-machine-protection-groups

The virtual machine Protection Groups API allows the creation and management of  virtual machine Protection Groups (Group of Virtual Machines, Datastores or Folder for Protection).

### Get all  virtual machine Protection Groups.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongrouplist.md): List all virtual machine Protection Groups.

### Create a new virtual machine Protection Group.

 - [POST /backup-recovery/v1beta1/virtual-machine-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroupcreate.md): Create the virtual machine Protection Group for data management.

### Remove a virtual machine Protection Group.

 - [DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroupdelete.md): Remove a virtual machine Protection Group.

### Get a virtual machine Protection Group resource.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroup.md): Get detailed information for a registered virtual machine Protection Group qualified by id.

### Update a virtual machine Protection Group.

 - [PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroupupdate.md): Update attributes for a virtual machine Protection Group.

### Refresh a virtual machine Protection Group.

 - [POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongrouprefresh.md): Refresh a virtual machine Protection Group.

### Restore a virtual machine Protection Group from recovery points.

 - [POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgrestore.md): Restore a virtual machine Protection Group from recovery points.

### Restore pre-check of a virtual machine Protection Group from recovery points.

 - [POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore-pre-check](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgrestoreprechecklist.md): Validations and recovery point info of a virtual machine Protection Group.

### Get information about all virtual machine protection groups backups.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgbackuplist.md): Get information about all Virtual Machine protection group backups.

### Delete a virtual machine protection group backup.

 - [DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/deletevmpgbackup.md): Remove a virtual machine protection group backup.

### Get details of a virtual machine protection group backup.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgbackup.md): Get detailed information for a virtual machine protection group backup qualified by backup-id.

### Update a virtual machine protection groups backup.

 - [PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgbackupupdate.md): Update attributes for a virtual machine protection groups backup.

### Get information about all virtual machine protection groups snapshots.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgsnapshotlist.md): Get information about all virtual machine protection groups snapshots.

### Delete a virtual machine protection group snapshot.

 - [DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/deletevmpgsnapshot.md): Delete a vm-protection-group snapshot.

### Get details of a virtual machine protection group snapshot.

 - [GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgsnapshot.md): Get detailed information for a virtual-machine-protection-group snapshot qualified by snapshot-id.

### Update a virtual machine protection group snapshot.

 - [PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgsnapshotupdate.md): Update attributes of a virtual machine protection group snapshot.

## virtual-machines

The virtual machines API allows the data management operations on virtual machines.

### Restore a virtual machine from snapshot or backup.

 - [POST /backup-recovery/v1beta1/virtual-machines/{id}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machines/virtualmachinerestore.md): Restores a virtual machine from the selected snapshot or backup.

### Restore one or more disks of a virtual machine from snapshot or backup.

 - [POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-disks](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machines/virtualmachinedisksrestore.md): Restore one or more disks of a virtual machine.

### Restore files and folders of a virtual machine.

 - [POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-files](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machines/virtualmachinefilerestore.md): Restore one or more files and folders of a virtual machine from snapshot or backup.

## volume-protection-groups

The Volume Protection Groups API allows the creation and management of Volume Protection Groups (Group of Volumes for Protection).

### Get all Volume Protection Groups.

 - [GET /backup-recovery/v1beta1/volume-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongrouplist.md): List all Volume Protection Groups.

### Create a new Volume Protection Group.

 - [POST /backup-recovery/v1beta1/volume-protection-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongroupcreate.md): Create the Volume Protection Group for data management.

### Remove a Volume Protection Group.

 - [DELETE /backup-recovery/v1beta1/volume-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/removevolumeprotectiongroup.md): Remove a Volume Protection Group.

### Get a Volume Protection Group resource identified by {id}.

 - [GET /backup-recovery/v1beta1/volume-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongroup.md): Get detailed information for a registered Volume Protection Group qualified by id.

### Update a Volume Protection Group.

 - [PATCH /backup-recovery/v1beta1/volume-protection-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongroupupdate.md): Update attributes for a Volume Protection Group. Edit is not available on a native group.

### Refreshes a Volume Protection Group.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/refresh](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongrouprefresh.md): Refreshes a Volume Protection Group and the corresponding snapshots and backups.

### Restores a Volume Protection Group from snapshot or backup.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongrouprestore.md): Restores a Volume Protection Group from selected snapshot or backup.

## datastore-backups

### Get information about all datastore backups.

 - [GET /backup-recovery/v1beta1/datastores/{id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-backups/datastorebackuplist.md): Get information about all datastore backups.

### Delete a datastore backup.

 - [DELETE /backup-recovery/v1beta1/datastores/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-backups/deletedatastorebackup.md): Remove a datastore backup.

### Get details of a datastore backup.

 - [GET /backup-recovery/v1beta1/datastores/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-backups/datastorebackup.md): Get detailed information for a datastore backup qualified by backup-id.

### Update a datastore backup.

 - [PATCH /backup-recovery/v1beta1/datastores/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-backups/datastorebackupupdate.md): Update attributes for a datastore backup.

## datastore-snapshots

### Get information about all datastore snapshots.

 - [GET /backup-recovery/v1beta1/datastores/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-snapshots/datastoresnapshotlist.md): Get information about all datastore snapshots.

### Delete a datastore snapshot.

 - [DELETE /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-snapshots/deletedatastoresnapshot.md): Delete a datastore snapshot.

### Get details of a datastore snapshot.

 - [GET /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-snapshots/datastoresnapshot.md): Get detailed information for a datastore snapshot qualified by snapshot-id.

### Update a datastore snapshot.

 - [PATCH /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-snapshots/datastoresnapshotupdate.md): Update attributes for a datastore snapshot.

## virtual-machine-backups

### Get information about all virtual machine backups.

 - [GET /backup-recovery/v1beta1/virtual-machines/{id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-backups/virtualmachinebackuplist.md): Get information about all virtual machine backups.

### Delete a virtual machine backup.

 - [DELETE /backup-recovery/v1beta1/virtual-machines/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-backups/deletevirtualmachinebackup.md): Remove a virtual machine backup.

### Get details of a virtual machine backup.

 - [GET /backup-recovery/v1beta1/virtual-machines/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-backups/virtualmachinebackup.md): Get detailed information for a virtual machine backup qualified by backup-id.

### Update a virtual machine backup.

 - [PATCH /backup-recovery/v1beta1/virtual-machines/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-backups/virtualmachinebackupupdate.md): Update attributes for a virtual machine backup.

## virtual-machine-snapshots

### Get information about all virtual machine snapshots.

 - [GET /backup-recovery/v1beta1/virtual-machines/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-snapshots/virtualmachinesnapshotlist.md): Get information about all virtual machine snapshots.

### Delete a virtual machine snapshot.

 - [DELETE /backup-recovery/v1beta1/virtual-machines/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-snapshots/deletevirtualmachinesnapshot.md): Remove a virtual machine snapshot.

### Get details of a virtual machine snapshot.

 - [GET /backup-recovery/v1beta1/virtual-machines/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-snapshots/virtualmachinesnapshot.md): Get detailed information for a virtual machine snapshot qualified by snapshot-id.

### Update a virtual machine snapshot.

 - [PATCH /backup-recovery/v1beta1/virtual-machines/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-snapshots/virtualmachinesnapshotupdate.md): Update attributes for a virtual machine snapshot.

## volume-protection-group-backups

### Get all Volume Protection Group backups.

 - [GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackuplist.md): List all Volume Protection Group backups.

### Create a backup copy of a Volume Protection Group.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/backups](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackupcreate.md): Create a backup copy of a Volume Protection Group.

### Remove a Volume Protection Group backup.

 - [DELETE /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/removevpgbackup.md): Remove a Volume Protection Group backup.

### Get a Volume Protection Group backup identified by {id}.

 - [GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackup.md): Get detailed information for a registered Volume Protection Group backup qualified by id.

### Update a Volume Protection Group backup.

 - [PATCH /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackupupdate.md): Update attributes for a Volume Protection Group backup. Edit is not available on a native group.

### Attach a Volume Protection Group backup.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}/attach](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackupattach.md): Attach a Volume Protection Group backup.

### Detach a Volume Protection Group backup.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}/detach](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackupdetach.md): Detach a Volume Protection Group backup.

## volume-protection-group-snapshots

### Get all Volume Protection Group snapshots.

 - [GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshotlist.md): List all Volume Protection Group snapshots.

### Create a snapshot copy of a Volume Protection Group.

 - [POST /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshotcreate.md): Create a snapshot copy of a Volume Protection Group.

### Remove a Volume Protection Group snapshot.

 - [DELETE /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/removevpgsnapshot.md): Remove a Volume Protection Group snapshot.

### Get a Volume Protection Group snapshot identified by {id}.

 - [GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshot.md): Get detailed information for a registered Volume Protection Group snapshot qualified by id.

### Update a Volume Protection Group snapshot.

 - [PATCH /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshotupdate.md): Update attributes for a Volume Protection Group snapshot. Edit is not available on a native group.

