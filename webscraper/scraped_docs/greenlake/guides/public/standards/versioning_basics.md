---
title: "API Versioning Basics | HPE GreenLake cloud"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides/public/standards/versioning_basics.md"
scraped_at: "2026-06-07T05:45:56.538138+00:00Z"
---

# GreenLake cloud API Versioning Basics

GreenLake cloud APIs are versioned. This document provides guidance to help you understand how versioning is identified and what it means.

Because GreenLake is composed of proprietary and industry standard APIs, you may encounter APIs that don't align with the definitions below. In that case, refer to the specific API for more information.

APIs are versioned at the resource collection level. Resource collections might change versions at independent points in time.

## Specifying the Version

* Generally: `/<api-group>/version/<resource-collection>`
* `Alpha`: The version names contain alpha (for example, `v1alpha1`, `v1alpha2`)
* `Beta`: The version names contain beta (for example, `v2beta3`, `v2beta4`)
* `Stable`: The version name is vX where X is an integer of the MAJOR version(for example, `v1`, `v2`)


Examples:

* Stable: `/iam/v1/<resource-collection>`
* Beta: `/iam/v1beta1/<resource-collection>`
* Alpha: `/iam/v1alpha1/<resource-collection>`


## Deprecation and Sunsetting

When a beta or stable Major version is incremented, both the new and old versions of the API are supported concurrently for a period of time:

* `/<api-group>/v1/...`
* `/<api-group>/v2/...`


The old version of the API is typically considered frozen (with the exception of bug fixes).

Deprecation is indicated using 'Deprecation', 'Sunset', 'Link' response headers and the OpenAPI 'deprecated' section.

### Deprecation Header

When the caller makes a request for a deprecated version, this is indicated via the `Deprecation` response header. The header contains the deprecation date or information about when it will be deprecated as prescribed in [RFC 9745](https://www.rfc-editor.org/rfc/rfc9745.html#section-2)

| Header | JSON Type | Value | Required? |
|  --- | --- | --- | --- |
| Deprecation | string | `true` if deprecated or date of deprecation (past or future) conforming to [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322#section-3.3) | Yes |



```plaintext
Deprecation: <imf-fixdate timestamp> or "true"
```

### Sunset Header

For versions that are expected to become unresponsive at a specific point in the future, the sunset time is indicated using the `Sunset` header.

| Header | JSON Type | Value | Required? |
|  --- | --- | --- | --- |
| Sunset | string | [RFC 8594](https://datatracker.ietf.org/doc/html/rfc8594). | Yes |


The timestamp given in the "Sunset" header field is later or the same as the one given in the "Deprecation" header field.

Example:


```plaintext
Deprecation: Sun, 11 Nov 2018 23:59:59 GMT
Sunset: Wed, 11 Nov 2020 23:59:59 GMT
```

The example shows that the resource has been deprecated since Sunday, November 11, 2018 at 23:59:59 GMT and its sunset date is Wednesday, November 11, 2020 at 23:59:59 GMT.


```plaintext
Sunset: <timestamp>
```

### Link Header

The Link header with relation type `deprecation` or `sunset` points to the resource documentation that provides additional information about the deprecation of the resource context.

* The Link header can also contain the following relation types:
  * `successor-version` that points to a resource containing the successor version.
  * `latest-version` that points to a resource containing the latest (e.g., current) version.
  * `alternate` that points to a substitute resource.


| Header | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| Link | string | Link to the additional deprecation/sunsetting information. | No |



```plaintext
Link: <{link}>; rel="deprecation"; type="text/html"
```


```plaintext
Link: <{link}>; rel="sunset"; type="text/html"
```

### OpenAPI Deprecated Section

Deprecated APIs are indicated using the `deprecated: true` field in the OpenAPI specification:


```yaml
  /resource:
    get:
      deprecated: true
```

## Understanding API Version Stages

Feature development proceeds through a series of stages of increasing maturity:

* `alpha`
* `beta`
* `stable`


Each stage has certain expectations and ramifications associated with them. APIs often can be highly mature / stable in one category, but may offer less long-term backwards compatibility support, so they have an overall lower designation.

|  | alpha | beta | stable |
|  --- | --- | --- | --- |
| Naming | `v1alpha1` → `v1alpha2` -> | `v1beta1` → `v1beta2` -> | `v1` |
| Purpose | Demo-able, works end-to-end but has limitations. Feature not guaranteed to have long-term support. | Usable, dependable. Feature intended to be moved to stable when ready where it will receive long-term support. | Production-hardened. |
| API | No guarantees on backward compatibility. | APIs are versioned. Breaking changes avoided, but assistance provided if necessary. | Dependable, production-worthy. APIs are versioned, with automated version conversion for backward compatibility. |
| Performance | Not quantified or guaranteed. | Weakly quantified. Monitored, but not guaranteed. | Performance (latency/scale) is quantified, documented, with guarantees against regression. |
| Security | Zero Trust applies: Must have some level of protection before being deployed to any publicly accessible endpoint. Alpha level permissions - Likely coarse-grained. | Zero Trust applies: Must have some level of protection before being deployed to any publicly accessible endpoint. May be mix of Alpha, beta level permissions - Likely coarse-grained. | Zero Trust applies: Must have some level of protection before being deployed to any publicly accessible endpoint. Permissions should be stable. Note that even stable permissions might later be made more or less granular and lost as they are backwards compatible. |
| Operational Support | Reduced Operational Requirements & SLAs. | Reduced Operational Requirements & SLAs. Striving for Always available. Upgrades do not cause downtime. Stateless redundancy. No single point of failure. | Standard Operational Requirements & SLAs. Generally always available. Upgrades do not cause downtime. Stateless redundancy. No single point of failure. |
| Deprecation Policy | None required, but best practice is to communicate with potential early integrators and set a timeline for deprecation. | Weak - 1 month notice until removed unless all usage has been migrated, then will be removed sooner. Will work with teams to prioritize and coordinate deprecation / migration. | Dependable, firm. Communicated broadly. At least 6 months notice will be provided before any API will be removed once deprecated. |


## Version History / Changelog

When a version change is made, a changelog is provided and released in the API documentation. The concepts are based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

One change is that we will not use semver, but rather the schema above.

### Types of changes

* `Added` for new features
* `Changed` for changes in existing functionality
* `Deprecated` for soon-to-be removed features
* `Removed` for now removed features
* `Fixed` for any bug fixes
* `Security` in case of security and vulnerabilities changes