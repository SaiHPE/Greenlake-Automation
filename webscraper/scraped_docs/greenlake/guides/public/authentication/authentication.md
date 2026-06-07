---
title: "API Authentication | HPE GreenLake Developer Portal"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication.md"
scraped_at: "2026-06-07T06:13:20.934456+00:00Z"
---

# Authentication

This guide explains how to create and manage access tokens for GreenLake cloud APIs.

## Prerequisites

Before generating access tokens, ensure you have:

- An active GreenLake account.
- Access to the required services in your workspace. For more information, see [Services](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-A34E1C6D-809E-47F0-B274-1F6CA5285A0E.html) and [Adding services to your workspace](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-2CCB459E-9B36-4EEF-830E-4D206F0ED1A1.html) in the GreenLake Cloud User Guide.


## Creating a personal API client

By creating a personal API client, you create the client ID and client secret used to access GreenLake or another service's APIs. The client ID and client secret are used to generate an access token. An access token authenticates API communication between your application and GreenLake.

Each user can create a maximum of seven personal API clients per workspace.

1. On the GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. Select **Personal API clients.**
3. Click **Create personal API client.**
4. In **Personal API client,** enter a name for the API client.
5. Select the **Service** that you want to access. Choose **HPE GreenLake Cloud Platform** to access APIs related to:
  - Data Services
  - GreenLake cloud services (for example, Audit Logs, Devices, Reporting, User Management and so on)
  - HPE Compute Ops Management
  - HPE Consumption Analytics
  - HPE Sustainability Insight Center
6. Click **Create personal API client** to continue. The **Personal API client created** display appears and shows that your credentials were successfully created.
7. Click **Copy** next to **Client ID** and **Client Secret** and save both to a safe and secure location.
8. Click **Close** to continue. You are returned to the main **Personal API clients** page, where you can generate the access token.


GreenLake cloud does not store your client secret. If you lose it, you must reset your credentials.

## Generating an access token

On the **Personal API clients** page, you can view API credential details and generate access tokens.

Access tokens are small strings of code sent in the header of your API calls. Access tokens identify whether you (or your application) have the necessary permissions to securely access resources through an API call. Access tokens inherit the permissions of the user that created the personal API client.

- In a standard enterprise workspace or in a tenant workspace, the access token applies automatically to the workspace of the logged-in user.
- In Managed Service Provider (MSP) mode, all MSP roles can configure access tokens to apply to the MSP mode workspace or to a tenant workspace.


To learn more about workspace types, see [Manage workspace type](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-CCD4CFC8-D67A-4AFF-953D-637A68588009.html) or [Manage Service Provider (MSP) mode Terminology](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-AE0274B2-A922-49E9-886D-AA85C9DC118E.html).

GreenLake tokens stay valid for 15 minutes. Tokens for all other HPE services stay valid for 120 minutes.

1. On the **Home** page, click **Manage Workspace** and then click the **Personal API clients** card.
2. Click the arrow next to the credential name to display the credential details.
3. Click **Generate access token.** The **Generate access token** dialog appears. The options in the **Generate access token** depend on your workspace type. Only MSPs require and see the option **Generate access token** for access to workspace.
4. From **Generate access token,** perform the following steps.
  1. The **Client ID** is prepopulated with the client ID.
  2. Paste the client secret into the **Client secret** field.
  3. (MSP-only) From the **Generate access token for access to workspace** drop-down, choose, or search for the workspace for which to create the access token. In MSP mode, you can choose to generate a token for the MSP workspace or a tenant workspace. API requests that are made using this access token only retrieve results from or affect the chosen workspace.
5. Click **Create access token.** The **Access token created** modal appears with your **Access token.**
6. Click **Copy** next to your access token.


GreenLake does not store tokens. Therefore, you must copy and store your access token in a secure location.

The access token can be used as an authorization bearer token to make secure REST API calls to GreenLake API services. For example, if using cURL, include `-H 'Authorization: Bearer <YOUR_JWT_HERE>'` in your API request header. Replace `<YOUR_JWT_HERE>` with your token. The API reference documentation on [GreenLake Developer Portal](https://developer.greenlake.hpe.com/docs/greenlake/services/) provides example request headers in multiple programming languages.

## Viewing code samples for generating an access token

You can programmatically generate access tokens. Through the GreenLake UI, you can create sample code for this purpose.

GreenLake tokens stay valid for 15 minutes. Tokens for all other HPE services stay valid for 120 minutes.

1. On the **Home** page, click **Manage Workspace** and then click **Personal API client.**
2. Click the arrow next to the credential name to display the credential details.
3. Click **View code sample.** The **Generate code sample** modal appears. The options in the **Generate code sample** modal depend on your workspace type. Only managed service providers require, and see the option **Produce sample for accessing.**
4. From the **Generate code sample** modal, perform the following steps.
  1. (MSP-only) From the **Produce sample for accessing** drop-down, select the target workspace. In MSP mode, you can choose to generate a token for the MSP workspace or a tenant workspace. The resulting code sample generates an access token applicable to the chosen workspace.
  2. From the **Select programming language** drop-down, select the programming language.
  3. **Personal API client** is always prepopulated with the name given to the personal API client.
  4. Paste the client secret into the **Enter client secret** field. The information you selected or entered is displayed in the code sample.
5. Click **Copy code sample.** The copied code sample can be used to generate an access token programmatically.
6. Click **Close** when you are finished.


To learn more about workspace types, see [Manage workspace type](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-CCD4CFC8-D67A-4AFF-953D-637A68588009.html) or [Manage Service Provider (MSP) mode Terminology.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-AE0274B2-A922-49E9-886D-AA85C9DC118E.html)

The access token can be used as an authorization bearer token to make secure REST API calls to GreenLake API services. For example, if using cURL, include `-H 'Authorization: Bearer <YOUR_JWT_HERE>'` in your API request header. Replace `<YOUR_JWT_HERE>` with your token. The API reference documentation on [GreenLake Developer Portal](https://developer.greenlake.hpe.com/docs/greenlake/services/) provides example request headers in multiple programming languages.

## Resetting your client secret

There may be a time when you want to reset your client secret for security purposes.

1. Click the ellipsis next to **Generate Access Token** and select **Reset client secret.**
2. Click **Reset Client Secret.** The **Personal API client secret reset** dialog appears.
3. Click **Copy** next to the **Client secret.** Save the client secret in a secure location, as GreenLake cloud does not store the client secret.
4. Click **Close.**


## Deleting your client credentials

1. Click the ellipsis next to **Generate Access Token.**
2. Select **Delete personal API client.** The **Delete personal API client** dialog appears.
3. Click **Delete personal API client.**


If a user is deleted from GreenLake, any personal API clients generated and associated with any services owned by this user will no longer be valid.

## Points to remember

- GreenLake tokens stay valid for 15 minutes and tokens for all other HPE services stay valid for 120 minutes.
- The credentials created for a user are valid until they are deleted, reset, or the user account is removed.
- Always store client secrets and access tokens in secure locations.