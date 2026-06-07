---
title: "HPE GreenLake APIs for Device Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi.md"
scraped_at: "2026-06-07T06:13:36.531355+00:00Z"
---

# HPE GreenLake APIs for Device Management

With the HPE GreenLake APIs for Device Management you can view, manage, and onboard devices in your workspace. The API allows you to invoke any operation or task that is available through the HPE GreenLake edge-to-cloud platform user interface.

Version: latest
License: HPE End User License Agreement

## Servers

Url hostname
```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake APIs for Device Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi.yaml)

## Devices - v2beta1

### Add devices

 - [POST /devices/v2beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v2beta1/postdevicesv2beta1.md): Add one or more devices to a workspace. This API endpoint provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to invoke to  fetch the progress of the device addition task. For details about the  status fetch URL, refer to the API endpoint Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to call this API endpoint. Rate limits are enforced, and 25 requests per minute are supported per workspace. The API endpoint returns 429 if this threshold is breached.

### Update devices

 - [PATCH /devices/v2beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v2beta1/patchdevicesv2beta1.md): Update devices by passing one or more device IDs.  The API supports Device operations such as:
Assigning and unassigning devices to and from a service. Adding, updating and removing tags to devices. Archiving and un-archiving the devices.   The API endpoint supports subscription operations of applying and removing subscriptions to and from devices.
To remove an application, set the id under application to null and region to null. Set an empty array to the attribute subscription to remove a subscription. For each tag provided in the request body: Tags are created and inserted into the specified devices if the provided tags do not map to null and are not already present. Tags are updated with the provided if the provided tag key is already present in a device, but the provided value differs from the existing value. Tags are removed from devices when a tag key is mapped to a null tag value. The tags are removed from any devices with a matching tag with the same key. The endpoint only supports either a device or a subscription operation per API call. For example, you cannot assign devices to an application and assign subscriptions to devices in a single API call. You can achieve this with two separate API calls. However, a single API call can perform device operations together; for example, assigning an application and adding tags can be performed. The archive device operation is incompatible with any other device operation in the same API call. For example, you cannot remove an application and archive a device using the same API call. This is an asynchronous API endpoint and it returns the 202 Accepted response code and a Location header containing the URI of the asynchronous operation that can be used to track progress. For details about the status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to initiate this API call. Rate limits are enforced, and 20 requests per minute are supported per workspace. The API returns 429 if this threshold is breached.

## Devices - v1

### Get devices managed in a workspace

 - [GET /devices/v1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1/getdevicesv1.md): With this API, you can: Retrieve a list of devices managed in a workspace. Filter  devices based on conditional expressions.NOTE: You need view  permissions for Devices and Subscription service to invoke this API.  Rate limits are enforced on this API. 160 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Add devices

 - [POST /devices/v1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1/postdevicesv1.md): Add one or more devices to a workspace. This API provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching the progress of the device addition task. For details about the  status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Update devices

 - [PATCH /devices/v1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1/patchdevicesv1.md): Update devices by passing one or more device IDs. The API currently supports:Assigning and unassigning devices to and from a service.Applying and removing subscriptions to and from devices. To remove an application, set the id under application to null and 'region' to null. Set an empty array to the attribute subscription to remove a subscription.  Only one operation is supported in a single API call. For example, you cannot assign devices to an application and assign subscriptions to devices in a single API invocation. You can achieve this with two API calls.This API provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The location header in the response provides the URI to be invoked for fetching the progress of the device update task. For details about the status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 20 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Get device information

 - [GET /devices/v1/devices/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1/getdevicebyidv1.md): Get details on a specific device by passing its resourceId. NOTE: You need  view permissions for device management to invoke this API. Rate limits are enforced on this API. 40 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Get progress or status of async operations in devices

 - [GET /devices/v1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1/getdevicesasyncoperationresourcev1.md): The add and update device APIs are asynchronous. Use this API to find the status of the asynchronous add and update operations.  An asynchronous resource tracks the status of an asynchronous operation. An asynchronous resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT) will no longer be accessible 24 hours after reaching the terminal state.  The TIMEOUT state indicates that the operation was in an INITIALIZED or RUNNING state for a period greater than the timeout set. If an asynchronous operation resource coming from an asynchronous request consists of multiple devices, a breakdown of succeeded devices and failed devices, if there are any, will be returned as the response. In this case, the device serial number identifies each device. NOTE: You need view permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 90 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

## Devices - v1beta1

### Get devices managed in a workspace (deprecated)

 - [GET /devices/v1beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/getdevices.md): With this API, you can: Retrieve a list of devices managed in a workspace. Filter  devices based on conditional expressions.NOTE: You need view  permissions for Devices and Subscription service to invoke this API.  Rate limits are enforced on this API. 160 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Add devices (deprecated)

 - [POST /devices/v1beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/postdevices.md): Add one or more devices to a workspace. This API provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching the progress of the device addition task. For details about the  status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 25 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Update devices (deprecated)

 - [PATCH /devices/v1beta1/devices](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/patchdevices.md): Update devices by passing one or more device IDs. The API currently supports:Assigning and unassigning devices to and from a service.Applying and removing subscriptions to and from devices. To remove an application, set the id under application to null and 'region' to null. Set an empty array to the attribute subscription to remove a subscription.  Only one operation is supported in a single API call. For example, you cannot assign devices to an application and assign subscriptions to devices in a single API invocation. You can achieve this with two API calls.This API provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The location header in the response provides the URI to be invoked for fetching the progress of the device update task. For details about the status fetch URL, refer to the API Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. Five requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get device information (deprecated)

 - [GET /devices/v1beta1/devices/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/getdevicebyid.md): Get details on a specific device by passing its resourceId. NOTE: You need  view permissions for device management to invoke this API. Rate limits are enforced on this API. 40 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get progress or status of async operations in devices (deprecated)

 - [GET /devices/v1beta1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/getdevicesasyncoperationresource.md): The add and update device APIs are asynchronous. Use this API to find the status of the asynchronous add and update operations.  An asynchronous resource tracks the status of an asynchronous operation. An asynchronous resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT) will no longer be accessible 24 hours after reaching the terminal state.  The TIMEOUT state indicates that the operation was in an INITIALIZED or RUNNING state for a period greater than the timeout set. If an asynchronous operation resource coming from an asynchronous request consists of multiple devices, a breakdown of succeeded devices and failed devices, if there are any, will be returned as the response. In this case, the device serial number identifies each device. NOTE: You need view permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 90 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

