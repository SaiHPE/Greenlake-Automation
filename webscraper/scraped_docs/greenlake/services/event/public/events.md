---
title: "Events"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/events.md"
scraped_at: "2026-06-07T06:13:26.999102+00:00Z"
---

# Events

Events are notifications that something has happened within a system. They are typically used in an event-driven architecture to signal state changes. These notifications contain context and data about what has happened. HPE GreenLake sends the notification to the event consumer (the webhook destination).

HPE GreenLake events follow the CloudEvents standard adopted by the Cloud Native Computing Foundation. This standard describes common formats for event data that provide interoperability across services, platforms, and systems. View the [CloudEvents v1.0.1 standard](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md).

## Events terminology

- **Event**—Events are factual records that HPE GreenLake creates when a resource has changed.
- **Event data**—Information about the occurrence or details about the data that was changed.
- **Event types**—Distinguishes between different events. Event types include created, updated, or deleted.
- **Message**—Events are sent to their destination in the form of a message.
- **Occurrence**—An occurrence is a factual capture of software system activity. For example, an occurrence might happen because of a state change in the software like a server is about to reboot.
- **Context attributes**—This is metadata included in an event that is used to identify the relationship of events to aspects of the system or to other events.


## Event types and event data

Event data is domain-specific information about the occurrence. The information contained within data is encoded as specified in datacontenttype. HPE GreenLake
supports three categories of event type.

- Resource created, updated, and deleted events
- Resource custom events
- Non-resource events


### Resource create, update, and delete events

These event types represent state changes to individual resources.
When a resource is created:

- type—`com.hpe.greenlake.<api-group>.<version>.<resource-collection>.created`
- datacontenttype—`application/json`
- time—The same as the createdAt and updatedAt property of the resource.
- data—A full representation of the updated resource.


When a resource is updated:

- type—`com.hpe.greenlake.<api-group>.<version>.<resource-collection>.updated`
- datacontenttype—`application/json`
- time—The same as the updatedAt property of the resource.
- data—A full representation of the updated resource.


When a resource is deleted:

- type—`com.hpe.greenlake.<api-group>.<version>.<resource-collection>.deleted`
- datacontenttype—`application/json`
- time—The time the resource was deleted
- data—A partial representation of the deleted resource including the
`type` and `id` properties.


### Resource custom events

Resource custom events represent a transition related to an individual
resource that is not a state change. For example, the completion of a
system start.

The resource custom event has:

- type—`hpe.greenlake.<api-group>.<version>.<resource-group>.<event>`
- datacontenttype—`application/json`
- time—The time the custom event occurred.
- data—Custom data.


### Non-resource event

These events represent a transition within the system not related to
an individual resource. The non-resource event has:

- type—`hpe.greenlake.<api-group>.<version>.<event>`
- datacontenttype—`application/json`
- time—The time the custom event occurred.
- data—Custom data.


## Event context attributes

Event context attributes are metadata that describe the event occurrence. HPE GreenLake events include the mandatory context
attribute properties defined in the CloudEvents standard, and may include several of the optional properties.

### Mandatory properties of an event

| Property | Value type | Description |
|  --- | --- | --- |
| `specversion` | String | The version of the CloudEvent specification. |
| `id` | String | The id property is the identifier of the event. In most cases, the id is in UUID format. |
| `source` | URI-reference | Provides the context of the event. It must be the URI that identifies the source and context in which the event occurred and it is prefixed with `//.api.greenlake.hpe.com/` and identifies the region and API group that produced the event. |
| `type` | String | The type property identifies the type of the event related to the source. For example: `greenlake.hpe.data.v1.volumes.snapshots.updated (type: volumes.snapshot, event: updated)` or `greenlake.hpe.compute.v1.servers.rebooted (type:servers, event: rebooted)`. |


### Optional properties

The optional properties that an event might include.

