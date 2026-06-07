---
title: "GET /compute-ops-mgmt/v1beta1/filters"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/filters-v1beta1/get_filters.md"
scraped_at: "2026-06-07T06:14:43.086271+00:00Z"
---

# List all saved filters

Retrieve a paginated collection of saved filter resources.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta1/filters
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Filters can be filtered by:
- filterResourceType
- id
- type

The following examples are not an exhaustive list of all possible filtering options.

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `items` (array, required)
    Array of saved filter resources in the page of the collection.

  - `items.id` (string)
    Primary identifier for the filter resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `items.type` (string)
    The type of the resource.

  - `items.generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `items.createdAt` (string)
    Time of filter resource creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.updatedAt` (string)
    Time of the last update to the filter resource.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.resourceUri` (string)
    URI to the filter resource itself (i.e. a self link).
    Example: "/compute-ops-mgmt/v1beta1/filters/b870f080-6448-48c5-b23a-d04f2d489174"

  - `items.name` (string)
    The display name of the filter, must be unique.

  - `items.description` (string,null,string,null)
    An optional longer description of the filter.

  - `items.readOnly` (boolean)
    If true, the filter is pre-defined and cannot be edited or deleted.

  - `items.filterResourceType` (string)
    The type of the resource that the filter matches against.  New resource types may be added as a backward
compatible change to the API.
    Enum: "compute-ops-mgmt/server"

  - `items.enabledForRRP` (boolean)
    Flags the filter for use with resource restriction policies used by scope-based access control (SBAC). Only administrators with full access to all scopes can create, edit, or delete RRP-enabled filters. The use of some resource properties may be disallowed in RRP-enabled filters.

  - `items.filter` (string,null,string,null)
    The filter expression, in the same syntax as the filter query parameter common to many
collection endpoints.  At least one of filter and filterTags must be specified.  If both are specified,
both filter expressions much match for a resource to match the filter.

  - `items.filterTags` (string,null,string,null)
    An optional filter expression for tags, in the same syntax as the filter-tags query parameter common to many
collection endpoints.  Used to handle tag keys with special characters.  At least one of filter and filterTags
must be specified.  If both are specified, both filter expressions much match for a resource to match the filter.

  - `items.uiData` (object,null,object,null)
    Opaque JSON structure used by the Compute Ops Management UI.  Other clients should not read or set this property.
Note that the format of the data is subject to change without notice, even with the same API version of filters.

  - `items.matchesUri` (string)
    URI of collection of match entities that indicate which resources match the filter.
    Example: "/compute-ops-mgmt/v1beta1/filters/b870f080-6448-48c5-b23a-d04f2d489174/matches"

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


