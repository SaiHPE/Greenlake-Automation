---
title: "Backup and Recovery API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api.md"
scraped_at: "2026-06-07T05:46:27.982222+00:00Z"
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

[Backup and Recovery API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api.yaml)

## hypervisor-managers

The hypervisor-managers API allows the management of hypervisor-managers

### Register a new hypervisor manager.

 - [POST /backup-recovery/v1alpha1/hypervisor-managers](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api/hypervisor-managers/hypervisormanagercreate.md): Register the hypervisor manager for data management.

### Unregister a hypervisor manager.

 - [DELETE /backup-recovery/v1alpha1/hypervisor-managers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api/hypervisor-managers/unregisterhypervisormanager.md): Unregister a hypervisor manager.

### Update a hypervisor manager.

 - [PATCH /backup-recovery/v1alpha1/hypervisor-managers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api/hypervisor-managers/hypervisormanagerupdate.md): Update attributes for a hypervisor manager.

