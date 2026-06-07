---
title: "API Versioning Basics | HPE GreenLake cloud"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides.md"
scraped_at: "2026-06-07T05:45:53.727418+00:00Z"
---

# Getting started

GreenLake cloud is a secure, cloud-based platform that allows you to view and control your hybrid cloud estate. GreenLake cloud APIs are a set of RESTful APIs that enable programmatic access to the diverse services offered on the platform. These APIs allow you to automate the management of resources, integrate with third-party tools, and enhance your workflow efficiency by interacting with the platform's infrastructure.

This page explains how developers can get started using the GreenLake Developer Portal.

The [GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us) has information for customer administrators and customer users about configuring and using the platform.

## Prerequisites for using GreenLake cloud APIs

To use the APIs, you need:

- An HPE account for GreenLake. See [Creating an HPE account.](/docs/greenlake/guides#creating-an-hpe-account)
- A Personal API client, including a client ID and secret key. See [Creating a Personal API client](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client) for details on this process.
- An access token to include in the headers of your API requests. See [Generating an access token](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token) for details on this process.
- Knowledge of RESTful API principles.
- A development environment with tools to make HTTP requests, such as cURL, Postman, or a programming language like Python.


## Creating an HPE account

Your HPE Account is the identity and access management infrastructure service for HPE customers and partners. It provides a consistent identity and access experience between all HPE applications with centralized user registration, profile management, authentication services (including MFA), and support for third party IdPs (Identity Providers) / SSO (Single Sign On).

1. To create an HPE account, click **Login.**
2. Click **Sign Up** at the bottom of the page. The **Create an HPE Account** page appears.
3. Provide the following account information:
  - **Email**—The email address for your account.
  - **Password**—A password for accessing your account.
  - **First Name/Last Name**—Your first and last name.
  - **Organization Information**—The name and address details of your business.
  - **Language**— Select your preferred language.
  - **Time Zone**— Select your time zone.
  - **Phone Number**— Enter your phone number.
4. Select your contact preferences.
5. Acknowledge the **HPE Terms of Use** by selecting the check box.
6. Click **Create Account.** A verification email sent message appears.
7. Verify your email address and activate your new HPE account using the link provided in the email.


### Signing in to GreenLake

After creating your HPE account, you can log in to the platform with the credentials that you provided when you created the account.

1. Go to [GreenLake.](https://common.cloud.hpe.com/)
2. Enter your login credentials. The Welcome to GreenLake page appears. Here, you can create a new workspace or sign in to an existing workspace.


If you need assistance to manage your HPE account, including recovering forgotten passwords, see [HPE Account Help.](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00003196en_us&page=GUID-85481EA8-668D-4CAB-A768-41C9DEABE756.html)

## Roles and permissions hierarchy

Some content on the portal can be made completely private, or it can be visible to a restricted group (for example: partners, developers, or administrators).

User roles allow users to access the restricted content. The portal comes with the following roles:

1. Public
2. Partner


### Public

1. Guest—Every visitor will have this role with a single permission to read all public content on the portal.
2. Authenticated-User—Every logged in user will have this role.


### Partner

Users with the Partner role can access restricted content that is specific to a Partner.

## Discover and try the APIs

To find APIs, browse the service catalog or use the search function.

1. Log in to the GreenLake Developer Portal.
2. There are three ways to find APIs:
  - Click **Services** > and select a service from the navigation menu.
  - Enter the name of an API into the search. The results for your search appear beneath the search bar.
  - Navigate to **Service > Overview** to view a catalog of available APIs along with a description.
3. Click **API reference** from the service documentation and navigate to an API request. Use the **Try It** option to experiment with the APIs directly within the platform. This tool allows you to make API calls to understand their behavior and validate their responses.


Try It
The **Try It** tool interacts with the actual environment and not a separate sandbox, so any changes you make will affect your production data. It is advisable to use the tool with caution and verify the impact of the changes in a controlled manner before integrating them into your live applications. Always test with non-critical or sample data to mitigate potential risks.

## Next steps

Find out how to get [authenticated](/docs/greenlake/guides/public/authentication/authentication) and [browse the API catalog.](/docs/greenlake/services)