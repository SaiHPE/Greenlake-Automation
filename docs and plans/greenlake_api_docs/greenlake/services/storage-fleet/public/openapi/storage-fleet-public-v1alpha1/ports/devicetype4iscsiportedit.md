---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/ports/devicetype4iscsiportedit.md"
scraped_at: "2026-06-07T06:15:56.861251+00:00Z"
---

# Edit iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Edit iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the port
    Example: "d0fcfe2ff572f44e5beb0a9712c76d5d"

## Request fields (application/json):

  - `enablePeer` (boolean,null)
    Make the iSCSI port peer enabled. This is supported from OS version 10.4.0.
    Example: true

  - `ethernetFlowControl` (string,null)
    Flow Control setting of the port. Applicable for HPE Alletra Storage MP B10000 10.5.0 OS version and above. Ethernet Pause (EthPause) pauses transmission of all traffic on a physical Ethernet link. Data center bridging (DCB) is an enhancement to the Ethernet-pause protocol, that enables 0-drop packet delivery for certain traffic classes.
    Enum: "None", "EthPause", "DCB"

  - `label` (string,null)
    label of the port to edit to
    Example: "port_123"

  - `mtu` (string)
    Maximum transmission unit (MTU) size
    Example: "1500"

  - `vlans` (array,null)
    Port VLANs information. Specifying VLAN id is mandatory to configure VLAN.

  - `vlans.gatewayAddress` (string,null)
    Gateway address for the iSCSI port. If you are configuring VLAN then this is the VLAN Gateway for this port. If you want to clear or don't want to set the gateway address, then the gateway address should be 0.0.0.0.Configuring the gateway address supported from OS version 10.3.0.
    Example: "255.255.255.0"

  - `vlans.gatewayAddressV6` (string,null)
    Gateway address for the iSCSI port. If you are configuring VLAN then this is the VLAN Gateway for this port. Configuring the IPV6 gateway address supported from OS version 10.4.0.
    Example: "2001:db8:85a3::8a2e:370:7114"

  - `vlans.ipAddress` (string)
    IP address for the iSCSI port. If you are configuring VLAN then this is the VLAN IP address for this port.
    Example: "192.168.193.21"

  - `vlans.ipAddressV6` (string,null)
    IPv6 address for the iSCSI port. If you are configuring VLAN then this is the VLAN IPv6 address for this port. Configuring IPv6 address is supported from OS version 10.4.0.
    Example: "2001:db8:85a3::8a2e:370:7334"

  - `vlans.netMask` (string)
    NetMask for the iSCSI port. If you are configuring VLAN then this is the VLAN Netmask for this port.
    Example: "255.255.255.0"

  - `vlans.netMaskV6` (string,null)
    NetMask for the iSCSI port. If you are configuring VLAN then this is the VLAN Netmask for this port. Configuring this is supported from OS version 10.4.0.
    Example: "12"

  - `vlans.sendTargetGroupTag` (integer,null)
    The SendTargets Group Tag (STGT) for the iSCSI port
    Example: 13

  - `vlans.vlanId` (string)
    VLAN id for the iSCSI port. Value ranges between 1 to 4096
    Example: "1234"

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response default fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