| Property | Value type | Description |
|  --- | --- | --- |
| `datacontenttype` | String | The encoding of the data in the `data` property in [RFC 2046](https://datatracker.ietf.org/doc/html/rfc2046) format. |
| `time` | Timestamp | Timestamp of when the event occurred in [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339) format. |
| `data` | Object | Event payload. The content is marshaled according to the media type in `datacontenttype`. |
| `dataschema` | string | A URI pointing to the `data` property schema. |
| `traceparent` | string | This field tracks the event as it moves through different systems. See [W3C Trace Context](https://w3c.github.io/trace-context/). |
| `tracestate` | string | This field carries additional tracing information specific to vendors and services involved in the event’s lifecycle. See [W3C Trace Context](https://w3c.github.io/trace-context/). |
| `recordedtime` | string | This field captures a precise timestamp, in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format, at which an event was recorded. |
| `sequence` | string | This event's order in the stream of events. |
| `deprecated` | boolean | Indicates whether the resource is deprecated. |
| `deprecationfrom` | string | The date and time in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format when the resource was marked as deprecated. |
| `deprecationsunset` | string | The future date and time in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format when the resource will become unsupported. |
| `deprecationmigration` | string | A URI to information describing the deprecated event's replacement. |


## Event batching

By default, webhook events are sent to the webhook destination one by one. However, you can configure events to be sent in batches. With batching enabled, events are sent in small groups (called batches) as an array. An event batch is sent based on whichever of the following happens first:

- **Event count**—When the maximum number of events are queued.
- **Time window**—If the maximum number of events is not met, events are sent after a short waiting time.


You can configure batching through the [HPE GreenLake UI](/docs/greenlake/services/event/public/ui#registering-a-webhook) or through an [API call](/docs/greenlake/services/event/public#registering-a-new-webhook).

The following code samples show examples of a single event and a batch of events.

An example of a single event:


```json
{
  "specversion": "1.0",
  "type": "com.hpe.greenlake.sample-publisher.v1beta1.sample-event4",
  "source": "publisher-test-single-2",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "time": "2009-11-10T23:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "eventData": {
      "key1": "new-data-6",
      "key2": "value-7"
    }
  },
  "subject": "485d4628bb5911eeb355f27748645044"
}
```

An example of batched events:


```json
[
  {
    "specversion": "1.0",
    "type": "com.hpe.greenlake.sample-publisher.v1beta1.sample-event4",
    "source": "publisher-test-single-2",
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "time": "2009-11-10T23:00:00Z",
    "datacontenttype": "application/json",
    "data": {
      "eventData": {
        "key1": "new-data-8",
        "key2": "value-7"
      }
    },
    "subject": "485d4628bb5911eeb355f27748645044"
  },
  {
    "specversion": "1.0",
    "type": "com.hpe.greenlake.audit-logs.v1beta1.created",
    "source": "audit-log-publisher",
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "time": "2009-11-10T23:00:00Z",
    "datacontenttype": "application/json",
    "data": {
      "eventData": {
        "logData": "Sample Log Description"
      }
    },
    "subject": "485d4628bb5911eeb355f27748645044"
  }
]
```

## Event filtering

With HPE GreenLake events, you can use filters to receive event notifications only when a specified subset of an event type occurs. For example, when the event type occurs for a particular user, status type, or when a value is greater or lower than a threshold.

Use the HPE GreenLake UI to subscribe to an event and specify a filter, see [Subscribe to an event](/docs/greenlake/services/event/public/ui#subscribing-to-an-event).

This section explains the elements of event filtering generically helping you construct your own filters prior to specify your filter in the UI.

Consult the event type documentation to learn the specifics of what a particular event type supports. The documentation for an event type specifies:

- The properties you can filter on.
- The literals that apply to each property.
- The comparison operations allowed.
- The logical operators allowed.


The event type documentation provides examples of event filters that will assist you in building your own.

Example filters:

- `status eq 'active'`—The event is sent when the status is active.
- `cpu gt 4`—The event is sent when the CPU is greater than 4.
- `startswith(name, 'abc')`—The event is sent when the name begins with the letters a, b, and c.


### Building a simple filter

The basic syntax of a filter is `<property> <comparison operation> <literal>`. For example, `name eq 'John'`. By applying this filter, HPE GreenLake only sends event messages to the webhook when the **name** (`property`) is **equal** (`comparison operation`) to **John** (`literal`).

#### Property

A property is a filterable resource or attribute. The property name is typically to the left of the comparison operation.
Event filters only apply to the properties in the `data` field, see [event types and event data](/docs/greenlake/services/event/public/events#event-types-and-event-data).

In the following JSON example of an event type payload, properties include `app_slug` and `customer_id`.
The example JSON also includes nested properties, such as `audit_info/username` and `audit_info/category`. The `/` separator specifies nested properties.

As event filters only apply to the `data` field, it can be excluded from event filter queries.


```JSON

  "data": {
    "app_slug": "string",
    "customer_id": "string",
    "username": "string",
    "app_instance_id": "string",
    "application_customer_id": "string",
    "audit_details": {},
    "enable_streaming": "string",
    "audit_info": {
      "username": "string",
      "category": "string",
      "customer_name": "string",
      "account_type": "string",
      "msp_id": "string",
      "audit_created_at": "string",
      "additional_info": {},
      "has_details": true
    },
    "created_at": "string"
  }
}
```

#### Literal

Event filters might support the following literals:

| Type | Example | Description |
|  --- | --- | --- |
| integer | **1234567** | An integer in base 10 (-1234567 for negative integer). |
| decimal | **1234.567**, **-1234.567** | A decimal in base 10 (-1234.567 for negative decimals). |
| timestamp | **2019-10-12T07:20:50.52934852Z** | A timestamp in RFC 3339 date-time format. |
| string | **'this is a string'** | A string value. Strings must begin and end with single quotes. |
| boolean | **true**, **false** | The boolean false/true value. |
| null value | **null** | A null (or nil) value. |


A filter query must use the correct literal type.

For example, if the filter evaluates the property `name`, which is a string, the filter `name eq John` will fail. A string literal must begin and end with single quotes. Similarly, if the filter evaluates the property `age`, which is an integer, the filter `age eq '60'` will fail.

#### Comparison operation

A comparison operation compares a property to a literal to produce a logical value (true or false). Event messages are only sent when the comparison evaluates to true.

The comparisons an event type might support are the following:

| Comparison | Example | Description |
|  --- | --- | --- |
| Equality | name **eq** 'John' | True if the property's value is the same as the literal. The property is on the operator's left. Valid for number, boolean, string, or timestamp properties. |
| Inequality | name **ne** 'John' | True if the property's value differs from the literal. The property is on the operator's left. Valid for number, boolean, string, or timestamp properties. |
| Greater than | count **gt** 5 | True if the property's value is greater than the literal. The property is on the operator's left. Valid for number or timestamp properties. |
| Greater than or equal to | count **ge** 5 | True if the property's value is greater than or equal to the literal. The property is on the operator's left. Valid for number or timestamp properties. |
| Less than | count **lt** 20 | True if the property's value is less than the literal. The property is on the operator's left. Valid for number or timestamp properties. |
| Less than or equal to | count **le** 20 | True if the property's value is less than or equal to the literal. The property is on the operator's left. Valid for number or timestamp properties. |
| Literal in array property | 'blue' **in** colors | True if the literal is contained in the property where the property is an array. The literal is on the left of the operator, and the right operand of the **in** operator is always a collection. Valid for an array of strings. |
| Property in a list of literals | color **in** ('red','yellow','blue') | True if the property's value is in the list of literals. The property is on the operator's left, and the right operand of the **in** operator is always a collection. Valid for string properties. The list of strings is in parentheses. |


### Combining filters using logical operators

Logical operators allow you to join multiple simple filters. The basic syntax of a combined filter is `<simple filter> <logical operator> <simple filter>`. For example,
`name eq 'John' or name eq 'Aya'`. With this example filter applied, you will receive event messages when the name is John or Aya.

| Logical operator | Example | Description |
|  --- | --- | --- |
| `and` | `name eq 'John' or name eq 'Aya'` | True if both sides of the logical operator are true. |
| `or` | `name eq 'John' or age eq 45` | True if either side of the logical operator is true. |
| `not` | `not color in ('RED', 'GREEN', 'BLUE')` | True if the right side of the logical operator is false. |


You can group filter queries using parentheses `()`. For example, `(count eq 5 or name eq 'fred') and color eq 'RED'`. The filter expression in the parentheses gets evaluated first and then used in the outer filter expression.
The order of precedence among the logical operators is first `not`, then `and`, and then `or`. The evaluation order is changed when grouping using parentheses.

### Invalid filters

If you supply an invalid filter in the HPE GreenLake UI, you’ll get a 400 Bad Request and an error message explaining which token failed to parse.

## Versioning

HPE GreenLake events are versioned to ensure they are adaptable over time, facilitating updates without disrupting existing functionalities.

Each event type includes a version string to indicate the version of the event. This version string aligns with the API versioning.

Examples:

- `com.hpe.greenlake.devices.`**v2alpha2.**`devices.updated`
- `com.hpe.greenlake.workspaces.`**v1beta1.**`tenants.deleted`
- `com.hpe.greenlake.data-services.`**v1.**`volumes.created`


Event versions pass through stages of increasing maturity, from `alpha` to `beta` to stable (`v1`).

See [HPE GreenLake Versioning](/docs/greenlake/guides/public/standards/versioning_basics#version-history--changelog) for more on the versioning stages.

### Deprecation policy and sunsetting

During the deprecation period, the event is still supported but is no longer recommended for use. Consumers are encouraged to migrate to the newer version. After deprecation, the event version is no longer supported in the sunset phase and may be removed.

Event deprecation is similar to and aligned with API deprecation. To attain this alignment, HPE GreenLake events use the [CloudEvents deprecation attributes](https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/deprecation.md). These attributes inform event consumers about upcoming changes or removals, facilitating smoother transitions and adjustments. The attributes used are:

- `deprecated`
- `deprecationfrom`
- `deprecationsunset`
- `deprecationmigration`


See [Optional properties](/docs/greenlake/services/event/public/events#optional-properties).

### Version history and changelog

A changelog is provided and released in the event documentation when a version change is made. The concepts are based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

One change is that we will not use semver.

Types of changes:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for removed features
- **Fixed** for any bug fixes
- **Security** in case of security and vulnerability changes