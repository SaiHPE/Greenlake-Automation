---
title: "POST /compute-ops-mgmt/v1beta1/settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/settings-v1beta1/create_settings.md"
scraped_at: "2026-06-07T06:14:51.419612+00:00Z"
---

# Create a device setting

Create a device setting entry

Endpoint: POST /compute-ops-mgmt/v1beta1/settings
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `name` (string, required)
    The display name for the setting

  - `category` (string, required)
    The category to which the settings data applies.

The available server settings categories are:

| Category         | Purpose                                                            |
|------------------|--------------------------------------------------------------------|
| BIOS             | BIOS configuration                                                 |
| EXTERNAL_STORAGE | HPE GreenLake for Data Services Cloud Console (DSCC) configuration |
| FIRMWARE         | firmware configuration                                             |
| ILO              | iLO security configuration                                         |
| OS               | operating system                                                   |
| STORAGE          | internal storage configuration                                     |

The available OneView VM appliance settings categories are:

| Category                       | Purpose                                              |
|--------------------------------|------------------------------------------------------|
| OVE_APPLIANCE_SETTINGS_ANY     | appliance configuration                              |
| OVE_SERVER_TEMPLATES_VM        | server profile templates                             |
| OVE_SOFTWARE_VM                | OneView appliance software                           |

The available OneView Synergy appliance settings categories are:

| Category                       | Purpose                                              |
|--------------------------------|------------------------------------------------------|
| OVE_APPLIANCE_SETTINGS_ANY     | appliance configuration                              |
| OVE_APPLIANCE_SETTINGS_SYNERGY | synergy-specific appliance configuration             |
| OVE_SERVER_TEMPLATES_SYNERGY   | server profile templates                             |
| OVE_SOFTWARE_SYNERGY           | OneView Synergy appliance software                   |
    Enum: "BIOS", "EXTERNAL_STORAGE", "FIRMWARE", "ILO", "OS", "STORAGE", "OVE_APPLIANCE_SETTINGS_ANY", "OVE_APPLIANCE_SETTINGS_SYNERGY", "OVE_SERVER_TEMPLATES_SYNERGY", "OVE_SERVER_TEMPLATES_VM", "OVE_SOFTWARE_VM", "OVE_SOFTWARE_SYNERGY"

  - `description` (string,null)
    The description for the setting
    Example: "Firmware server setting"

  - `settings` (object)
    Configuration data corresponding to the specified category.

ILO settings are HPE-defined only. Adding a new ILO setting is not supported.

The following table shows the available schema keys for each settings category:

| Category         | Key(s)              | Details                                      |
|------------------|---------------------|----------------------------------------------|
| BIOS             | DEFAULT             | server BIOS configuration                    |
| EXTERNAL_STORAGE | DEFAULT             | HPE GreenLake for DSCC storage configuration |
| FIRMWARE         | GEN10, GEN11, GEN12 | Firmware for the specified platform(s)       |
| ILO              | DEFAULT             | iLO security configuration                   |
| OS               | DEFAULT             | Installed operating system                   |
| STORAGE          | DEFAULT             | Internal storage configuration               |
| OVE_*            | DEFAULT             | All OneView appliance settings categories    |

  - `settings.GEN10` (any)

  - `settings.GEN11` (any)

  - `settings.GEN12` (any)

  - `settings.DEFAULT` (any)

## Response 201 fields (application/json):

  - `id` (string)
    Primary identifier for the setting given by the system

  - `name` (string)
    The display name for the setting

  - `description` (string,null)
    The description for the setting

  - `category` (string)
    The category to which the settings data applies.

The available server settings categories are:
* BIOS - BIOS configuration
* EXTERNAL_STORAGE - storage configured in HPE GreenLake for Data Services Cloud Console (DSCC)
* FIRMWARE - firmware configuration
* ILO - iLO security configuration
* OS - operating system
* STORAGE - internal storage configuration

The available OneView VM appliance settings categories are:
* OVE_APPLIANCE_SETTINGS_ANY - appliance configuration
* OVE_SERVER_TEMPLATES_VM - server profile templates
* OVE_SOFTWARE_VM - OneView appliance software

The available OneView Synergy appliance settings categories are:
* OVE_APPLIANCE_SETTINGS_ANY - appliance configuration
* OVE_APPLIANCE_SETTINGS_SYNERGY - synergy-specific appliance configuration
* OVE_SERVER_TEMPLATES_SYNERGY - server profile templates
* OVE_SOFTWARE_SYNERGY - OneView Synergy appliance software
    Enum: "BIOS", "EXTERNAL_STORAGE", "FIRMWARE", "ILO", "OS", "STORAGE", "OVE_APPLIANCE_SETTINGS_ANY", "OVE_APPLIANCE_SETTINGS_SYNERGY", "OVE_SERVER_TEMPLATES_SYNERGY", "OVE_SERVER_TEMPLATES_VM", "OVE_SOFTWARE_VM", "OVE_SOFTWARE_SYNERGY"

  - `settings` (object)
    Configuration data corresponding to the specified category

  - `settings.GEN10` (any)

  - `settings.GEN11` (any)

  - `settings.GEN12` (any)

  - `settings.DEFAULT` (any)

  - `generation` (integer)
    Monotonically increasing update counter

  - `resourceUri` (string)
    URI to the settings itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/settings/a2fdaf7a-4933-4c47-bfe0-891f0a83dc6e"

  - `type` (string)
    Type of the resource

  - `createdAt` (string)
    Time of settings creation

  - `updatedAt` (string)
    Time of the last settings update

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 415 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


