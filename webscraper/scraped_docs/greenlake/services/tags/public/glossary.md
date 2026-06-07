---
title: "HPE GreenLake for Tags glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public/glossary.md"
scraped_at: "2026-06-07T06:13:29.517809+00:00Z"
---

# HPE GreenLake for Tags glossary

## Terms

### Tag

A tag is a form of metadata applied to any resource and primarily used to categorize resources based on purpose, owner, environment, or other criteria. A tag is a key-value pair attached to an HPE GreenLake cloud and services resource.

A tag key is the name used to refer to the tag, and a tag value is a value applied to the tag key. For example, a tag key (`key`) could be `location` and a tag value (`value`) could be `San Jose`.


```json
{
  "items": [
    {
      "id": "e0987f86-72e5-45ac-81b4-93c525a139ac",
      "type": "tags/tag",
      "key": "location",
      "value": "San Jose",
      "resourceCount": 4,
      "createdAt": "2024-02-27T17:04:44.799Z",
      "updatedAt": "2024-02-27T17:05:10.589Z",
      "generation": 0
    }
  ],
  "offset": 0,
  "count": 1,
  "total": 1
}
```

### Tagged resource

A tagged resource is a supported service resource that has one or more tags associated with it. Currently, under the scope of the Tags Service, the following resource types are supported:

- `DEVICE`
- `LOCATION`
- `DEVICE_SUBSCRIPTION`
- `SERVICE_SUBSCRIPTION`