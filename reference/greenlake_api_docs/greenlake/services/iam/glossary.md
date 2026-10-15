---
title: "IAM Glossary | HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/glossary.md"
scraped_at: "2026-06-07T06:13:19.841855+00:00Z"
---

# IAM, or Identity and Access Management Glossary

IAM stands for Identity and Access Management, which refers to a set of policies, technologies, and processes designed to manage digital identities and control access to resources in an organization's IT environment. IAM systems help ensure that users are granted appropriate access rights based on their roles and responsibilities, while minimizing the risk of unauthorized access or data breaches.

This glossary provides an overview of various IAM terms. It does not represent the native feature set of HPE GreenLake.

## Shared Responsibility Model

IAM is a shared responsibility between you and HPE. Here’s a brief overview of our joint responsibilities:

### Our Responsibilities

- **Foundational IAM Controls:** We provide base IAM features for user account management and role assignments.


### Your Responsibilities as Administrators

- **User Management:** You should manage user access responsibly and train your team on security best practices.
- **Custom IAM Configuration:** You're responsible for configuring the IAM controls to suit your organization’s specific needs.


Remember, while we lay the foundation for security and IAM, you play a crucial role in customizing and managing these controls to fit your organization’s unique requirements.

## Basics

In the context of HPE GreenLake services, authentication and authorization refer to the process by which the service validates the identity of all API call subjects using a reliable and trusted identity source. Following this verification, the service assesses the permissions or entitlements of the subject against the HPE GreenLake Authorization system before granting access to the requested services.

![Authentication & Authorization Illusrration](/assets/authn-authz-illustration.43400f543fda17f8b29f1a0b15a5b35cb1f23b24fdd220ab9b20a4e31ec22e79.3bd884bd.png)

## Authentication

Authentication is the process of verifying the identity of a user, device, or system. This typically involves presenting credentials, such as a username and password, that are checked against a database of known identities. Authentication aims to ensure that only legitimate users or systems gain access to protected resources or services.

## Authorization

Authorization is the process of granting or denying access to resources based on the authenticated user's identity and permissions. It involves checking whether a user has the appropriate permissions to access a specific resource or perform a particular action. Authorization helps enforce security by restricting access to sensitive information and resources to authorized users only.

Some protocols like Oauth2 cross the boundary between authentication and authorization.

## Principal

A principal is an entity that can be authenticated and authorized to access resources. a principal can be a user, a device, an API client, or a system. Principals are essential components of access control, as they are used to determine who can access what resources and under what conditions.

- Learn more about [HPE GreenLake Identity Principals](/docs/greenlake/services/iam/iam-principals-subjects)


## Subject

a subject is a representation of a principal, which is used to enforce access control policies. Subjects can be used to define permissions, roles, and other attributes that determine what a principal can access. They are essential components of identity management, as they are used to manage and control access to resources based on the identity and privileges of the principal.

## Directory service / Identity Directory

A directory service is a centralized database that stores and manages user, group, and API client information, serving as the backbone for managing access to resources within an organization. Common examples of directory services include Active Directory, LDAP, Okta, and Keycloak. These services provide a unified and consistent way to store and manage user attributes, group memberships, and access controls, facilitating the implementation of identity and access management (IAM) policies and simplifying the administration of users and permissions.

## User

A user is an individual who can access an organization's resources and perform actions based on their assigned permissions. Users typically have unique identities, such as usernames or email addresses, and are granted access to resources through roles, groups, or individual permissions.

## User Group

A group is a collection of users that share a common set of permissions or access rights. Groups are used to simplify access management by allowing administrators to assign permissions to multiple users at once, based on their membership in the group. This makes it easier to manage and maintain consistent access controls across an organization.

## API Client

An API client is a software application or service that communicates with an API (Application Programming Interface) to access and consume data or functionality provided by a remote system or application. API clients are typically used to enable third-party applications or services to access IAM functionality, such as user authentication, authorization, and access management.

