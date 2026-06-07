---
title: "POST /compute-ops-mgmt/v1beta1/ahs-files"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/post_ahs_file_upload_request_v1beta1.md"
scraped_at: "2026-06-07T06:14:58.075087+00:00Z"
---

# Create AHS file upload

A pre-signed URL can be created by issuing this POST call with correct payload for the task.
The pre-signed URL allows the user to upload the selected file directly and securely to the 
Compute Ops Management data store provided by Amazon Web Services (AWS) Simple Storage Service (S3).

The pre-signed URL is valid for a maximum of 10 minutes. The user must upload the file within this 
time period, or the link will expire, and the upload will fail.

Note: Use the “parameters” list to create a pre-signed URL response to fill all the values in . 
It will form the upload command.

An example curl command to upload an AHS file is shown below:

curl -i -F key=AHS_DISCONNECTED/427275fcddef29436/c924e770-...-9219276d2a5f/upload_file_presigned_post.ahs 
-F x-amz-algorithm=AWS4-HMAC-SHA256 -F x-amz-credential=example_credential -F x-amz-date=20250213T000000Z 
-F x-amz-security-token=example_token 
-F policy=example_policy 
-F x-amz-signature=example_signature -F file=@P05172-B21+2M2D110304_FWUFailure.ahs 
'https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/'

Sample Success Response:

HTTP/1.1 200 Connection Established
Proxy-Agent: Zscaler/6.2
HTTP/1.1 100 Continue
HTTP/1.1 204 No Content
x-amz-id-2: LYH6S+m7DrtihxwwXGNm8l7DFsJNwlBS5ps0+vOuucVy2dzDd9OMBZLeund2vJvUUtBWiQETYn0=
x-amz-request-id: 3RNFF7X985Y2M0WV
Date: Mon, 16 Dec 2024 14:17:04 GMT
x-amz-server-side-encryption: aws:kms
x-amz-server-side-encryption-aws-kms-key-id: arn:aws:kms:us-west-2:647619633241:key/ebcad3a6-b6e2-4314-acf1-447f9f38f9bc
x-amz-server-side-encryption-bucket-key-enabled: true
ETag: "6e215e86cc62e52ad1ff5f184edd483d"
Location: https://dev-hpecomputesupport-us-west-2.s3.amazonaws.com/AHS_DISCONNECTED%2F427275fcddef11ebaeaea25b204e9436%2F72684583-59cf-4a81-b4c4-c4e586c8b0c1%2FP05172-B21+2M2D110304_FWUFailure.ahs
Server: AmazonS3

Endpoint: POST /compute-ops-mgmt/v1beta1/ahs-files
Version: latest
Security: Bearer

## Request fields (application/json):

  - `fileName` (string, required)
    Name of the AHS file which needs to be uploaded.
    Example: "2024-08-26_19-20-42_P05172-B21+2M2D110304_FWUFailure.ahs"

## Response 200 fields (application/json):

  - `id` (string)
    Unique file identifier (File UUID) of the ahs-files resource given by the system.
    Example: "017a9224-4d6e-4adb-9c78-321f95c7bb2c"

  - `type` (string)
    Type of the resource

  - `baseUrl` (string)
    Bucket url where file is being uploaded.

  - `parameters` (array)
    Key value pairs attributes of parameters list supplied for uploading the AHS file to AWS S3 bucket.
    Example: [{"name":"key","value":"AHS_DISCONNECTED/427275fcddef29436/c924e770-...-9219276d2a5f/upload_file_presigned_post.ahs"},{"name":"x-amz-algorithm","value":"AWS4-HMAC-SHA256"},{"name":"x-amz-credential","value":"example_credential"},{"name":"x-amz-date","value":"20250213T000000Z"},{"name":"x-amz-security-token","value":"example_token"},{"name":"policy","value":"example_policy"},{"name":"x-amz-signature","value":"example_signature"}]

  - `parameters.name` (string)
    Enum: "key", "x-amz-algorithm", "x-amz-credential", "x-amz-date", "x-amz-security-token", "policy", "x-amz-signature"

  - `parameters.value` (string)

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

## Response 404 fields (application/json):

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

## Response 429 fields (application/json):

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


