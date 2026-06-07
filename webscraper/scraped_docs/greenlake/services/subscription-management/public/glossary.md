---
title: "HPE GreenLake for Subscription Management glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/glossary.md"
scraped_at: "2026-06-07T06:13:29.393661+00:00Z"
---

# HPE GreenLake for Subscription Management glossary

## Acronyms

### MSP

A managed service provider (MSP) workspace is a multi-tenant operational mode between a service provider and clients. An MSP workspace provides MSP administrators options to manage multiple independent HPE GreenLake tenant workspaces, devices, and licenses. Only some applications support this model.

## Terms

## Auto-subscription

The Auto-Subscribe option enables automatic assignment of available licenses for devices available in the inventory. Find out more about auto-subscribe in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-3BC45941-37D8-437F-9823-3E95B8AC24AB.html).

### As a service type

As a service (aaS) is a product delivery model in which the product (or services) are provided on subscription. In the API, the `aasType` field returns a boolean declaring if the subscription is of type infrastructure as a service (IaaS) or not.

### Device type

A device type is a category or grouping of functionally related devices. In the API, the field (`deviceType`) declares the device type associated with a subscription.

- `AP`—Access points
- `COMPUTE`—Compute devices
- `GATEWAY`—Gateway devices
- `IAP`—Instant access point
- `STORAGE` —Storage devices
- `SWITCH`—Switch devices
- `PCE`—HPE for Private Cloud Enterprise devices


### Tier

A subscription tier defines the available licensed features and functionality. In the API, the field (`tier`) returns the subscription tier. The HPE GreenLake Cloud User Guide provides information about [network device type and subscription tier mapping](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-36EC6A65-7ED5-44FD-89A1-9C1805E82E6F.html). The table maps the device type to the corresponding subscription tier for network devices (AP, IAP, switch, or gateway devices) and provides a description of the tier.

There are two main subscription tiers.

- **Foundation** licenses enable all of the primary enterprise features.
- **Advanced** licenses include all Foundation features plus enhanced and additional premium features.


Find out more about subscription tiers by viewing these external links.

- [License types for devices](https://www.arubanetworks.com/techdocs/central/2.5.7/content/nms/subscriptions/lic-ovr-lic-typs.htm)—Find information about the types of licenses per device type.
- [Supported features](https://www.arubanetworks.com/techdocs/central/2.5.7/content/nms/subscriptions/lic-ovr-sup-ftrs.htm#Features)—Find information on the specific features supported by foundation and advanced licenses.