## Credential management

The process of managing user authentication credentials, such as usernames, passwords, and security tokens. Credential management involves the creation, storage, and updating of user credentials, as well as the enforcement of policies and controls to ensure their security and integrity. Credential management is an essential component of IAM, as it helps protect user identities and ensure the confidentiality, integrity, and availability of resources.

## Passwordless

"Passwordless" refers to a system or method of authentication that allows users to access their accounts or systems without using traditional passwords. Instead of relying on a password, passwordless authentication utilizes alternative and often more secure means to verify a user's identity. The goal of passwordless authentication is to enhance security, reduce the risk of password-related vulnerabilities (e.g., password leaks, weak passwords, password reuse), and improve the user experience.

There are several methods of passwordless authentication, including:

- Biometric authentication: This involves using unique biological characteristics, such as fingerprints, facial recognition, or iris scans, to verify a user's identity.
- Two-factor authentication (2FA): Passwordless 2FA involves combining something the user knows (e.g., a PIN or a username) with something the user possesses (e.g., a smartphone or a hardware token) to authenticate.
- One-time passwords (OTPs): Users receive temporary codes through email, SMS, or authenticator apps that they use to log in, eliminating the need for a static password.
- Public-key cryptography: This method uses public and private key pairs for authentication, with the private key being securely stored on the user's device.
- FIDO (Fast Identity Online): FIDO standards offer passwordless authentication using biometrics, security keys, or other external devices to verify user identities.


## Identity lifecycle management

Identity lifecycle management refers to the continuous process of managing the creation, modification, and deletion of user identities within an organization's IT environment. This process helps ensure that users have the appropriate access rights throughout their association with the organization, from onboarding to offboarding. Effective identity lifecycle management involves regularly updating and reviewing user access rights, roles, and permissions to maintain security and compliance with internal and external regulations.

### Identity Proofing

The process of verifying the identity of a user, often as part of the user registration or onboarding process. Identity proofing may involve the collection and validation of various personal information, such as name, date of birth, social security number, or government-issued ID, to confirm that the user is who they claim to be. This process helps ensure the accuracy and integrity of the user's digital identity and reduces the risk of identity fraud or impersonation.

### User Provisioning

User provisioning is the process of creating, updating, and managing user accounts and their associated permissions within an organization's environment. This process includes defining user attributes, assigning roles, and granting access to resources based on the user's job function and responsibilities.

#### Just-In-Time (JIT) Provisioning

A method of user provisioning that automatically creates and manages user accounts on-demand, as users attempt to access resources for the first time. JIT provisioning reduces the need for manual account creation and management, and helps ensure that users have access to the resources they need when they need them.

#### Joiners, Movers, and Leavers

Terms used in Identity and Access Management (IAM) and Human Resources (HR) to describe different stages in an employee's lifecycle within an organization. These stages are crucial for managing user access to resources, ensuring security, and maintaining compliance with organizational policies.

##### Joiners

Joiners are new employees who have recently joined the organization. During the onboarding process, joiners are granted access to the necessary resources, systems, and applications required for their job role.

##### Movers

Movers are existing employees who have changed roles or responsibilities within the organization. This change may result from a promotion, transfer, or new project assignment. When an employee moves to a new role, their access rights must be updated to reflect their new responsibilities. This process may involve modifying their permissions, adding or removing access to specific resources, and updating their membership in user groups.

##### Leavers

Leavers are employees who have left the organization, either through resignation, retirement, or termination. When an employee leaves the organization, it is essential to promptly revoke their access to all resources, systems, and applications to minimize security risks. The offboarding process typically includes disabling or deleting user accounts, revoking access to resources, and recovering any company-owned devices or assets.

## System for Cross-domain Identity Management (SCIM)

