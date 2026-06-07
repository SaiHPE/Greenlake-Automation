---
title: "HPE Greenkake for Credential Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials.md"
scraped_at: "2026-06-07T06:13:36.397208+00:00Z"
---

# HPE Greenkake for Credential Management API

With the HPE GreenLake for Credential Management APIs, you can add, update, delete, and get information about user credentials in a standard enterprise, managed service provider (MSP), or MSP tenant workspaces.

  You can view request and response samples for four scenarios while exploring the API reference.

  The Create credential API has sample requests and responses.

  1. In the **Request samples** panel, click the drop-down to choose a scenario.

  2. In the **Response samples** panel, select the **201** tab and click the drop-down to choose a scenario.

  The Get list of credentials and Reset a credential APIs have response samples.

  * In the **Response samples** panel, select the **200** tab and click the drop-down to choose a scenario.

  The four scenarios are:

  * **Workspace credentials for HPE GreenLake service manager**—Provides a sample relevant to HPE GreenLake platform service manager credentials for standard enterprise or MSP workspaces.

  * **MSP tenant credentials for HPE GreenLake service manager**—Provides a sample relevant to HPE GreenLake platform service manager credentials in an MSP tenant workspace.

  * **Workspace credentials for a provisioned service manager**— Gives an example relevant to provisioned service manager credentials for standard enterprise or MSP workspaces.

  * **MSP tenant credentials for a provisioned service manager**—Gives an example relevant to provisioned service manager credentials in an MSP tenant workspace.


Version: 1.0.0
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### BearerAuth

Type: http
Scheme: bearer

## Download OpenAPI description

[HPE Greenkake for Credential Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/credentials/public/openapi/credentials/index.yaml)

## Credential Management

### Get list of credentials

 - [GET /workspaces/v1/credentials](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/get_all_credentials_workspaces_v1_msp_tenants__tenantid__credentials_get.md): Retrieve a list of all credentials for a user in a standard enterprise, managed service provider (MSP), or MSP tenant workspace. 

NOTE: Use the filter query parameter in an MSP tenant workspace and filter on the tenantId property.

### Create a credential

 - [POST /workspaces/v1/credentials](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/create_credentials_workspaces_v1_msp_tenants__tenantid__credentials_post.md): Create a new credential in a standard enterprise, managed service provider (MSP), or MSP tenant workspace. 

NOTE: In an MSP tenant workspace, use the associatedTenant property

### Delete a credential

 - [DELETE /workspaces/v1/credentials/{credentialId}](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/delete_credentials_workspaces_v1_msp_tenants__tenantid__credentials__credentialid__delete.md): Delete a credential for a user in a standard enterprise, managed service provider (MSP), or MSP tenant workspace.

### Reset a credential

 - [POST /workspaces/v1/credentials/{credentialId}/reset](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/reset_credential_workspaces_v1_msp_tenants__tenantid__credentials__credentialid__reset_post.md): Reset the client secret for a credential in a standard enterprise, managed service provider (MSP), or MSP tenant workspace.

