---
title: "HPE GreenLake for User Management developer guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/guide.md"
scraped_at: "2026-06-07T06:13:27.709291+00:00Z"
---

# HPE GreenLake for User Management developer guide

The examples in this guide help you use the User Management APIs.

## Prerequisites

### Endpoints

Endpoints are the host URLs to which you will submit your API requests. To access the User Management APIs, use the unified API:

- `https://global.api.greenlake.hpe.com`


### URIs

Unique Resource Identifiers (URIs) are used to identify a server or resource used within the users and workspaces. A URI is a full API path ending in an identification number. For example:

- `/identity/v1/users/{userId}`


### Generating tokens

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


## Making It All Work

The HPE GreenLake for User Management APIs allow you to:

- Find information on existing users.
- Invite a user to a workspace.
- Find information on a single-user.
- Delete a user from a workspace.
- Update user preferences.


### Obtain information on users in a workspace

To retrieve a list of users and their related information in the workspace, use the following request GET request:


```curl
GET https://global.api.greenlake.hpe.com/identity/v1/users
```

The information returned for each user is the following:

- User ID, username, status, and login status
- Pagination information: offset, count, items, and total


Sample response:


```json
{
"offset": 0,
    "count": 2,
    "total": 2,
    "items": [
        {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "type": "string",
            "generation": 0,
            "createdAt": "2019-08-24T14:15:22Z",
            "updatedAt": "2019-08-24T14:15:22Z",
            "username": "user@example.com",
            "userStatus": "UNVERIFIED",
            "lastLogin": "2019-08-24T14:15:22Z"
        },
        {
            "id": "523a65de-2266-5012-bfeb-53cdddd16f08",
            "type": "string",
            "generation": 0,
            "createdAt": "2020-08-24T14:15:22Z",
            "updatedAt": "2021-08-24T14:15:22Z",
            "username": "user2@example.com",
            "userStatus": "VERIFIED",
            "lastLogin": "2019-08-24T14:15:22Z"
        }
    ]
}
```

### Obtain information on a single user

To retrieve information on a specific user, make the following request GET request specifying the user ID:


```curl
GET https://global.api.greenlake.hpe.com/identity/v1/users/<id>
```

### Inviting a user to the workspace

To invite a user to the same workspace where you created the access token, submit a POST request:


```curl
POST https://global.api.greenlake.hpe.com/identity/v1/users
```

Payload:


```json
{
  "email": "string",
  "sendWelcomeEmail": true
}
```

In the request body, specify the user's email address and whether to send a welcome or not.

A valid response generates a location header, and the response payload returns a user invited message.

### Disassociating a user from the workspace

To delete a user from a workspace, submit the following request specifying the path of the user ID.

To find a user ID, see [Obtain information on users in a workspace](#obtain-information-on-users-in-a-workspace).


```curl
DELETE https://global.api.greenlake.hpe.com/identity/v1/users/<id>
```

### Updating your user preferences

To change your user preferences, use the following PUT request:


```curl
PUT https://global.api.greenlake.hpe.com/identity/v1/users/<id>
```

Payload:


```json
{
    "language": "en",
    "idleTimeout": 1800
}
```

## Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET or PUT action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

### Filtering example

In this example of filtering, the query's resources are limited to results for the specified username. Within the filter, the separator is a space.


```curl
GET <URI>?filter=username eq 'user@example.com'
```

### Filtering on a single property


```curl
filter = <propertyName> <comparison operation> <literal>
```

`GET /identity/v1/users?filter=username eq 'user@example.com'`

**Property** is the name of an attribute in the requested resource type, for example, username. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

Examples of the possible filter values:

| **Filter** | **Example** | **Description** |
|  --- | --- | --- |
| ID | `id eq '7600415a-8876-5722-9f3c-b0fd11112283'` | A user is returned when their user ID that matches the given string. |
| Username | `username eq 'user@example.com'` | A user is returned when their email address matches the given string. |
| userStatus | `userStatus ne 'UNVERIFIED'` | Returns a list of users whose status is not unverified are retrieved. |
| createdAt | `createdAt gt '2020-09-21T14:19:09.769747'` | Retrieves a list of users created after the specified date time. |
| updatedAt | `updatedAt gt '2020-09-21T14:19:09.769747'` | Retrieves a list of users updated after the specified date time. |
| lastLogin | `lastLogin lt '2020-09-21T14:19:09.769747'` | Returns a list of users whose last login was before the specified date time. |


**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `username eq 'user@example.com'` | The username is equal to the provided string (email address). |
| ne | `createdAt ne '2020-09-21T14:19:09.769747’` | createdAt is not equal to the provided date time. |
| gt | `createdAt gt '2020-09-21T14:19:09.769747’` | createdAt is greater than the provided date time |
| ge | `createdAt ge '2020-09-21T14:19:09.769747` | createdAt is greater than or equal to the provided date time. |
| lt | `createdAt lt '2020-09-21T14:19:09.769747` | createdAt is less than the provided date time. |
| le | `createdAt le '2020-09-21T14:19:09.769747` | createdAt is less than or equal to the provided date time. |
| in | `createdAt in ['2020-09-21T14:19:09.769747','2020-09-21T14:19:09.769747']` | createdAt must equal one of the literals provided literals, in this example, date times. |


Special case operations:

| Operation | Example | Description |
|  --- | --- | --- |
| in | `2020 in createdAt` | Retrieves a user or workspace created on a date that contains the value 2020. |


A **Function** can be used to extract information. A function is a block of reusable code that performs a single action. You pass a value into the function, which returns a value. These functions can be used in a filter:

| Function | Example | Description |
|  --- | --- | --- |
| Contains | `contains(id, '20')` | Checks if a string value is inside the source string, in this example, `'20'`. Returns boolean true or false as appropriate. |
| EndsWith | `endswith(userName, 'test')` | Assesses if a string value ends with the characters of a specified string, in this example, `'test'`. Returns boolean true or false as appropriate. |
| StartsWith | `startswith(wuserName, 'test')` | Assesses if a string value begins with the characters of a specified string, in this example, `'test'`. Returns boolean true or false as appropriate. |


A **literal**, for example, `true`, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**: Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**: -100, -1, 0, 1, 100
- **Decimal**: -3.14, -2.71, 2.71, 3.14
- **Timestamp**: 2019-10-12T07:20:50.52934852Z. The timestamp format is [RFC3339]
- **Boolean**: true, false
- **Null**: null. Null is equal to itself and nothing else. Null is not greater or less than anything.


### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and`, for example:

**Require both (and):** `createdAt eq '2020-09-21T14:19:09.769747' and workspaceName eq 'test'`

### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).