A standard protocol used for automating the exchange of user identity and access information between different systems or domains. SCIM is designed to simplify the management of digital identities and reduce the need for manual provisioning and deprovisioning of users across multiple systems. It enables organizations to automate user onboarding and offboarding, enforce consistent access policies, and reduce the risk of errors and inconsistencies. SCIM is widely used in IAM solutions, especially in cloud-based environments where multiple applications and services need to share identity information. SCIM supports both RESTful and HTTP-based APIs for exchanging identity information, and defines a common schema and set of operations for managing user identities, groups, and access rights.

## User Sign-on

Sign-on is the process by which a user gains access to a computer system, network, or application by providing valid credentials, typically a username and password combination. The sign-on process is a crucial component of Identity and Access Management (IAM), as it helps to verify the user's identity and ensure that only authorized individuals can access protected resources. Sign-on is often the first step in the authentication and authorization process, which is followed by granting or denying access to specific resources based on the user's assigned permissions and roles. Additionally, sign-on mechanisms can be enhanced with various security measures, such as multi-factor authentication (MFA) or single sign-on (SSO), to provide an extra layer of protection against unauthorized access or potential security threats.

### Session

A session is a period of time during which a user is authenticated and authorized to access resources. A session begins when a user logs in and ends when the user logs out or when the session expires. Sessions are used to track user activity and enforce access control policies. They can be used to monitor user behavior and detect security threats, such as unauthorized access attempts.

### Multi-Factor Authentication (MFA)

An authentication method that requires users to provide two or more independent factors to verify their identity. MFA typically combines something the user knows (e.g., password), something the user has (e.g., smartphone), and/or something the user is (e.g., fingerprint). MFA enhances security by making it more difficult for unauthorized individuals to access accounts, even if they have obtained the user's password.

## Single sign-on (SSO)

A user authentication process that allows users to access multiple applications, services, or systems with a single set of credentials. Single Sign-On simplifies the user experience by eliminating the need for users to remember and enter multiple sets of credentials for different resources. SSO can be implemented using various protocols, such as SAML, OAuth, and OpenID Connect.

### Identity federation / Brokering

The process of linking identities across different systems or organizations to provide a seamless user experience and simplify management. The process involves establishing trust between two or more organizations to enable users to access resources across different systems or domains.

### Identity provider (IdP)

An entity or system that creates, maintains, and manages digital identities, as well as authenticates users for access to resources. Identity providers are responsible for verifying the identity of users and providing the necessary information to relying parties, such as applications or services, to enable them to make access control decisions. Common identity providers include Microsoft Azure Active Directory, Google Identity Platform, Okta, and Auth0.

### Protocol

A protocol is a set of rules and guidelines for communicating and exchanging data between different systems or entities. IAM protocols define standardized methods for user authentication, authorization, and access management, and enable different applications and services to interoperate and share identity information. Some of the commonly used IAM protocols include SAML (Security Assertion Markup Language), OAuth (Open Authorization), OpenID Connect, SCIM (System for Cross-domain Identity Management), and LDAP (Lightweight Directory Access Protocol). These protocols provide a common language and framework for implementing IAM solutions, and help ensure interoperability and compatibility across different systems and applications.

#### SAML

Stands for "Security Assertion Markup Language," which is an XML-based protocol used for exchanging authentication and authorization data between different systems.

#### OAuth 2.0

An authorization protocol used to grant third-party applications access to protected resources, without sharing the user's credentials. OAuth 2.0 is commonly used in modern IAM systems to allow users to grant access to their accounts or resources, such as social media profiles or cloud-based storage, to third-party applications or services. OAuth 2.0 is based on a token-based authorization mechanism, in which an access token is issued by an authorization server to the third-party application after the user has granted permission. This token is then used by the application to access the protected resource on behalf of the user, without the need for the user to share their credentials with the third-party application.

#### OpenID Connect (OIDC)

