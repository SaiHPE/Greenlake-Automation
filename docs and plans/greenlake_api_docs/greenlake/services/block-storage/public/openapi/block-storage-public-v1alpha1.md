---
title: "HPE Greenlake For Block Storage REST APIs."
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1.md"
scraped_at: "2026-06-07T05:46:29.013638+00:00Z"
---

# HPE Greenlake For Block Storage REST APIs.

HPE Greenlake For Block Storage REST APIs.

Version: 1.0.0
License: HPE End User License Agreement

## Servers

```
https://eu1.data.cloud.hpe.com
```

```
https://us1.data.cloud.hpe.com
```

```
https://jp1.data.cloud.hpe.com
```

## Security

### bearer

Storage Fleet API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE Greenlake For Block Storage REST APIs.](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/index.yaml)

## host-initiator-groups

The Host service API allows the management of Host Group

### Get the list of host groups

 - [GET /block-storage/v1alpha1/host-initiator-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgrouplist.md): Get the list of host groups

### Create a host group

 - [POST /block-storage/v1alpha1/host-initiator-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupcreate.md): Create a host group with hosts having same protocol initiators

### Delete a host group by {hostGroupId}

 - [DELETE /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupdelete.md): Delete a host group by {hostGroupId}

### Get the host group details by {hostGroupId}

 - [GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupgetbyid.md): Get the host group details by {hostGroupId}

### Update host group by {hostGroupId}

 - [PUT /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupupdatebyid.md): Update host group details by {hostGroupId}. Hostgroup can be updated with hosts containing same protocol initiators

### Get details of a host group identified by {hostGroupId} across its associated systems

 - [GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}/mapped-devices](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupmappeddevice.md): Get details of a host group identified by {hostGroupId} across its associated systems

## host-initiators

The Host service API allows the management of Host, initiators

### Get the list of hosts

 - [GET /block-storage/v1alpha1/host-initiators](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostlist.md): Get the list of hosts

### Create a host

 - [POST /block-storage/v1alpha1/host-initiators](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostcreate.md): Create a host with same protocol initiators

