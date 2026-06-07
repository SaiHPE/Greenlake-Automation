---
title: "HPE GreenLake for User Management glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/glossary.md"
scraped_at: "2026-06-07T05:46:11.040402+00:00Z"
---

# HPE GreenLake for User Management glossary

## Terms

### Joiners, movers, and leavers

Terms used in identity and access management (IAM) and human resources (HR) to describe different stages in an employee's lifecycle within an organization. These stages are crucial for managing user access to resources, ensuring security, and maintaining compliance with organizational policies.

#### Joiners

Joiners are new employees who have recently joined the organization. During the onboarding process, joiners are granted access to the necessary resources, systems, and applications required for their job role.

#### Movers

Movers are existing employees who have changed roles or responsibilities within the organization. This change may result from a promotion, transfer, or new project assignment. When an employee moves to a new role, their access rights must be updated to reflect their new responsibilities. This process may involve modifying their permissions, adding or removing access to specific resources, and updating their membership in user groups.

#### Leavers

Leavers are employees who have left the organization, either through resignation, retirement, or termination. When an employee leaves the organization, it is essential to promptly revoke their access to all resources, systems, and applications to minimize security risks. The offboarding process typically includes disabling or deleting user accounts, revoking access to resources, and recovering any company-owned devices or assets.

### Identity lifecycle management

Identity lifecycle management refers to the continuous process of managing the creation, modification, and deletion of user identities within an organization's IT environment. This process helps ensure that users have the appropriate access rights throughout their association with the organization, from onboarding to offboarding. Effective identity lifecycle management involves regularly updating and reviewing user access rights, roles, and permissions to maintain security and compliance with internal and external regulations.

### Identity proofing

The process of verifying the identity of a user, often as part of the user registration or onboarding process. Identity proofing may involve the collection and validation of various personal information, such as name, date of birth, social security number, or government-issued ID, to confirm that the user is who they claim to be. This process helps ensure the accuracy and integrity of the user's digital identity and reduces the risk of identity fraud or impersonation.

### Language preferences

The `PUT /identity/vi/users/{id}` API call can change a user’s preferred language by entering a language code in the response body, for example, `"language": "fr"` changes the language preference to French.

English is the default.

| Language code | Language |
|  --- | --- |
| `"br"` | Brazilian Portuguese |
| `"cn"` | Chinese |
| `"en"` | English |
| `"fr"` | French |
| `"de"` | German |
| `"it"` | Italian |
| `"jp"` | Japanese |
| `"ko"` | Korean |
| `"ru"` | Russian |
| `"es"` | Spanish |


### User provisioning

User provisioning is the process of creating, updating, and managing user accounts and their associated permissions within an organization's environment. This process includes defining user attributes, assigning roles, and granting access to resources based on the user's job function and responsibilities.

#### Just-in-time (JIT) provisioning

A method of user provisioning that automatically creates and manages user accounts on-demand, as users attempt to access resources for the first time. JIT provisioning reduces the need for manual account creation and management, and helps ensure that users have access to the resources they need when they need them.

### User status

`userStatus` is a filterable in the GET a user and GET users API call that refers to the onboarding status of the user. For example, a verified user will have a `"VERIFIED”` userStatus. The user statuses available are:

* `"BLOCKED"`
* `"DELETE_IN_PROGRESS"`
* `"DELETED"`
* `"SUSPENDED"`
* `"UNVERIFIED"`
* `"VERIFIED"`