A protocol built on top of the OAuth 2.0 framework, used for authentication and authorization purposes. OIDC allows for the exchange of identity information between parties, such as an identity provider and a relying party (e.g., a web application). It is designed to provide single sign-on (SSO) capabilities, as well as support for user authentication and authorization using JSON Web Tokens (JWTs). OIDC is widely used in modern IAM solutions and is supported by many popular identity providers and service providers.

#### Tokens

- **JWT (JSON Web Token):** JWT stands for JSON Web Token, which is a compact, URL-safe, and self-contained way of securely transmitting information between parties as a JSON object. JWTs are often used for authentication and authorization purposes, especially in web applications and APIs. JWTs are useful in scenarios where you need to transmit information securely between parties, as they can be digitally signed or encrypted. One common use case is during user authentication, where a server generates a JWT after successful authentication and returns it to the client. The client can then use the JWT to access protected resources by including it in the request's authorization header.
- **OAuth Access Token:** An OAuth Access Token is a credential issued by an authorization server in response to a client application's request for access to a resource owner's protected resources. The token represents the client's granted permissions and allows the client to access the specified resources on behalf of the resource owner. Access tokens typically have a limited lifespan and are used in the header of API requests for authentication and authorization.
- **ID Token:** An ID Token is a JSON Web Token (JWT) provided by an identity provider as part of an OpenID Connect (OIDC) authentication flow. It contains user profile information and is used to verify the user's identity. The ID Token includes claims about the user, such as their username, email address, and other relevant details. Clients can decode and validate the ID Token to authenticate the user and obtain their profile information for use within an application.
- **Refresh Token:** A Refresh Token is a long-lived credential issued by the authorization server, used to obtain new access tokens when the current access token expires. Refresh tokens allow client applications to maintain access to protected resources without requiring the resource owner to re-authenticate. When the client detects an expired access token, it uses the refresh token to request a new access token, allowing for a seamless user experience and continued access to resources.
- **Personal Access Token (PAT):** A Personal Access Token (PAT) is a user-specific credential used to authenticate with an application or service, typically for API access or script automation. Unlike session-based tokens, PATs do not expire after a set time and are often used for situations where long-term access is required. PATs are particularly useful for developers or administrators who need to interact with an API or automate tasks without using their own password.
- **Bearer Token:** A Bearer Token is a type of access token that provides the bearer, or holder of the token, with access to a protected resource. It is a simple, lightweight method for authorizing API requests, and it is included in the authorization header of the HTTP request. Bearer tokens are often used in RESTful APIs and are typically generated by an authorization server as part of an OAuth 2.0 or OpenID Connect flow.


## Access Control

**Access control** is the mechanism for enforcing authorization policies that define who can access what resources. It's the process of limiting access to resources based on the identity and permissions of the user or system requesting access.

### Least Privilege

**Least Privilege** is a security principle stating that users should only have the minimum level of access necessary to perform their job functions. By limiting user access to only what is required, organizations can reduce the risk of unauthorized access or data breaches. Implementing this principle involves regularly reviewing and adjusting user permissions, and using role-based access control or other access control mechanisms.

### Zero Trust

**Zero Trust** is a security model that assumes all network traffic, users, devices, and resources are potentially compromised and should not be trusted by default. It requires continuous verification of the identity and security posture of users, devices, and resources before granting access, regardless of location. Technologies like multi-factor authentication, micro-segmentation, and real-time risk assessments are employed in Zero Trust architectures.

### Role-based access control (RBAC)

An approach to access control that assigns permissions to users based on their roles within an organization. Roles are defined based on job functions or responsibilities, and permissions are assigned to roles rather than individual users. This approach simplifies the management of permissions, as changes can be made to roles without affecting individual user accounts.

#### Role

A **role** is a predefined set of permissions that define what actions a user or system can perform within an organization. Assigned based on job responsibilities, roles streamline the process of granting and managing access to resources.

### Resource

A **resource** refers to any asset or entity requiring authentication and authorization for access. This includes both physical assets (like buildings or equipment) and digital assets (like files, databases, applications, and services). IAM systems manage access to these resources by assigning permissions based on roles, responsibilities, and privileges.