### Delete a host by {hostId}

 - [DELETE /block-storage/v1alpha1/host-initiators/{hostId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostdelete.md): Delete a host by {hostId}

### Get the host details by {hostId}

 - [GET /block-storage/v1alpha1/host-initiators/{hostId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostgetbyid.md): Get the host details by {hostId}

### Update Host by {hostId}

 - [PUT /block-storage/v1alpha1/host-initiators/{hostId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostupdatebyid.md): Update host details by {hostId}. Host can only be updated with the same protocol initiators

### Get Host CHAP details by {hostId}

 - [GET /block-storage/v1alpha1/host-initiators/{hostId}/chap](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/gethostchapbyid.md): Get Host CHAP details by {hostId}

### Update Host CHAP by {hostId}

 - [PUT /block-storage/v1alpha1/host-initiators/{hostId}/chap](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/updatehostchapbyid.md): CHAP can be updated only on iSCSI host on HPE GreenLake for Block Storage 10.4.0 or later and NVMe/TCP host on HPE GreenLake for Block Storage 10.5.0 or later.

### Generate a DH-HMAC-CHAP host key usable for NVMe In-Band Authentication for Host by {hostId}

 - [POST /block-storage/v1alpha1/host-initiators/{hostId}/chapkey](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/generatechapkeybyid.md): CHAP key can be generated only on NVMe/TCP host on HPE GreenLake for Block Storage 10.5.0 and later system OS versions.

### Get details of a host identified by {hostId} across its associated systems

 - [GET /block-storage/v1alpha1/host-initiators/{hostId}/mapped-devices](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostmappeddevice.md): Get details of a host identified by {hostId} across its associated systems

### Get the volume performance history data associated with a host identified by {uid}

 - [GET /block-storage/v1alpha1/host-initiators/{hostId}/storage-performance-history](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostvolumeperformancehistoryget.md): Get the volume performance history data associated with a host identified by {uid}

### Get details of volumes associated with a host identified by {uid}

 - [GET /block-storage/v1alpha1/host-initiators/{hostId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostvolumesget.md): Get details of volumes associated with a host identified by {uid}

### Get the list of initiators

 - [GET /block-storage/v1alpha1/initiators](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostinitiatorlist.md): Get the list of initiators

### Create initiator

 - [POST /block-storage/v1alpha1/initiators](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostinitiatorcreate.md): Create initiator

### Delete initiator by {initiatorId}

 - [DELETE /block-storage/v1alpha1/initiators/{initiatorId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostinitiatordelete.md): Delete initiator by {initiatorId}

### Get the initiator details by {initiatorId}

 - [GET /block-storage/v1alpha1/initiators/{initiatorId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostinitiatorgetbyid.md): Get the initiator details by {initiatorId}

## host-paths

The ports API allows the management of host-paths

### Get details of HPE Alletra Storage MP B10000 Host Paths

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-paths/devicetype4getallhostpaths.md): Get details of HPE Alletra Storage MP B10000 Host Paths

### Get details of HPE Alletra Storage MP B10000 Host Path identified by {HostPathId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths/{hostPathId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-paths/devicetype4gethostpathsbyid.md): Get details of HPE Alletra Storage MP B10000 Host Path identified by {HostPathId}

## host-sets

The ports API allows the management of host-sets

### Get details of HPE Alletra Storage MP B10000 Host Sets

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-sets/devicetype4getallhostsets.md): Get details of HPE Alletra Storage MP B10000 Host Sets

### Get details of HPE Alletra Storage MP B10000 Host Set identified by {HostSetId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets/{hostSetId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-sets/devicetype4gethostsetsbyid.md): Get details of HPE Alletra Storage MP B10000 Host Set identified by {HostSetId}

## hosts

The ports API allows the management of hosts

### Get details of HPE Alletra Storage MP B10000 Hosts

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/hosts/devicetype4getallhosts.md): Get details of HPE Alletra Storage MP B10000 Hosts

### Get details of HPE Alletra Storage MP B10000 Host identified by {HostId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts/{hostId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/hosts/devicetype4gethostbyid.md): Get details of HPE Alletra Storage MP B10000 Host identified by {HostId}

## storage-pools

The pools API allows the management of storage pools

### Get all storage-pools details by HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/devicetype4storagepoollist.md): Get all storage-pools details by HPE Alletra Storage MP B10000

### Get details of HPE Alletra Storage MP B10000 storage-pool identified by {id}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/devicetype4storagepoolgetbyid.md): Get details of HPE Alletra Storage MP B10000 storage-pool identified by {id}

### Get all volumes for storage-pool identified by {uuid} of HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/devicetype4storagepoolvolumegetbyid.md): Get all volumes for storage-pool identified by {uuid} of HPE Alletra Storage MP B10000

### Get all storage pools for a device {systemId}

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/storage-pools](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/storagepoolslist.md): Get all storage pools for a device {systemId}

### Get details of storage pools identified by {id}

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/storage-pools/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/storagepoolsgetbyid.md): Get details of storage pools identified by {id}

### Get all volumes for storage-pool identified by {id}

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/storage-pools/{id}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/storagepoolvolumeslist.md): Get all volumes for storage-pool identified by {id}

## storage-systems

The storage-systems API allows the management of storage device.

### Get Application Summary for an HPE Alletra Storage MP B10000 storage system

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/application-summary](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4applicationsummaryget.md): Get Application Summary for an HPE Alletra Storage MP B10000 storage system

### Get latest capacity trend data and forecasted data

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-forecast](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4systemcapacityforecastget.md): Get latest capacity trend data and forecasted data

### Get capacity time until full data for an HPE Alletra Storage MP B10000 storage system

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/capacity-timeuntilfull](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4systemcapacitytimeuntilfull.md): Get capacity time until full data for an HPE HPE Alletra Storage MP B10000 storage system

