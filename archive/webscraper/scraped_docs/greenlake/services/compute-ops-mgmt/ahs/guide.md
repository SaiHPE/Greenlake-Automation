---
title: "Getting Started Guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/ahs/guide.md"
scraped_at: "2026-06-07T06:13:21.831465+00:00Z"
---

# Getting Started Guide

This guide provides instructions for using the Compute Ops Management APIs to analyze an Active Health System (AHS) log file.

## 1. Review the prerequisites

Verify that the prerequisites are met before starting the analysis. For more information, see [AHS Log Prerequisites](/docs/greenlake/services/compute-ops-mgmt/ahs/overview#ahs-log-analysis-prerequisites).

## 2. Upload the AHS file

Use the following steps to upload an AHS file for analysis.

### Create a pre-signed URL

A pre-signed URL can be created by issuing a POST to the `/compute-ops-mgmt/v1beta1/ahs-files` endpoint with the correct payload for the task.
The following properties are used when creating a pre-signed URL task:

| Method | API | Property | JSON Type | Description | Required |
|  --- | --- | --- | --- | --- | --- |
| POST | `/compute-ops-mgmt/v1beta1/ahs-files` | `fileName` | string | AHS file name which will be uploaded using pre-signed URL | Yes |


A sample payload to create a pre-signed URL for an AHS file is shown below:


```json

{
    "fileName": "DL20_Gen9.ahs"
}
```

The pre-signed URL allows the user to upload the selected file directly and securely to the Compute Ops Management data store provided by Amazon Web Services (AWS) Simple Storage Service (S3).

The pre-signed URL is valid for a maximum of 10 minutes. The user must upload the file within this time period, or the link will expire, and the upload will fail.

A response sample from the POST follows:


```json

{
    "id": "2da59d25-72e7-4052-afd3-f20fc8e6d0b7",
    "type": "compute-ops-mgmt/ahs-file",
    "baseUrl": "https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/",
    "parameters": [
        {
            "name": "key",
            "value": "AHS_DISCONNECTED/427275fcddef11ebaeaea25b204e9436/2da59d25-72e7-4052-afd3-f20fc8e6d0b7/DL20_Gen9.ahs"
        },
        {
            "name": "x-amz-algorithm",
            "value": "AWS4-HMAC-SHA256"
        },
        {
            "name": "x-amz-credential",
            "value": "<YOUR_AWS_ACCESS_KEY_ID>/20250116/us-west-2/s3/aws4_request"
        },
        {
            "name": "x-amz-date",
            "value": "20250116T081435Z"
        },
        {
            "name": "x-amz-security-token",
            "value": "<YOUR_AWS_SESSION_TOKEN>"
        },
        {
            "name": "policy",
            "value": "<YOUR_S3_UPLOAD_POLICY>"
        },
        {
            "name": "x-amz-signature",
            "value": "1fc2a080e55489f6e5ec0aac9e6da11990ea04a2f29aa2764e1e0f0246dbb703"
        }
    ]
}
```

### Upload AHS file

Use the “parameters” list to create a pre-signed URL response to fill all the values in <>. It will form the upload command.


```sh

curl -i -F key=<key value> -F x-amz-algorithm=<algorithm value> -F x-amz-credential=<credential value> -F x-amz-date= <value> -F x-amz-security-token=<token value> -F policy=<policy value> -F x-amz-signature=<signature> -F file=@<filename> '<baseUrl value>'
```

An example curl command to upload an AHS file is shown below:


```sh

curl -i -F key=AHS_DISCONNECTED/427275fcddef11ebaeaea25b204e9436/72684583-59cf-4a81-b4c4-c4e586c8b0c1/upload_file_limit.ahs -F x-amz-algorithm=AWS4-HMAC-SHA256 -F x-amz-credential=<YOUR_AWS_ACCESS_KEY_ID>/20250107/us-west-2/s3/aws4_request -F x-amz-date=20250107T094634Z -F x-amz-security-token=<YOUR_AWS_SESSION_TOKEN> -F policy=<YOUR_S3_UPLOAD_POLICY> -F x-amz-signature=<YOUR_AWS_SIGNATURE> -F file=@090887-K53+8899090887992537_FWUFailure.ahs 'https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/'
```

After the successful command execution, the AHS file is uploaded to the AWS S3 bucket.

### AHS file upload failed

PATCH requests can be sent to `/compute-ops-mgmt/v1beta1/ahs-files/{id}` to update the status of AHS file.

| Method | API | Property | JSON Type | Description | Required |
|  --- | --- | --- | --- | --- | --- |
| PATCH | `/compute-ops-mgmt/v1beta1/ahs-files/{id}` | `status` | string | The status to be updated for an AHS file resource | Yes |


A sample payload to create a patch request to update the parsing status of AHS file to `ANALYSIS_FAILED` is shown below:


```json

{
    "parsingStatus": {
        "status": "ANALYSIS_FAILED"
    }
}
```

The following table summarizes the supported state transitions through PATCH request.

| Existing Analysis State | Requested Analysis State | Supported |
|  --- | --- | --- |
| `ANALYSIS_PENDING` | `ANALYSIS_FAILED` | Yes |
| `ANALYSIS_IN_PROGRESS` | `ANALYSIS_FAILED` | Yes |


During AHS analysis, once the file upload starts the initial status is set to `ANALYSIS_PENDING`. If the upload operation fails, the user should update the status from this initial state to the terminal state `ANALYSIS_FAILED` by using the above PATCH API call.

## 3. Parse AHS file

After uploading an AHS file to the pre-signed URL of the AWS S3 bucket, the user must send a request to parse the AHS file contents to get the required server details. To trigger the parse, send a POST request to the `/compute-ops-mgmt/v1beta1/ahs-files/{id}/parse` endpoint as shown below. The following property is used when creating a parse request:

| Method | API | Property | JSON Type | Description | Required |
|  --- | --- | --- | --- | --- | --- |
| POST | `/compute-ops-mgmt/v1beta1/ahs-files/{id}/parse` | `components` | string | Name of the component from AHS file which needs to be parsed | Yes |


A sample payload to create a parse request to the uploaded AHS file is shown below:


```json

{
    "components": "INVENTORY",
}
```

A sample response to a parse request is shown below:

200 OK

### Wait for the AHS file parsing to complete

After the parse request, Compute Ops Management will start parsing the AHS file. During the parsing, the status will be shown as parsing in progress.
The parsing status can be viewed by issuing a GET to the `/compute-ops-mgmt/v1beta1/ahs-files` endpoint with the correct path parameters for the task.
The following table gives a few examples for viewing the parsing status.

| Method | API | Property | Description |
|  --- | --- | --- | --- |
| GET | `/compute-ops-mgmt/v1beta1/ahs-files/` | none | Get the parsing status of all the AHS files |
| GET | `/compute-ops-mgmt/v1beta1/ahs-files/{id}` | `id` | Get the parsing status of an AHS file with UUID of `id` |
| GET | `/compute-ops-mgmt/v1beta1/ahs-files?sort=parsingStatus%2FstatusModifiedAt+desc&limit=1` | none | Get the status of last parsed AHS file |


The following table summarizes the possible parsing status values.

| Status | JSON Type | Description |
|  --- | --- | --- |
| `ANALYSIS_PENDING` | String | The pre-signed URL is generated, but the file is not uploading or parsing |
| `ANALYSIS_IN_PROGRESS` | String | Uploaded AHS file parsing is in progress for the given component/s |
| `ANALYSIS_SUCCESS` | String | Uploaded AHS file parsing is successfully completed for the given component/s |
| `ANALYSIS_FAILED` | String | Uploaded AHS file parsing failed for the given component/s |


A sample JSON response for a file that was parsed successfully from the GET call `/compute-ops-mgmt/v1beta1/ahs-files/3f071e5c-07f0-4b45-a99a-ae084e71f5f0` is shown below:


```json

{
    "id": "3f071e5c-07f0-4b45-a99a-ae084e71f5f0",
    "type": "compute-ops-mgmt/ahs-file",
    "generation": 6,
    "createdAt": "2025-02-27 07:32:18.684341Z",
    "updatedAt": "2025-02-27 07:32:30.573285Z",
    "resourceUri": "/compute-ops-mgmt/v1beta1/ahs-files/3f071e5c-07f0-4b45-a99a-ae084e71f5f0",
    "name": "HPE_MXQ2020JDN_20230911_GPU.ahs",
    "baseUrl": null,
    "parameters": [],
    "parsingStatus": {
        "status": "ANALYSIS_SUCCESS",
        "statusModifiedAt": "2025-02-27 07:32:30.536033Z",
        "statusReason": "",
        "errorCode": ""
    },
    "parsingResults": {
        "components": {
            "INVENTORY": {
               "csv"  : "MXQxxxxDN-20250227-0732-SERVER_INVENTORY.csv",
               "json" : "MXQxxxxDN-20250227-0732-SERVER_INVENTORY.json"
            }
        }
    },
    "hardware": {
        "productId": "Rxxx5A",
        "serialNumber": "MXQxxxxDN"
    }
}
```

A failure response sample from a GET call for getting the analysis status of a file identified by its UUID (id)
`/compute-ops-mgmt/v1beta1/ahs-files/7ffebeea-d6a6-4fe4-adbe-77d0a71ca691` is shown below:


```json

{
    "id": "7ffebeea-d6a6-4fe4-adbe-77d0a71ca691",
    "type": "compute-ops-mgmt/ahs-file",
    "generation": 7,
    "createdAt": "2025-02-19 16:07:19.559038Z",
    "updatedAt": "2025-02-19 16:08:54.705760Z",
    "resourceUri": "/compute-ops-mgmt/v1beta1/ahs-files/7ffebeea-d6a6-4fe4-adbe-77d0a71ca691",
    "name": "HPE_AHS.ahs",
    "baseUrl": null,
    "parameters": [],
    "parsingStatus": {
        "status": "ANALYSIS_FAILED",
        "statusModifiedAt": "2025-02-19 16:08:54.668771Z",
        "statusReason": "due to unknown issue. Contact support if the problem persists (error code: AHSE-103).",
        "errorCode": "AHSE-103"
    },
    "parsingResults": {
        "components": {
            "INVENTORY": ""
        }
    },
    "hardware": {
        "productId": "KS000-100",
        "serialNumber": "VL9XXX0035"
    }
}
```

## 4. Download the parsed contents

To download the parsed server inventory CSV file, send a GET request to the `/compute-ops-mgmt/v1beta1/ahs-files/{id}/download?filename={filename.csv}` endpoint as specified below. Here, `{id}` represents the AHS file UUID from which we are trying to download the server information, and `{filename.csv}` is the parsing results inventory file name. The format of the CSV file name is `server serial number-AHS file timestamp-upload time on local client.csv`. For downloading the JSON file, replace the `filename.csv` with `filename.json` in the above GET request. The format of the JSON file is similar to the CSV file format.

When you upload an AHS log file, the server inventory information in the resulting CSV or JSON file is derived from the latest bootlog present in the AHS log.

The server information CSV or JSON file contains the following set of data from the AHS:

### Server inventory

- General details, for example: Product name, serial number, Server ID, and power state.
- Chassis
- iLO
- BIOS
- Processor
- Device inventory
- Memory
- Storage
- Network
- Power
- Thermal-Fan Information
- Firmware
- Applications
- Drivers
- SD cards
- Power Supply Summary
- Thermal - Sensor Temperature Information In Celsius


### Server logs

The last seven days from the following logs are included

- Integrated Management Log
- iLO Event Log
- Security Log


Example download API call for the successfully parsed file is:`/compute-ops-mgmt/v1beta1/ahs-files/f897360a-64b7-47bd-aac7-4e1f88cd3c9f/download?filename=MXQxxxxDN-20250226-1047-SERVER_INVENTORY.csv`

A sample download API call response follows:


```csv

Product Name, ProLiant ML350 Gen10
Serial Number, MXQxxxxDN
ServerID, Rxxx5A:MXQxxxxDN
Date processed, 2025-04-03 16:34:57.010787+00:00 UTC
Power state, Not Available
Chassis
,ChassisType,FormFactor
,Unknown,4U
ILO
,ILOFirmware,ILOLicense
,iLO 5 v2.55p23 built on Oct 01 2021,iLO Advanced
BIOS
,BIOSVendor,BIOSVersion,BIOSReleaseDate
,HPE,U41 v2.04,04/18/2019
Processor
,MaxSpeedMHz,Model,Name,Stepping,RatedSpeedMHz,Status.Health,Status.State,TotalCores,TotalThreads
,4000,Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz,Intel Xeon processor,Cascade Lake SP B1,2100,OK,Enabled,20,40
,4000,Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz,Intel Xeon processor,Cascade Lake SP B1,2100,OK,Enabled,20,40
Device
,FirmwareVersion,Location,Name,PartNumber,ProductVersion,SerialNumber,Status.Health
,4.11,Embedded RAID,HPE Smart Array P408i-a SR Gen10,80xxx4-003,B,PZXxxxx0A9,Ok
,10.54.7,PCI-E Slot 1,HPE Ethernet 10Gb 2-port 56xxFP+ Adapter,72xx55-B21,00,MYIxxxM6L,Unknown
...
,90.04.96.00.01,PCI-E Slot 7,NVIDIA Tesla T4,900-2Gxx3-0300-000,A1,132xxx9515,Ok
,N/A,PCI-E Slot 8,Empty slot 8,,,,Absent
,2.5,Embedded Device,Embedded Video Controller,,,,Ok
Memory
,DeviceLocator,BaseModuleType,CapacityMiB,MemoryDeviceType,HPEPartNumber,Vendor,VendorPartNumber,OperatingSpeedMHz,MaximumSpeed,IsHPEMemory,HPESmartMemory,SerialNumber,CorrectableThresholdErrorCount,UnCorrectableThresholdErrorCount,Status.Health
,PROC 1 DIMM 3,RDIMM,65536,DDR4,P0xx53-0A1,Hynix,HMxxxx4N-XN,2933 MHz,3200 MHz,No,Yes,848xxx64,0,0,
...
,PROC 2 DIMM 8,RDIMM,65536,DDR4,P0xx53-0A1,Hynix,HMxxxx4N-XN,2933 MHz,3200 MHz,No,Yes,848xxx68,0,0,
,PROC 2 DIMM 10,RDIMM,65536,DDR4,P0xx53-0A1,Hynix,HMxxxx4N-XN,2933 MHz,3200 MHz,No,Yes,848xxx31,0,0,
Storage
,ControllerLocation,ControllerSlotLocation,ControllerModel,ControllerFirmware,ControllerSerialNumber,ControllerMemorySize,PhysicalDrivesCount,LogicalDrivesCount,DriveLocation,DriveNumber,DriveMedia,DriveModel,DriveCapacity,DriveProtocol,DriveRevision,DriveSerialNumber,DriveVendor,DriveWWID,DrivePowerOnHours
,0,Slot 0,P408i-a SR Gen10,4.11,PZXxxxx0A9,2048 MiB,N/A,N/A,Port 1I Box 3 Bay 1,0,SATA HDD,VK00xxxxTTC,1.75 TB,N/A,HPG6,PHYFxxxxDGN,N/A,314xxxC83310,N/A
...
,0,Slot 0,P408i-a SR Gen10,4.11,PZXxxxx0A9,2048 MiB,N/A,N/A,Port 2I Box 3 Bay 6,5,SATA HDD,VK00xxxxTTC,1.75 TB,N/A,HPG6,PHYFxxxxDGN,N/A,314xxx83315,N/A
Storage_NVME
,None
Network
,None
Power
,FirmwareVersion,Model,OEM.Hpe.Bay,PowerCapacity,Vendor,CTNumber,Revision,PartNumber,SparePartNumber,OptionKitNumber,FRU,SerialNumber,Status.Health
,2.00,Power Supply 1,1,800,LTEON,5XLxxxxRA34,A1,Pxxx95-B21,Pxxx85-001,Pxxx95-B21,03/14/16,5XLxxxxRA34,Ok
,2.00,Power Supply 2,2,800,LTEON,5XxxxxA35,A1,Pxxx95-B21,Pxxx85-001,Pxxx95-B21,03/14/16,5XxxxxA35,Ok
Thermal - Fan Information
,Name,Oem.Hpe.Location,Status.Health
,Fan 2,Fan,
,Fan 4,Fan,
...
,Fan 3,Fan,
,Fan 5,Fan,
Firmware
,Name,Version
,iLO,iLO 5 v2.55p23 built on Oct 01 2021
,System ROM,v2.04 (04/18/2019)
,Redundant System ROM,v2.04 (04/18/2019)
,Power Management Controller Firmware,1.0.8
,Power Management Controller FW Bootloader,1.1
,System Programmable Logic Device,0x12
,Server Platform Services (SPS) Firmware,4.1.4.505.0
,Intelligent Platform Abstraction Data,10.2.1 build 29
,HPE Smart Storage Battery 1 Firmware,0.70
,Intelligent Provisioning,3.64.2
,ME SPI Descriptor,1.2.0
,Innovation Engine (IE) Firmware,0.2.2.3.0
,Embedded Video Controller,2.5
,TPM Firmware,73.20
,HPE Ethernet 10Gb 2-port 562SFP+ Adapter,10.54.7
,HPE Ethernet 1Gb 4-port 369i Adapter,1.2836.0
,HP Ethernet 1Gb 4-port 366T Adapter,1.2836.0
,Power Supply 1,2.00
,Power Supply 2,2.00
,Array Controller P408i-a SR Gen10 in slot 0,4.11
,SATA HDD VK00xxxxTTC Port 1I Box 3 Bay 1,HPG6
,SATA HDD VK00xxxxTTC Port 2I Box 3 Bay 6,HPG6
Applications
,None
Drivers
,None
SDcards
,DeviceName,Revision,Manufacturer,mfgDate,SerialNumber,Capacity,LBAcount
,004GA0,3.0,Toshiba,7/2021,EBxxxC00,4 GB,7733248
Integrated Management Logs
,None
ILO Event Logs
,None
Security Event Logs
,None
Power Supply Summary
,PresentPowerReading,PowerManagementControllerFirmwareVersion,HighEfficiencyMode
,365 Watts,1.0.8,Balanced
Thermal - Sensor Temperature Information In Celsius
Sensor,Location,CriticalThreshold,CautionThreshold,Reading
01-Inlet Ambient,Inlet Temp,47.0,42.0,20
02-CPU 1,Processor Temp,N/A,69.75,40
03-CPU 2,Processor Temp,N/A,69.75,40
...
69-Inlet Ambient,Inlet Temp,N/A,N/A,20
81-Derived,Baseboard Temp,N/A,N/A,20
82-Derived,Baseboard Temp,N/A,N/A,38
```

Example download API call for the successfully parsed file with JSON format is:`/compute-ops-mgmt/v1beta1/ahs-files/f897360a-64b7-47bd-aac7-4e1f88cd3c9f/download?filename=MXQxxxxDN-20250226-1047-SERVER_INVENTORY.json`

A sample download API call with JSON response follows:


```json
{
    "ProductName": "ProLiant ML350 Gen10",
    "SerialNumber": "MXQxxxxDN",
    "ServerID": "Rxxx5A:MXQxxxxDN",
    "DateProcessed": "2025-04-03 16:34:57.011914+00:00 UTC",
    "PowerState": "Not Available",
    "Chassis": [
        {
            "ChassisType": "Unknown",
            "FormFactor": "4U"
        }
    ],
    "ILO": [
        {
            "ILOFirmware": "iLO 5 v2.55p23 built on Oct 01 2021",
            "ILOLicense": "iLO Advanced"
        }
    ],
    "BIOS": [
        {
            "BIOSVendor": "HPE",
            "BIOSVersion": "U41 v2.04",
            "BIOSReleaseDate": "04/18/2019"
        }
    ],
    "Processor": [
        {
            "MaxSpeedMHz": "4000",
            "Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",
            "Name": "Intel Xeon processor",
            "Stepping": "Cascade Lake SP B1",
            "RatedSpeedMHz": "2100",
            "Status.Health": "OK",
            "Status.State": "Enabled",
            "TotalCores": "20",
            "TotalThreads": "40"
        },
        {
            "MaxSpeedMHz": "4000",
            "Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",
            "Name": "Intel Xeon processor",
            "Stepping": "Cascade Lake SP B1",
            "RatedSpeedMHz": "2100",
            "Status.Health": "OK",
            "Status.State": "Enabled",
            "TotalCores": "20",
            "TotalThreads": "40"
        }
    ],
    "Device": [
        {
            "FirmwareVersion": "4.11",
            "Location": "Embedded RAID",
            "Name": "HPE Smart Array P408i-a SR Gen10",
            "PartNumber": "804334-003",
            "ProductVersion": "B",
            "SerialNumber": "PZXxxxx0A9 ",
            "Status.Health": "Ok"
        },
        {
            "FirmwareVersion": "2.5",
            "Location": "Embedded Device",
            "Name": "Embedded Video Controller",
            "Status.Health": "Ok"
        }
    ],
    "Memory": [
        {
            "DeviceLocator": "PROC 1 DIMM 3",
            "BaseModuleType": "RDIMM",
            "CapacityMiB": 65536,
            "MemoryDeviceType": "DDR4",
            "HPEPartNumber": "P0xxx-0A1",
            "Vendor": "Hynix",
            "VendorPartNumber": "HMxxxx4N-XN",
            "OperatingSpeedMHz": "2933 MHz",
            "MaximumSpeed": "3200 MHz",
            "IsHPEMemory": "No",
            "HPESmartMemory": "Yes",
            "SerialNumber": "84xxx64",
            "CorrectableThresholdErrorCount": 0,
            "UnCorrectableThresholdErrorCount": 0
        },
        {
            "DeviceLocator": "PROC 2 DIMM 8",
            "BaseModuleType": "RDIMM",
            "CapacityMiB": 65536,
            "MemoryDeviceType": "DDR4",
            "HPEPartNumber": "P0xxx-0A1",
            "Vendor": "Hynix",
            "VendorPartNumber": "HMxxxx4N-XN",
            "OperatingSpeedMHz": "2933 MHz",
            "MaximumSpeed": "3200 MHz",
            "IsHPEMemory": "No",
            "HPESmartMemory": "Yes",
            "SerialNumber": "84xxx68",
            "CorrectableThresholdErrorCount": 0,
            "UnCorrectableThresholdErrorCount": 0
        },
        {
            "DeviceLocator": "PROC 2 DIMM 10",
            "BaseModuleType": "RDIMM",
            "CapacityMiB": 65536,
            "MemoryDeviceType": "DDR4",
            "HPEPartNumber": "P0xxx-0A1",
            "Vendor": "Hynix",
            "VendorPartNumber": "HMxxxx4N-XN",
            "OperatingSpeedMHz": "2933 MHz",
            "MaximumSpeed": "3200 MHz",
            "IsHPEMemory": "No",
            "HPESmartMemory": "Yes",
            "SerialNumber": "84xxx31",
            "CorrectableThresholdErrorCount": 0,
            "UnCorrectableThresholdErrorCount": 0
        }
    ],
    "Storage": [
        {
            "ControllerLocation": 0,
            "ControllerSlotLocation": "Slot 0",
            "ControllerModel": "P408i-a SR Gen10",
            "ControllerFirmware": "4.11",
            "ControllerSerialNumber": "PZXxxxx0A9",
            "ControllerMemorySize": "2048 MiB",
            "PhysicalDrivesCount": "N/A",
            "LogicalDrivesCount": "N/A",
            "DriveLocation": "Port 1I Box 3 Bay 1",
            "DriveNumber": 0,
            "DriveMedia": "SATA HDD",
            "DriveModel": "VK00xxxxTTC",
            "DriveCapacity": "1.75 TB",
            "DriveProtocol": "N/A",
            "DriveRevision": "HPG6",
            "DriveSerialNumber": "PHYFxxxxDGN",
            "DriveVendor": "N/A",
            "DriveWWID": "3140xxxx3310",
            "DrivePowerOnHours": "N/A"
        },
        {
            "ControllerLocation": 0,
            "ControllerSlotLocation": "Slot 0",
            "ControllerModel": "P408i-a SR Gen10",
            "ControllerFirmware": "4.11",
            "ControllerSerialNumber": "PZXxxxx0A9",
            "ControllerMemorySize": "2048 MiB",
            "PhysicalDrivesCount": "N/A",
            "LogicalDrivesCount": "N/A",
            "DriveLocation": "Port 2I Box 3 Bay 6",
            "DriveNumber": 5,
            "DriveMedia": "SATA HDD",
            "DriveModel": "VK00xxxxTTC",
            "DriveCapacity": "1.75 TB",
            "DriveProtocol": "N/A",
            "DriveRevision": "HPG6",
            "DriveSerialNumber": "PHYFxxxxDGN",
            "DriveVendor": "N/A",
            "DriveWWID": "3140xxxx83315",
            "DrivePowerOnHours": "N/A"
        }
    ],
    "Storage_NVME": [],
    "Network": [],
    "Power": [
        {
            "FirmwareVersion": "2.00",
            "Model": "Power Supply 1",
            "OEM.Hpe.Bay": 1,
            "PowerCapacity": 800,
            "Vendor": "LTEON",
            "CTNumber": "5XLxxxxRA34",
            "Revision": "A1",
            "PartNumber": "Pxxx95-B21",
            "SparePartNumber": "Pxxx85-001",
            "OptionKitNumber": "Pxxx95-B21",
            "FRU": "03/14/16",
            "SerialNumber": "5XLxxxxRA34",
            "Status.Health": "Ok"
        },
        {
            "FirmwareVersion": "2.00",
            "Model": "Power Supply 2",
            "OEM.Hpe.Bay": 2,
            "PowerCapacity": 800,
            "Vendor": "LTEON",
            "CTNumber": "5XxxxxA35",
            "Revision": "A1",
            "PartNumber": "Pxxx95-B21",
            "SparePartNumber": "Pxxx85-001",
            "OptionKitNumber": "Pxxx95-B21",
            "FRU": "03/14/16",
            "SerialNumber": "5XxxxxA35",
            "Status.Health": "Ok"
        }
    ],
    "Thermal-FanInformation": [
        {
            "Name": "Fan 2",
            "Oem.Hpe.Location": "Fan"
        },
        {
            "Name": "Fan 3",
            "Oem.Hpe.Location": "Fan"
        },
        {
            "Name": "Fan 5",
            "Oem.Hpe.Location": "Fan"
        }
    ],
    "Firmware": [
        {
            "Name": "iLO",
            "Version": "iLO 5 v2.55p23 built on Oct 01 2021"
        },
        {
            "Name": "System ROM",
            "Version": "v2.04 (04/18/2019)"
        },
        {
            "Name": "HPE Ethernet 10Gb 2-port 562SFP+ Adapter",
            "Version": "10.54.7"
        },
        {
            "Name": "Power Supply 1",
            "Version": "2.00"
        },
        {
            "Name": "Array Controller P408i-a SR Gen10 in slot 0",
            "Version": "4.11"
        },
        {
            "Name": "SATA HDD VK00xxxxTTC Port 2I Box 3 Bay 6",
            "Version": "HPG6"
        }
    ],
    "Applications": [],
    "Drivers": [],
    "SDcards": [
        {
            "DeviceName": "004GA0",
            "Revision": "3.0",
            "Manufacturer": "Toshiba",
            "mfgDate": "7/2021",
            "SerialNumber": "EBxxxC00",
            "Capacity": "4 GB",
            "LBAcount": 7733248
        }
    ],
    "IntegratedManagementLogs": [],
    "ILOEventLogs": [],
    "SecurityEventLogs": [],
    "PowerSupplySummary": [
        {
            "PresentPowerReading": "365 Watts",
            "PowerManagementControllerFirmwareVersion": "1.0.8",
            "HighEfficiencyMode": "Balanced"
        }
    ],
    "Thermal-SensorTemperatureInformationInCelsius": [
        {
            "Sensor": "01-Inlet Ambient",
            "Location": "Inlet Temp",
            "CriticalThreshold": 47.0,
            "CautionThreshold": 42.0,
            "Reading": 20
        },
        {
            "Sensor": "02-CPU 1",
            "Location": "Processor Temp",
            "CriticalThreshold": "N/A",
            "CautionThreshold": 69.75,
            "Reading": 40
        },
        {
            "Sensor": "12-HD Max",
            "Location": "Disk",
            "CriticalThreshold": "N/A",
            "CautionThreshold": 60.0,
            "Reading": 35
        },
        {
            "Sensor": "82-Derived",
            "Location": "Baseboard Temp",
            "CriticalThreshold": "N/A",
            "CautionThreshold": "N/A",
            "Reading": 38
        }
    ]
}
```

Save the response from the download API call to a CSV or JSON file. Open the file to view the server information.