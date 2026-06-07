---
title: "HPE Compute Ops Management AHS Log Analysis"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/ahs/overview.md"
scraped_at: "2026-06-07T06:13:21.730089+00:00Z"
---

# HPE Compute Ops Management AHS Log Analysis

## AHS Log Analysis Definition

Active health system (AHS) log analyzer is an HTTP-based API call function that allows the user to upload and analyze an AHS file from HPE Gen10 and later servers.

## Using Compute Ops Management AHS log Analysis Task

The AHS log analyzer allows you to upload an AHS file from an HPE Gen10 or later server. Compute
Ops Management parses the file and provides a CSV or JSON file that you can use to review the server information from an AHS log file.

## AHS Log Analysis Prerequisites

- You have an active health system (AHS) log file for an HPE Gen10 or later server.
- The AHS log file size is 100 MB or less. 0 MB AHS files are not supported because they do not contain any information.
- Verify that your HPE GreenLake user account has the Compute Ops Management Administrator or Operator role with read and edit server permissions.
- HPE GreenLake is set up, a Compute Ops Management subscription has been added, and a Compute Ops Management service instance is provisioned.