### Get Top headroom contribution by volumes/Apps for device-type4

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/headroom-contribution](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4getheadroomcontribution.md): Get Top headroom contribution by volumes/Apps for device-type4

### Get hotspots for HPE Alletra Storage MP B10000 storage system based on resourceType VOLUMES or VOLUME-SET and metricType LATENCY

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hotspots](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4gethotspots.md): Get the top hotspots segregated into read and write categories

### Get system level latency factors

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/latency-factors](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/device4latencyfactorsget.md): Get system level latency factors of system identified by {systemId}

### Get resource contention data for resources DISK and CPU for device-type4

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/resource-contention](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-systems/devicetype4getresourcecontentiondata.md): Get the top volume contributors and timeseries data for disk and cpu resource contention

## volume-sets

The Volume-sets API allows the management of volume sets

### Get all applicationset details for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetslist.md): Get all applicationset details for HPE Alletra Storage MP B10000

### Create Application Set for an HPE Alletra Storage MP B10000 storage system

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetscreate.md): Create Application Set for an HPE Alletra Storage MP B10000 storage system

### Export applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetexport.md): Export applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get details of HPE Alletra Storage MP B10000 replication partners identified by {systemId} and {appsetId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getreplicationpartnersbyappsetid.md): Get details of HPE Alletra Storage MP B10000 replication partners identified by {systemId} and {appsetId}

### Get volume details of replication partners identified by {appsetId} and {replicationPartnerId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners/{replicationPartnerId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getreplicationpartnervolumesbyappsetid.md): Get volume details of replication partners identified by {appsetId} and {replicationPartnerId} for HPE Alletra Storage MP B10000

### Remove HPE Alletra Storage MP B10000 snapset in system identified by {snapsetId}

 - [DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetsnapshotgetbyid.md): Remove HPE Alletra Storage MP B10000 snapset in system identified by {snapsetId}

### Get details of snapsets identified by {snapsetId} for Applicationset identified by {appsetId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4snapsetsgetbyid.md): Get details of snapset identified by {snapsetId} for Applicationset identified by {appsetId} for HPE Alletra Storage MP B10000

### Unexport applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/un-export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetunexport.md): Unexport applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get volumes for an applicationset identified by appsetUid

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetvolumeslist.md): Get volumes for an applicationset identified by appsetUid

### Remove applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetsdeletebyid.md): Remove applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get applicationset details for an applicationset identified by appsetUid

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetsgetbyid.md): Get applicationset details for an applicationset identified by appsetUid

### Edit applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetseditbyid.md): Edit applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get capacity details for an applicationset identified by appsetUid

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/capacity-statistics](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetcapacitystatisticsgetbyid.md): Get capacity details for an applicationset identified by appsetUid

### Get details of protection policies configured on application set identified by {id} created on HPE Alletra Storage MP B10000 identified by {systemId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getprotectionpolicies.md): Get details of protection policies configured on application set identified by {id} created on HPE Alletra Storage MP B10000 identified by {systemId}

### Add protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4createprotectionpolicy.md): Add protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Edit protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4editprotectionpolicies.md): Edit protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Fix protection policy configuration on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/fix](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4fixprotectionpolicy.md): Remedies issues caused in protection policy configuration on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Remove protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/remove](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4removeprotectionpolicies.md): Remove protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get hosts and proximity details identified by application set {id} for HPE Alletra Storage MP B10000 identified by {systemId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getproximitysettings.md): Get hosts and proximity details identified by application set {id} for HPE Alletra Storage MP B10000 identified by {systemId}

### Change proximity settings of hosts where volume sets are exported identified by {id} and {systemId} from HPE Alletra Storage MP B10000

 - [PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4editproximitysettings.md): Change proximity settings of hosts where volume sets are exported identified by {id} and {systemId} from HPE Alletra Storage MP B10000

### Actions on volume set identified by {id} and {systemId} from HPE Alletra Storage MP B10000

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/remote-protection/actions](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4actiononvolumesets.md): Actions on volume set identified by {id} and {systemId} from HPE Alletra Storage MP B10000

