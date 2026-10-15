---
title: "POST Service Offer Provision"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_external_events/webhooks/paths/service%20offer%20provision/post.md"
scraped_at: "2026-06-07T06:15:39.789337+00:00Z"
---

# Service offer provision event

A notification is sent when a service offer has been successfully provisioned in a region for a workspace.Event type—com.hpe.greenlake.service-provision.v1.serviceprovision.provisioned

Endpoint: POST Service Offer Provision
Version: 1.0.0

## Request fields (application/json):

  - `specversion` (string, required)
    The version of the CloudEvents specification the event adheres to.
    Example: 1

  - `id` (string, required)
    The unique identifier for the event.
    Example: "123e4567-e89b-12d3-a456-426614174000"

  - `source` (string, required)
    The source field is a URI reference that identifies the event producer.
    Example: "Compute"

  - `type` (string, required)
    The type of event.
    Example: "SERVICE_OFFER_PROVISION"

  - `subject` (string, required)

  - `data` (object, required)
    The event payload.

  - `data.ServiceProvisionID` (string)
    The unique identifier for the service provision.
    Example: "123e4567-e89b-12d3-a456-426614174000"

  - `data.ServiceOfferID` (string)
    The unique identifier for the service offer.
    Example: "123e4567-e89b-12d3-a456-426614174000"

  - `data.Region` (string)
    The region where the service provision should be provisioned.
    Example: "us-west"

  - `data.PlatformCustomerID` (string)
    The workspace ID of the customer.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.ApplicationCustomerID` (string)
    The workspace ID of the customer.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.UserID` (string)
    The username or email ID of the customer.
    Example: "abcd@hpe.com"

  - `data.ApplicationID` (string)
    The unique ID for an application.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.ApplicationInstanceID` (string)
    The unique ID for an application available in a particular region.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.Status` (string)
    The status of the service offer provisioning.
    Example: "PROVISIONED"

  - `data.AccountType` (string)
    The type of workspace associated with the account.
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `data.OperationalMode` (string)
    Indicates where the service offer can be viewed or provisioned.
    Enum: "DEFAULT", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `data.MspPlatformCustomerID` (string)
    The workspace ID of the MSP customer.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.MspServiceProvisionID` (string)
    The unique ID for the service provision provisioned in MSP workspace.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `data.MspApplicationCustomerID` (string)
    The unique ID for the application provisioned in a MSP workspace.
    Example: "23e4567-e89b-12d3-a456-426614174000"

  - `time` (string)
    The date and time the event occurred in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format.
    Example: "2023-10-01T12:00:00Z"

  - `dataschema` (string)
    A URI pointing to the data property schema.

  - `datacontenttype` (string)
    The encoding of the data in the data property in [RFC 2046](https://datatracker.ietf.org/doc/html/rfc2046) format.