### Permission

**Permission** is a right granted to a user or system to perform a specific action or access a resource. Defined at a granular level, permissions can form roles or policies applied to users or groups. Examples include read, write, execute, create, delete, modify, and administer. IAM systems help manage these permissions.

### Scope

**Scope** in IAM defines the precise boundary or target area of a permission or policy, determining exactly which resources an action applies to. It represents the set of resources that can be addressed using a well-defined syntax. Scope refers to the range of access that a user or application is authorized to have for particular resources. This access boundary is defined by various factors, including the user's role, permissions, and privileges, as well as the sensitivity and criticality of the resources involved.

#### Scope - HPE GreenLake Resource Notation (GRN)

The HPE GreenLake Resource Notation (GRN) is the standardized, URI-compatible syntax (`grn:glp/workspaces/...`) that enables the precise definition of this scope. It uniquely identifies resources through a clear hierarchy (platform, workspace, region, provider, resource), allowing you to specify the exact boundary of an action.

- Learn more in the [GreenLake Resource Notation - GRN Specification](/docs/greenlake/services/iam/greenlake-resource-notation)


#### Scope Group

**Scope Group** in IAM provides a management tool to put multiple scopes together and used in Role assignment as an unit. Scope Group does not support nested scope group.

### Context

Context refers to additional information that informs a policy decision. Context can include factors such as the user's location, device type, time of day, or network connection. Contextual information can be used to enforce more granular and dynamic access controls, based on the specific circumstances of each access request.

### Permission boundaries

Permission boundaries are limits placed on the access permissions of a subject or principal. These limits help prevent unauthorized access to resources and protect sensitive data. Permission boundaries can be set based on attributes such as job role, organizational hierarchy, or project team membership. They help ensure that users have access only to the resources they need to perform their job functions and nothing more.

### Effective permissions

Effective permissions are the permissions that a principal has based on its roles, permissions, and any applicable policies. Effective permissions take into account permission boundaries, and any restrictions or allowances set by the policies. Effective permissions are used to enforce access control and ensure that users have the appropriate level of access to resources.

### Privileged Access Management (PAM)

**Privileged Access Management (PAM)** involves managing and controlling an individual's access to digital resources, such as applications, services, and data. PAM ensures users have appropriate access levels based on their needs and responsibilities, while minimizing unauthorized access risks.

### Access Request

**Access request** is the process of requesting access to a resource that the user does not currently have permission to access.

### Access Review

**Access review** involves reviewing and verifying that users still require access to the resources they have been granted.

## Compliance

The process of ensuring that an organization's IAM practices adhere to relevant laws, regulations, and standards. In a general context, refers to the process of adhering to a set of rules, regulations, standards, or laws that are applicable to an organization or industry. In the context of information security and Identity and Access Management (IAM), compliance involves ensuring that an organization's practices, policies, and procedures align with relevant legal requirements, industry standards, and internal guidelines.

## Governance

In a general context, refers to the process of establishing and implementing policies, procedures, and frameworks to effectively manage and control an organization or system. In the context of Identity and Access Management (IAM), governance involves overseeing the use of digital identities and their access to resources across an organization. This includes setting standards, guidelines, and best practices for managing identities and access, as well as defining roles and responsibilities for IAM stakeholders, such as administrators, users, and auditors.

### Identity Governance and Administration (IGA)

A framework for managing digital identities and their access to resources across an organization. IGA combines identity management, access management, and compliance management to ensure that users have the right access to the right resources at the right time, and that access is granted and revoked in a timely and auditable manner.

### Policy

A policy is a set of rules that define how resources can be accessed and used within an organization. Policies help establish the acceptable use of resources, provide guidelines for users, and set constraints on the operations of systems and applications. They are often created to enforce compliance with laws, regulations, and industry standards.