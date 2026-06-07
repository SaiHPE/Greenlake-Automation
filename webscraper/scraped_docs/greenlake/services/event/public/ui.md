---
title: "Manage webhooks and events in the HPE GreenLake cloud UI"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/ui.md"
scraped_at: "2026-06-07T05:46:10.014073+00:00Z"
---

# Manage webhooks and events in the HPE GreenLake cloud UI

The content in this section describes how HPE GreenLake administrators or operators can use the HPE GreenLake UI to:

- Register, edit, test, and delete webhooks
- Subscribe to events
- Remove event subscriptions


## Setting up your first webhook and subscribing to an event

### **About this task**

Before registering a webhook and receiving event messages from HPE
GreenLake cloud, you must configure a webhook destination and handler
on your server to receive, validate, and handle events. After
configuring the webhook destination, use the HPE GreenLake UI to
register the webhook and subscribe to an event. Optionally, visit the
HPE GreenLake Developer Portal to read the documentation about
specific events.

### **Procedure**

1. [Configure a webhook destination and handler.](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/webhooks/#configure-a-webhook-handler)
2. [Register your webhook.](#registering-a-webhook)
3. (Optional) [Find events on HPE GreenLake Developer Portal.](#finding-events-on-hpe-greenlake-developer-portal)
4. [Subscribe to an event.](#subscribing-to-an-event)


## Registering a webhook

### **Prerequisites**

- You need **Create** permissions for **Automations Webhook.** To change your permissions, talk to your HPE GreenLake administrators. Find out more about [HPE GreenLake roles and permissions](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).
- Before registering a webhook by API, you need to create a webhook handler. While webhook verification is optional, it is enabled by default and is strongly recommended for secure communications. For details, see [Webhook Verification](/docs/greenlake/services/event/public/webhooks#webhook-verification) and [Create a webhook handler.](/docs/greenlake/services/event/public/webhooks/#configure-a-webhook-handler)


### **About this task**

Webhooks are automated HTTP requests that send real-time information
about an event (known as a message) from HPE GreenLake to a
destination of your choice. When registering a webhook, you provide a
URL to a server (known as the webhook destination) that you want HPE
GreenLake to send the real-time event information to.

You can create up to five webhooks.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click **Register webhook.**
4. Complete the **Register webhook** form. Providing a **Description** is optional. All the other information is mandatory.
  1. Provide the **Name,** **Description,** **Webhook URL,** **Challenge request setting,** or **Shared secret**.
    - **Name**—Provide a name for the webhook. Webhook names must be unique within your workspace. Webhook names can be alphanumeric with the following special characters also allowed: `-`,`.`, `@`, and `\`. There is a maximum character limit of 50.
    - **Description**—Provide a short and insightful description that outlines the purpose of the webhook. The maximum character limit is 100.
    - **Webhook URL**—The URL to the webhook destination that you want to receive the information contained in the event message.
    - **Challenge request**—Select or deselect the **Require challenge request handshake** checkbox. This checkbox enables or disables (skips) the webhook verification process. Enabling webhook verification is recommended. Disabling (skipping) the challenge request removes the **Actions > Test** functionality.
    - **Shared secret**—A shared secret, or password, is used to generate an HMAC signature to verify message integrity. The shared secret must be between 4 and 100 characters. The shared secret is securely stored. Once it is created, it cannot be retrieved; it can only be replaced. It is good practice to change secrets periodically and use unique shared secrets for every webhook. Optionally, you can add two shared secrets to assist with zero downtime key rotation.
      - If you use one shared secret and rotate the key, downtime is possible until webhook destinations verifying the signature are updated.
      - If you add two shared secrets, the second secret is used for verification when rotating the first.
  2. Select an **Authentication type** and fill in the required information. HPE GreenLake supports API key authentication, OAuth authentication, or no authentication.
    - **API key**—A simple token-based authentication mechanism that is used to authenticate requests. Enter the **API key** in the **API key** box.
    - **OAuth**—OAuth 2.0 is an authorization protocol that allows users (or applications) to grant access to or interact with data without sharing passwords. Enter the **Client ID,** **Client Secret,** and **Client token issuer URL.**
    - **No authentication**—If you select **No authentication,** you do not have to add additional details.
  3. (Optional) Select or deselect **Batching enabled.** When the checkbox is not selected, webhook events are sent to the webhook destination one-by-one. With batching enabled (checkbox selected), events are sent in small groups (known as a "batch"). This reduces the number of requests the webhook destination needs to handle and can improve performance. An event batch is sent when one of the following conditions is met:
    - **Event count**—When the maximum number of events are queued.
    - **Time window**—If the maximum number of events is not met, events are sent after a short waiting time.
5. Click **Register webhook.** A verification challenge is sent to the webhook destination by default. While
awaiting a response, the webhook is put in a pending state. After successful verification, the webhook is set to active. You will receive a confirmation email when the webhook is successfully registered. The confirmation email includes the webhook ID.


If the webhook is successfully registered, you can continue and [subscribe to an event.](/docs/greenlake/services/event/public/ui#subscribing-to-an-event) If the webhook registration fails, check your server configuration.

## Viewing webhook details

### **Prerequisites**

You need to have registered at least one webhook.

### **About this task**

You can review information about the registered webhook.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Under **Webhooks,** click a webhook. The webhook details page opens.


The details page includes the following information:

- **Webhook URL**—The URL of the registered webhook destination.
- **State**—The state indicates if the webhook is pending, active, disabled, critical, or in a warning state. Find out more about [Webhook states.](/docs/greenlake/services/event/public/webhooks#webhook-states)
- **Webhook ID**—The unique identifier of the webhook.
- **Batching enabled**—Confirms whether batching is enabled.
- **Challenge request**—Displays whether the challenge request is required or skipped.
- **Endpoint requested rate limit**—The rate limit of the webhook destination endpoint. The possible values are:
  - Not configured
  - The number of events per minute
  - Unlimited
- **Last updated**—The date the webhook was last edited.
- **Registered**—The date the webhook was registered.
- **Registered by**—The email address of whoever created the webhook.
- **Event subscription**—Here you can view event details and perform various actions.
  - Subscribe to an event. See [Subscribing to an event.](#subscribing-to-an-event)
  - View details related to the event.
    - **Event**—The name of the event.
    - **Event type**—The event type is a string value used to specify the occurrence that triggers a message to be sent to the webhook URL.
    - **API Group**—The HPE GreenLake service that the event belongs to.
    - **Identity used for authorization**—The email address of the user who subscribed to the event.
  - Remove an event subscription. See [Removing an event subscription.](#removing-an-event-subscription)
- **Recent Deliveries** A record of successful and failed event message deliveries.
  - **Delivery:**
    - For a single event, the event type string is listed to specify the occurrence that triggers a message to be sent to the webhook URL.
    - For batched events, the number of events sent in the batch is listed. For example, "Batch of 10 events".
  - **ID**—The unique identifier of an event. The same as **ID** in the **Delivery details** dialog.
  - **Response**— The HTTPS status code. For more information, see [Webhook HTTPS status.](/docs/greenlake/services/event/public/webhooks#webhook-https-status-codes)
  - **Date**—The delivery date of the event message.
- Click a recent delivery to open the **Delivery details** dialog and see additional information.
  - **Resource URI**—The identifier of the event resource.
  - **Request header**—The HTTP header carrying metadata about the event. This includes the `Hpe-Webhook-Signature`.
  - **Request body**—The payload of the HTTP request. This contains the event type, event data, and metadata.
  - **Response header**—The HTTP headers returned by your endpoint in response to the webhook call. This might include status codes and other metadata about how the event was processed.
  - **Response body**—The content returned by your endpoint, confirming successful event processing or providing details about any errors  encountered.


To retry failed deliveries, see [Retrying failed event deliveries.](#retrying-failed-event-deliveries)

## Editing a webhook

### **Prerequisites**

- You need **Edit** permissions for **Automations Webhook**. To change
your permissions, talk to your HPE GreenLake cloud administrators.
Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)
- You must have registered at least one webhook.


### **About this task**

You can edit the details of an already created webhook.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that you want to change.
4. Click **Actions.**
5. Click **Edit.**
6. From the **Edit webhook** form, make the required changes. If you do not edit a field, it remains unchanged.
  1. (Optional) Change the **Name,** **Description,** **Webhook URL,** **Challenge request setting,** or **Shared secret** as required.
    - **Name**—Provide a name for the webhook. Webhook names must be unique within your workspace. Webhook names can be alphanumeric with the following special characters also allowed: `-`,`.`, `@`, and `\`. There is a maximum character limit of 50.
    - **Description**—Provide a short and insightful description that outlines the purpose of the webhook. The maximum character limit is 100.
    - **Webhook URL**—The URL to the webhook destination that you want to receive the information contained in the event message.
    - **Challenge request**—Select or deselect the **Require challenge request handshake** checkbox. This checkbox enables or disables (skips) the webhook verification process. Enabling webhook verification is recommended. Disabling (skipping) the challenge request removes the **Actions > Test** functionality.
    - **Shared secret**—A shared secret, or password, is used to generate an HMAC signature to verify message integrity. The shared secret must be between 4 and 100 characters. The shared secret is securely stored. Once it is created, it cannot be retrieved; it can only be replaced. It is good practice to change secrets periodically and use unique shared secrets for every webhook. Optionally, you can add two shared secrets to assist with zero downtime key rotation.
      - If you use one shared secret and rotate the key, downtime is possible until webhook destinations verifying the signature are updated.
      - If you add two shared secrets, the second secret is used for verification when rotating the first.
  2. (Optional) From the **Edit webhook** form, you can edit your **Authentication type.** You can select a new **Authentication type** or update information for the existing **Authentication type.**
    - **API key**—A simple token-based authentication mechanism that is used to authenticate requests. Enter the **API key** in the **API key** box.
    - **OAuth**—OAuth 2.0 is an authorization protocol that allows users (or applications) to grant access to or interact with data without sharing passwords. Enter the **Client ID,** **Client Secret,** and **Client token issuer URL.**
    - **No authentication**—If you select **No authentication,** you do not have to add additional details.
  3. (Optional) Select or deselect **Batching enabled.** When the checkbox is not selected, webhook events are sent to the webhook destination one-by-one. With batching enabled (checkbox selected), events are sent in small groups (known as a "batch"). This reduces the number of requests the webhook destination needs to handle and can improve performance. An event batch is sent when one of the following conditions is met:
    - **Event count**—When the maximum number of events are queued.
    - **Time window**—If the maximum number of events is not met, events are sent after a short waiting time.
7. Click **Update webhook** to confirm your changes. A confirmation email is sent to the email address used to create the
webhook. The webhook then enters a pending state while HPE GreenLake re-authenticates it by default. After it is authenticated, the webhook enters the active state.


## Testing a webhook

### **Prerequisites**

- You need **Read** permissions for **Automations Webhook.** To change
your permissions, talk to your HPE GreenLake cloud administrators.
Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)
- You must have registered at least one webhook.
- The webhook verification challenge request must be enabled. If the challenge request is disabled, the **Test** option is not available.


### **About this task**

If a webhook is not working correctly, testing it helps you determine the cause, view more information, and resolve the issue.

- The webhook **State** appears as warning, error, or disabled. To find
out more, see [Webhook States.](/docs/greenlake/services/event/public/webhooks#webhook-states)
- The **Recent Deliveries** log lists delivery failures.


### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that you want to test.
4. (Optional) Check under **Recent Deliveries** to see if recent webhook messages have not been sent. If so, click an item to view more information. This information helps you resolve any delivery failures. The following details are shown.
  - **Delivery**—The event type is a string value used to specify the occurrence that triggers a message to be sent to the webhook URL.
  - **ID**—The unique identifier of an event.
  - **Response**— The HTTPS status code. For more information, see [Webhook HTTPS status.](/docs/greenlake/services/event/public/webhooks#webhook-https-status-codes)
  - **Date**—The delivery date of the event message.
  - **Resource URI**—Unique identifier for the web resource.
  - **Request header**—Metadata about the request.
  - **Request body**—The data sent to the server during the request.
  - **Response header**—Metadata about the server response.
  - **Response body**—The data returned by the server. For 400—499 codes, the response body includes:
    - The HTTPS Status Code, for example 400 Bad Request.
    - The error code, which is a machine-friendly identifier of the error.
    - A message providing a readable description of the issue.
    - The debug ID, which is a unique identifier of the particular error instance.
5. To test the webhook, click **Actions.**
6. Click **Test.** The **Test webhook** panel opens and an HTTPS status code appears, indicating the result of the test. Use the information provided by the HTTPS status code to help resolve the error.
7. (Optional) To rerun the test, click **Retest.**
8. Click **Close.**


#### HTTPS response status code overview

| Response type | Code range | Description |
|  --- | --- | --- |
| Successful response | 200—299 | The test was successful. For example, a 200 response indicates that the test was successful and fully complete. |
| Client error response | 400—499 | There was an error on the client side. For example, a 401 indicates you are not correctly authenticated. |
| Server error response | 500—599 | There was an error on the service or server. For example, a 503 might mean that the server is unavailable. |


For more detailed information, see [Webhook HTTPS status codes.](/docs/greenlake/services/event/public/webhooks#webhook-https-status-codes) Use the information provided by the HTTPS status code to help resolve the error.

## Enabling or disabling a webhook

### **Prerequisites**

- You need **Update** permissions for **Automations Webhook.** To change
your permissions, talk to your HPE GreenLake cloud administrators.
Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)


### **About this task**

If a webhook is active, you can disable it. If the webhook is
disabled, you can enable it.

Disabling a webhook pauses all processing and notification activities.
The webhook remains on the **Webhooks** page and you can enable or unregister the webhook at any time.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that you want to enable or disable.
4. Click **Actions.**
5. Choose the appropriate action.
  - (Optional) To enable the webhook, click **Enable** and then click
**Enable webhook** from the dialog. By default, the webhook appears in a pending state while HPE GreenLake reauthenticates the webhook. After it is authenticated, the webhook enters the active state, and all processing and notification activities begin.
  - (Optional) To disable the webhook, click **Disable,** and then
click **Disable webhook** from the dialog. Disabling a webhook
pauses all processing and notification activities.
6. After you click **Enable webhook** or **Disable webhook,** you are
returned to the webhook details page.


## Unregistering a webhook

### **Prerequisites**

- You need **Delete** permissions for **Automations Webhook.** To change your permissions, talk to your HPE GreenLake cloud administrators. Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)
- You must have registered at least one webhook.


### **About this task**

Unregister a webhook when it is no longer required. Unregistering a webhook deletes it from the UI, and stops events from being sent to the webhook destination.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that you want to remove.
4. Click **Action.**
5. Click **Unregister webhook.**
6. From the **Unregister webhook** dialog, click **Unregister webhook** to remove the webhook. The webhook is removed from the UI, and events are no longer sent to its destination. An automated confirmation email is sent to the email address that created the webhook.


## Finding events on HPE GreenLake Developer Portal

### **About this task**

Events, and their associated **Event type,** are available from the [HPE GreenLake Developer Portal.](https://developer.greenlake.hpe.com/) The developer portal also contains event reference documentation.

### **Procedure**

1. Go to [HPE GreenLake Developer Portal.](https://developer.greenlake.hpe.com/)
2. Click **Services.**
3. Under **ON THIS PAGE**, click **Event catalog.** In the **Event catalog**, read about the event in the **Event description** column. The **API group** column contains a link to the event's reference documentation.
4. From the **Event catalog,** view the **event type** string and read the short **Event Description.** An example of an event type is `com.hpe.greenlake.audit-log.v1.logs.created`.
5. (Optional) To read the event reference documentation, click the link in the **API group** column. The event documentation describes the information returned by the event, and if available, explains the filtering options available for the event.
6. (Optional) To subscribe to an event, copy the **Event type,** and follow the steps in [Subscribing to an event.](#subscribing-to-an-event)


## Subscribing to an event

### **Prerequisites**

- You need **Create** permissions for **Automations Subscription**. To change your permissions, talk to your HPE GreenLake cloud administrators. Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)
- You must have registered at least one webhook.
- Review the documentation available on the HPE GreenLake Developer Portal to:
  - Review the [Event filtering](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/events/#event-filtering) documentation.
  - Browse the **Event catalog** and learn more about the available **API groups.**
  - Read the event reference documentation to understand the information returned by an event type.
  - Copy the **Event type.**


### **About this task**

The events you subscribe to define what triggers the webhook and what information is sent to the webhook destination. Steps 8 and 9 are only necessary if you want to specify event filters.

### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that you want to add an event subscription to.
4. Click **Subscribe to event.** The **Subscribe to event** panel appears.
5. From **Service Manager,** select the service the event belongs to. Scroll through the listing or use the search to find a specific service.
6. From **API group,** select the **API group** the event belongs to. Scroll through the listing or use the search to find a specific API group. API groups are listed on the **Services** page of HPE GreenLake Developer Portal.
7. From **Event type,** select the event type that will trigger the webhook. Scroll through the listing or use the search to find a specific event type. You can subscribe to a maximum of five event types per webhook, and these event types can come from one API group or multiple API groups.
8. (Optional) Click **Specify filters.** By specifying a filter, you choose to receive notifications only when the event applies to a subset. For example, you could specify to receive notifications only when an audit log relates to a specific user. The **Specify filters** dialog box opens.
9. (Optional) From the **Specify filters** dialog, under the event type name, enter your filter in the text box, and click **Apply Filters.** You can apply filters to any of the selected event types, but it is not required to apply a filter to every event type. The event type documentation on HPE GreenLake Developer Portal outlines the filterable properties available along with example filters that you can use or amend. HPE GreenLake Developer Portal also provides general technical documentation explaining how to construct event filters, see [Event filtering.](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/events/#event-filtering)
10. Click **Subscribe to event.** An automated confirmation email is sent to the email address used to create the webhook.


## Specifying event filters

### **Prerequisites**

- You need **Create** permissions to **Automations Subscription.** To change your permissions, talk to your HPE GreenLake cloud administrators. Find out more about [Roles & Permissions.](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html)
- You must have registered at least one webhook.


### **About this task**

Use filters to receive event notifications only when a specified
subset of an event type occurs. For example, when the event type
occurs for a particular user, status type, or when a value is greater
or lower than a threshold.

### **Procedure**

1. Go to the [Event catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/#event-catalog) on HPE GreenLake Developer Portal, and select an **API group** from the catalog.
2. Review the event documentation. The documentation will state if the event supports filtering. If the event does support filtering, the documentation will show:
  - The filterable event properties (resources or attributes) and the property's data type. In a filter expression, you compare a filterable event property with your choice of literal (a string, number, or date). The literal you choose must match the data type of the event property.
  - The comparison operators available. A comparison operator is a keyword or keywords used to compare two values or variables.
  - The available logical operators. A logical operator is a symbol or word used to connect two or more filter expressions.
  - Examples of filters.
3. Construct your filter. The basic syntax of a filter is `<property><comparison operation><literal>`. The following is a sample JSON of an event type. Filters apply only to data. Example of filters you could construct
here:
  - `name eq 'Jeremy'`—Return events when the name is equal to Jeremy. The property is a string, so literal must be in single quotation marks ('Jeremy').
  - `salary gte 50000`—Return events when salary is greater than or equal to 50000. The property is an integer so the literal in query is a whole number and not in quotation marks.
  - `country eq 'Brazil' and salary lt 80000`—Return events when the country is Brazil and the salary is less than 80000. This example uses the logical operator `and`, so events are returned whenever both filters to its left and right are true.
4. After constructing your filter, follow the steps in [Subscribing to an event.](#subscribing-to-an-event) When prompted, enter your filter in the **Specify filter** dialog box in the **Event type** text box.


If you subscribe to multiple events, you will have the choice to specify event filters for each chosen event type. Review the
documentation for each event type to ensure that your filter is valid. You do not have to specify a filter for every event type.

## Retrying failed event deliveries

### **About this task**

Events are sent to your chosen webhook URL as a message. If a message
fails to deliver to the webhook URL, you can manually retry the
message delivery.

### **Procedure**

1. On the **Manage Workspace** page, click **Automations** and then
click **Webhooks.**
2. Under **Webhooks,** select the webhook with the failed delivery you
want to retry.
3. View **Recent Deliveries**. In the **Response** column, failed
deliveries are denoted with a red icon and a non-200 HTTPS status
code. Events that can be retried have a **Retry** button.
4. (Optional) Click a record in the **Recent Deliveries** to review
detailed information.
5. In **Recent Deliveries**, click **Retry.**


The platform attempts to resend the message. You are returned to
the **Webhooks** page where, you can view the updated delivery status
of the event.

- If successful, the event displays a green icon and a 200 HTTPS status
code in **Response.**
- If unsuccessful, the event displays a red icon and a non-200 HTTPS
status in **Response.**


## Removing an event subscription

### **Prerequisites**

- You need **Delete** permissions for **Automations Subscriptions.** To
change your permissions, talk to your HPE GreenLake cloud
administrators. Find out more about [Roles & Permissions](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).
- The webhook must have at least one event subscription.


### **Procedure**

1. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace.**
2. On the **Manage Workspace** page, click **Automations** and then click **Webhooks.**
3. Click the webhook that has the event you want to remove.
4. Under **Event subscriptions,** find the event you want to remove and click **Delete.** The **Remove event subscription** dialog appears.
5. Click **Remove subscription.** The event subscription is removed.