### Get snapshot details of volume sets identified by {id} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetsnapshotslist.md): Get snapshot details of volume sets identified by {id} for HPE Alletra Storage MP B10000

### Create snapshot for application set identified by {id}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetssnapshotcreate.md): Create snapshot for application set identified by {id}

### Get supported protection types for application set identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/supported-protection](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getsupportedprotectiontypes.md): Get supported protection types for application set identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get all volume-sets for a systemId

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/volume-sets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/volumesetlistforsystembysystemid.md): Get all volume sets for a systemId

### Get volume-set identified by id

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/volume-sets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/volumesetsystemgetbyid.md): Get volume-set identified by id

### Get all volume-sets

 - [GET /block-storage/v1alpha1/volume-sets](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/volumesetlist.md): Get all volume sets

### Get volume-set identified by id

 - [GET /block-storage/v1alpha1/volume-sets/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/volumesetgetbyid.md): Get volume-set identified by id

### Get volumes identified by volume set id

 - [GET /block-storage/v1alpha1/volume-sets/{id}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/volumesetgetbyvolumesetid.md): Get volumes  identified by volume set id

## volumes

The volumes API allows the management of volumes

### Create a clone of a snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000 systems.

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/clone](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4snapshotclonecreate.md): Create a clone of a snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000 systems.

### Export vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunexportforsnapshot.md): Export vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Create snapshot of snapshot identified by {snapshotId} on a HPE Alletra storage MP system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4snapshotofsnapshotcreate.md): Create snapshot of snapshot identified by {snapshotId} on a HPE Alletra storage MP system identified by {systemId}

### Unexport vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/un-export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlununexportforsnapshot.md): Unexport vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get details of vluns for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getsnapshotvlunslist.md): Get details of vluns for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

### Get details of vlun identified by {id} for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getsnapshotvlunsbyid.md): Get details of vlun identified by {id} for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

### Get all volumes details for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeslist.md): Get all volumes details for HPE Alletra Storage MP B10000

### Create a new volume for an HPE Alletra Storage MP B10000 storage system

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumecreate.md): Create a new volume for an HPE Alletra Storage MP B10000 storage system

### Get performance history of Volumes on storage system identified by {systemid}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes-performance](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getvolumesperformancehistory.md): Get performance history of Volumes on storage system identified by {systemid}

### Remove volume identified by {volumeId} from HPE Alletra Storage MP B10000

 - [DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumedelete.md): Remove volume identified by {volumeId} from HPE Alletra Storage MP B10000

### Get details of HPE Alletra Storage MP B10000 Volume identified by {id}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumegetbyid.md): Get details for a single HPE Alletra Storage MP B10000 volume identified by {id}

### Edit volume identified by {volumeId} from HPE Alletra Storage MP B10000

 - [PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeedit.md): Edit volume identified by {volumeId} from HPE Alletra Storage MP B10000

### Get volume capacity trend data of HPE Alletra Storage MP B10000 Volume identified by {id}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/capacity-history](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumecapacityhistorygetbyid.md): Get volume capacity trend data of HPE Alletra Storage MP B10000 Volume identified by {id}

### Create a clone volume identified by {id} for HPE Alletra Storage MP B10000 systems.

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/clone](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeclonecreate.md): Create a clone volume identified by {id} for HPE Alletra Storage MP B10000 systems.

### Export vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunexport.md): Export vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get histogram buckets distribution of I/Os of a volume for a given duration.

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-histogram](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getperformancehistogram.md): Get the I/O size histogram for a volume over the specified duration. The buckets query parameter must contain one or more of: Size512B, Size1k, Size2k, Size4k, Size8k, Size16k, Size32k, Size64k, Size128k, Size256k, Size512k, Size1m, Size2m

### Get performance trend data of HPE Alletra Storage MP B10000 Volume identified by {id}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-history](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeperformancehistorygetbyid.md): Get performance trend data of HPE Alletra Storage MP B10000 Volume identified by {id}

