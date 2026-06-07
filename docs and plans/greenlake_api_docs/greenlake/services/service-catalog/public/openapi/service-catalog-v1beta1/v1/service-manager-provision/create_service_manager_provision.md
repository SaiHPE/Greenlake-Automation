---
title: "POST /service-catalog/v1/service-manager-provisions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1/service-manager-provision/create_service_manager_provision.md"
scraped_at: "2026-06-07T06:15:40.227686+00:00Z"
---

# Provision a service manager in a given region

Provision a service manager deployed in a region. Provisioning of a service manager is an async process and you can monitor the  provisionStatus field to know the current status.

Endpoint: POST /service-catalog/v1/service-manager-provisions
Version: v1
Security: bearerAuth

## Request fields (application/json):

  - `serviceManagerId` (string, required)
    The unique identifier of the service manager.

  - `region` (string, required)
    HPE GreenLake platform defined region code.

## Response 201 fields (application/json):

  - `id` (string, required)

  - `resourceUri` (string, required)
    URI to the service manager provision resource

  - `serviceManager` (object, required)
    A reference to a service manager resource.

  - `serviceManager.resourceUri` (string)
    URI to the service manager resource

  - `region` (string, required)

  - `createdBy` (string, required)
    The HPE GreenLake platform username that provisioned the service manager.

  - `generation` (integer, required)
    Monotonically increasing update

  - `type` (string, required)
    Type of resource

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.


