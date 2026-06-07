---
title: "HPE GreenLake for Service Catalog glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/glossary.md"
scraped_at: "2026-06-07T05:46:13.774889+00:00Z"
---

# HPE GreenLake for Service Catalog glossary

## Acronyms

### MSP

An MSP workspace provides the MSP administrators with options to manage multiple independent HPE GreenLake tenant workspaces, devices, and licenses. Only some services support this model.

## Terms

### MSP supported

This field (`mspSupported`) is used to filter service managers based on whether or not they support MSP.

- **True**—The service supports MSP.
- **False**—The service does not support MSP.


### Provisioned state

This field (`provisionStatus`) represents the provisioning status of a service.

- `PROVISION_INITIATED`—Service provisioning has been initiated.
- `PROVISIONED`—The service has been successfully provisioned.
- `PROVISION_FAILED`—Service provisioning has failed.
- `UNPROVISION_INITIATED`—The service is being un-provisioned.
- `UNPROVISIONED`—The service has been successfully un-provisioned.
- `UNPROVISION_FAILED`—Service un-provisioning has failed.


Think of service provisioning as adding or deploying a service in a workspace.

### Media Category

This field (`category`) represents the type of the media.

- `LOGO`—The media uploaded is a logo representing the service.
- `SCREENSHOT`—The media uploaded is a screenshot of some feature offered by the service.
- `VIDEO`—The media uploaded is a video explaining some feature or workflow for the service.


### Region

A geographical area where services are provisioned or need to be provisioned.

| Region code | Region |
|  --- | --- |
| `ap-ausnz` | Asia-Pacific Australia and New Zealand |
| `ap-east` | Asia-Pacific East |
| `ap-northeast` | Asia-Pacific Northeast |
| `ap-south` | Asia-Pacific South |
| `ap-southeast` | Asia-Pacific Southeast |
| `ca-central` | Canada Central |
| `ca-east` | Canada East |
| `cn-east` | China East |
| `cn-north` | China North |
| `eu-central` | Europe Central |
| `eu-north` | Europe North |
| `eu-west` | Europe West |
| `mea` | Middle-East and Africa |
| `sa-east` | South America East |
| `us-central` | Central United States |
| `us-east` | Eastern United States |
| `us-gov` | United States Government |
| `us-west` | Western United States |
| `att-mcd-us-west` | ATT McDonald's Cluster |
| `att-ent-us-west` | ATT Enterprise Cluster |
| `att-hilton-us-west` | ATT Hilton Cluster |


### Service catalog

The service catalog is a list of services available to be added to your workspace.

### Service manager

Some services in the service catalog are qualified as service managers. These are entries created corresponding to the applications that were part of the application-centric experience of the past. HPE GreenLake cloud moved to a service-centric UI and experience in December 2023.

The service manager entries were retained as HPE GreenLake still supports workflows pertaining to them. Most newer services will be pure services (without the need for a service manager entry).

### Provisioned services

The services that are deployed (provisioned) in a specific region for a given workspace.

### Service manager provisioned

The services that are deployed (provisioned) in a specific region.