### Get performance statistics of HPE Alletra Storage MP B10000 Volume identified by {id}

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/performance-statistics](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeperformancestatisticsgetbyid.md): Get performance statistics of HPE Alletra Storage MP B10000 Volume identified by {id}

### Get snapshot details of volume identified by {id} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumesnapshotslist.md): Get snapshot details of volume identified by {id} for HPE Alletra Storage MP B10000

### Create snapshot for volumes identified by {id}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/snapshots](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumesnapshotcreate.md): Create snapshot for volumes identified by {id}

### Unexport vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/un-export](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlununexport.md): Unexport vlun for volume identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Get details of vluns for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/vluns](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunslist.md): Get details of vluns for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

### Get the details of the clone volumes associated with a base volume identified by {volumeId} for HPE Alletra Storage MP B10000 systems.

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getclones.md): Get the details of the clone volumes associated with a base volume identified by {volumeId} for HPE Alletra Storage MP B10000 systems.

### Promote a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones/{cloneId}/promote](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4promoteclonevolume.md): Promote a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Resynchronize a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/clones/{cloneId}/resync](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4resyncclonevolume.md): Resynchronize a clone volume identified by {cloneId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get volume latency annotations for device-type4

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/latency-annotations](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getvolumelatencyannotations.md): Get the high latency points to be annotated segregated into read and write categories

### Get latency drifts of a volume for a give duration

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/performance-drifts](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getperformancedrifts.md): Get latency drifts of a volume for a give duration.The minimum duration supported is 8 hours and a maximum duration of 2 days. Drifts are detected in both read and write latency metrics

### Remove HPE Alletra Storage MP B10000 snapshot in system identified by {snapshotId}

 - [DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumesnapshotgetbyid.md): Remove HPE Alletra Storage MP B10000 snapshot in system identified by {snapshotId}

### Get details of snapshot identified by {snapshotId} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4snapshotsgetbyid.md): Get details of vlun identified by {id} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

### Promote a snapshot identified by {snapshotId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4promotesnapshot.md): Promote a snapshot identified by {snapshotId} of a volume identified by {volumeId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Remove vlun idenfied by {id} form volume identified by {volumeId} from HPE Alletra Storage MP B10000

 - [DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/vluns/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunsdelete.md): Remove vlun idenfied by {id} form volume identified by {volumeId} from HPE Alletra Storage MP B10000

### Get details of vlun identified by {id} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/vluns/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunsgetbyid.md): Get details of vlun identified by {id} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

### Get details of volumes identified with {systemId}

 - [GET /block-storage/v1alpha1/storage-systems/{systemId}/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/volumelistforsystembysystemid.md): Get details of volumes identified with {systemId}

### Produce a set of provisioning recommendations based on the provided input parameters.

 - [POST /block-storage/v1alpha1/storage-systems/provisioning-recommendations](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/provisioningrecommendations.md): Produce a set of provisioning recommendations based on the provided input parameters.

### Get all volumes

 - [GET /block-storage/v1alpha1/volumes](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/volumeslist.md): Get all volumes

### Get details of Volume identified by {id}

 - [GET /block-storage/v1alpha1/volumes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/volumegetbyid.md): Get details of Volume identified by {id}

## snapshots

### Get the details of all read-write parent snapshots and base volume to which the child snapshot identified by {childSnapshotId} can be restored on HPE Alletra Storage MP B10000 system identified by {systemId}.

 - [GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{childSnapshotId}/restore-options](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/snapshots/devicetype4getsnapshotrestoreoptions.md): Get the details of all read-write parent snapshots and base volume to which the child snapshot identified by {childSnapshotId} can be restored on HPE Alletra Storage MP B10000 system identified by {systemId}.

### Restore a child snapshot identified by {childSnapshotId} to a read-write parent snapshot identified by {parentSnapshotId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{parentSnapshotId}/snapshots/{childSnapshotId}/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/snapshots/devicetype4restoresnapshotofsnapshot.md): Restore a child snapshot identified by {childSnapshotId} to a read-write parent snapshot identified by {parentSnapshotId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

