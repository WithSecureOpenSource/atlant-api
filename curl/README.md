# Getting Started with Atlant using cURL

WithSecure Atlant is an self-hosted service that can be used to scan files for
malicious content, detect spam, and classify URLs. Atlant exposes its scanning
and detection capabilities using a straight-forward REST API, making it a great
building block for any service that needs to perform these tasks.

This document explains how to deploy WithSecure Atlant and get started using its
scanning and detection API. The examples are using [cURL](https://curl.se)
command-line HTTP client to interact with the API, but the same tasks should be
doable with any HTTP client application or library.

## Installing and Configuring Atlant

WithSecure Atlant has multiple installation options to support different
environments and requirements:

- **DEB and RPM Packages**: Traditional distribution packages or installing
  standalone Atlant.
- **Policy Manager Package**: Policy Manager package can be imported to
  WithSecure Policy Manager to create the final installation package. Atlant
  installations created through this method can be managed Policy Manager
  Console.
- **VMWare Virtual Appliance**: Premade virtual appliance with Atlant installed.
  Can be easily taken into use in VMWare environments.
- **Container Image**: Atlant is also available as a Linux container suitable
  for use with Kubernetes, Docker, Podman, and other container management
  solutions.

All the Atlant installation options offer the same scanning and detection
capabilities. Where the options differ are the way they are configured and (in
the case of Atlant container) how clients authenticate when accessing privileged
APIs.

DEB and RPM packages, Policy Manager package, and VMWare virtual appliance offer
identical feature set. The only difference between them is that Policy Manager
package (and depending on the configuration, VMWare virtual appliance) can be
managed via Policy Manager Console. This document refers to installations
created using these methods as "regular" installations in order to distinguish
them from Atlant containers.

Due to being designed for a different kind of environment, Atlant container
changes how certain things work. Whereas "regular" non-containerized Atlant
installations rely on mutable configuration that can (optionally) be centrally
managed, Atlant container embraces immutable configuration as is typical with
container based solutions. Atlant container is configured using a single JSON
configuration file that defines all aspects of its operation.

Another difference between the regular and the containerized version of Atlant
is how they handle authentication. Regular Atlant supports OAuth 2.0 based
client management, whereas Atlant container uses a simple API key based scheme.

This guide explains how to setup a regular Atlant installation on a Debian based
system and how to deploy Atlant as a container. Atlant's deployment process is
very flexible and many of its features are not covered here. For more
information on all the different options that are available, please refer to the
[Atlant user manual][manual].

### Regular Installation

The first step of installing Atlant is to download a suitable installation
package from [Atlant's product page][atlant-download]. This guide assumes a
Debian 11 based target system, which means that the provided DEB package is the
correct choice for this system.

Before we can actually install Atlant we need to install its dependencies.
Up-to-date list of required dependencies for each supported distribution can be
found from the [Atlant user manual][manual-system-requirements]. The following
command (run as root) can be used to install the necessary dependencies on a
Debian 11 system:

```sh
apt install libcurl4 python3
```

Once the dependencies are installed, we are now ready to install Atlant. The
installation happens in two phases: first, we need to install the DEB package we
just downloaded and second, we need to activate Atlant using the included
`activate` program.

```sh
dpkg -i f-secure-atlant*.deb
/opt/f-secure/atlant/atlant/bin/activate --license-key ATLANT-LICENSE-KEY
```

Replace `ATLANT-LICENSE-KEY` with the license key you received from WithSecure.
If you are activating Atlant with a license file instead of a license key, use
`--license-file PATH-TO-LICENSE-FILE` option replacing `PATH-TO-LICENSE-FILE`
with the path of your license file.

Now Atlant should be installed and the next step is to configure it. For a
typical installation this includes three steps:

1. Configuring HTTPS
2. Configuring API endpoints
3. Configuring one or more clients

#### Configuring HTTPS

Atlant installations always expose their REST API endpoints over HTTPS. This
means that before any endpoints can be configured, it is necessarily to first
supply Atlant with a TLS certificate and a key. How to create or acquire a TLS
certificate is outside the scope of this guide and we will simply assume that a
valid certificate is available on the machine as `atlant.pem` and that the key
file associated with the certificate is available as `atlant.key`.

Atlant can be configured using `atlantctl` utility. The following commands can
be used to configure HTTPS assume `atlant.pem` and `atlant.key` are in the
current directory:

``` sh
/opt/f-secure/atlant/atlant/bin/atlantctl set tls certificate atlant.pem
/opt/f-secure/atlant/atlant/bin/atlantctl set tls key atlant.key
```

> **Note**
> The Atlant container can be configured to expose its API over plain HTTP. This
> can be useful in setups where TLS is terminated by the supporting
> infrastructure.

#### Configuring API Endpoints

Once HTTPS has been configured the next step is to configure the ports where
Atlant will expose its REST APIs. Atlant provides three different APIs:

- **Authentication API**: Clients must use this API to authenticate with Atlant
  before using the other APIs.
- **Scanning API**: Client can use this API to scan files, detect spam, and
  classify URLs.
- **Management API**: Clients can use this API to manage Atlant's configuration
  remotely. This guide does not make use of this API.

Atlant's different APIs must be exposed on different ports.

> **Note**
> Atlant container only exposes scanning API. This is because it relies on
> immutable configuration and handles authentication using API keys instead of
> OAuth.

For this guide, it is enough to configure authentication and scanning API
endpoints. The following command can be used to configure authentication API
endpoint to be available on port `8080`:

```sh
/opt/f-secure/atlant/atlant/bin/atlantctl add authorization https_endpoints \
  '{"address": "0.0.0.0", "port": 8080}'
```

This guide assumes that the port where Atlant's authentication API is available
is stored in shell variable `ATLANT_AUTH_PORT`.

Similar command can be used to configure scanning API endpoint to be available
on port `8081`:

```sh
/opt/f-secure/atlant/atlant/bin/atlantctl add scanning https_endpoints \
  '{"address": "0.0.0.0", "port": 8081}'
```

This guide assumes that the port where Atlant's scanning API is available is
stored in shell variable `ATLANT_SCAN_PORT`.

> **Warning**
> By default, regular Atlant installations come with a single ICAP endpoint
> enabled. ICAP is an alternative API that can be used for scanning. This is for
> compatibility with other existing solutions. The default ICAP endpoint is not
> using encryption and does not require authentication. Consider removing the
> default endpoint if this a problem in your environment. Atlant container does
> not enable any ICAP endpoints by default.

#### Configuring Clients

At this point Atlant's authentication and scanning APIs are enabled. However,
before the APIs can be accessed it is necessarily to create one or more clients.
Each client has its own client ID and secret. Clients can use these credentials
to authenticate via Atlant's authentication API.

The following command can be used to create a client that has the permission to
scan files using Atlant's scanning API:

```sh
/opt/f-secure/atlant/atlant/bin/atlantctl client create \
  '{"scopes": ["scan"]}'
```

The command prints out credentials for the newly created client:

```json
{
  "client_id": "5dbfe97de42bf53a0ae73bff9eba4ecb",
  "client_secret": "87e7b3a61e7fdcdfc03162fdcab82a942b9c62715ff3d612e15adf32d1b1500b"
}
```

> **NOTE**
> This is the only time client secret is shown. Store the client secret in order
> to use it later.

This guide assumes that the client ID and secret are stored in shell variable
`CLIENT_ID` and `CLIENT_SECRET`.

Now Atlant is installed and configured and can be used for scanning. Rest of
this guide will assume Atlant's address is stored in `ATLANT_HOST` shell
variable.

### Container

Before Atlant container can be created, the first step is to create a
configuration file for it. Atlant containers are configured using a single JSON
file and the configuration remains immutable once the container is running.

The following is a simple configuration file for Atlant container:

**config.json**

```json
{
  "subscription_key": "ATLANT-LICENSE-KEY",
  "scanning": {
    "http_endpoints": [
      {
        "address": "0.0.0.0",
        "port": 8081
      }
    ]
  },
  "authentication": {
    "api_key": "API-KEY-FOR-CLIENTS"
  },
  "tls": {
    "certificate": "atlant.pem",
    "key": "atlant.key"
  }
}
```

Replace `ATLANT-LICENSE-KEY` with the license key you received from WithSecure.
Replace `API-KEY-FOR-CLIENTS` with an API key that clients need to provide when
scanning content. API keys must be between 30 and 128 bytes long.

This example configures a single REST scanning API endpoint and exposes it on
the port `8081`. This guide will assume that this port is stored in
`ATLANT_SCAN_PORT` shell variable.

The configuration exposes Atlant's scanning API over HTTPS by specifying a path
to the TLS certificate and the associated key file. How to create or acquire a
TLS certificate is outside the scope of this guide and we will simply assume
that a valid certificate is available on the machine as `atlant.pem` and that
the key file for it is available as `atlant.key`. These files should be placed
to the same directory as the configuration file.

> **NOTE**
> Atlant container supports exposing APIs over plain HTTP. This can be done by
> simply leaving out the `tls` property from the configuration file. Serving
> APIs over plain HTTP can be useful in setups where TLS is terminated by the
> supporting infrastructure.

In this guide we will assume Atlant container's configuration file and any
additional files required by the configuration are located on the host at the
`/etc/atlant` directory.

With the configuration ready, Atlant container can now be started using Docker
with the following command:

```sh
docker run -v /etc/atlant:/etc/opt/withsecure/atlant/config:ro \
           -p 8081:8081 \
           public.ecr.aws/withsecure/atlant:latest
```

This command creates and starts a new Atlant container, downloading the image
from the container registry if it does not already exist on the host system. The
command mounts Atlant's configuration directory `/etc/atlant` from the host to
the `/etc/opt/withsecure/atlant/config` directory inside the container. The
configuration is mounted as read-only as there is no need for Atlant container
to ever change it. Finally, the command exposes container's port `8081` on the
same port on the host.

Now Atlant container is running and can be used for scanning. Rest of this guide
will assume Atlant's address is stored in `ATLANT_HOST` shell variable.

## Authentication

Clients need to authenticate with Atlant before they can scan content.

Atlant container and non-containerized version of Atlant use a different scheme
for authentication.

If Atlant was installed from a DEB or an RPM package, or an installer exported
from Policy Manager, or deployed from the provided VMWare virtual appliance it
is not the containerized version of Atlant. Correspondingly, if Atlant was
installed using Docker, Podman, or a similar container tool it is the
containerized version of Atlant. These different versions offer the same
scanning capabilities, but differ in the authentication schemes they support.

The next two sections cover how authentication works in "regular" (ie.
non-containerized) and containerized Atlant installations.

### Regular Installation

Clients need to authenticate with Atlant before they can scan content.
Authentication with regular Atlant happens using OAuth 2.0 client credentials
flow. In this authentication scheme, the client uses its client ID and client
secret to get a short-lived access token. The client can then use this access
token when making requests to the scanning API.

**Request**

```sh
curl -d grant_type=client_credentials \
     -d audience=f-secure-atlant \
     -d client_id=$CLIENT_ID \
     -d client_secret=$CLIENT_SECRET \
     https://${ATLANT_HOST}:${ATLANT_AUTH_PORT}/api/token/v1
```

`audience`: The audience parameter is used by Atlant to distinguish different
types of clients. If the client was created locally using the `atlantctl`
command (like is the case in this guide) the `audience` parameter should be set
to `f-secure-atlant`. Alternatively, if the client was created using Policy
Manager Console the parameter should be set to `policy-manager`.

`client_id` and `client_secret`: Client ID and secret identify the client to
Atlant. Values for these parameters are displayed when a client is first created
using `atlantctl` or Policy Manager Console.

**Response**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6InNjYW4gbWFuYWdlbWVudCIsImF1ZCI6ImYtc2VjdXJlLWF0bGFudCIsImV4cCI6MTY3OTMyNjMzMCwianRpIjoiMTJjN2JhODA5OTVkOGY2MWY5ZGE4NjY1ZWViY2NhZWUyNTA5ZWJhMTk4MzUzNzZkNTcwY2FhYTI1OWU3ZGNhMiIsImlhdCI6MTY3OTMyMjczMCwiaXNzIjoiZi1zZWN1cmUtYXRsYW50IiwibmJmIjoxNjc5MzIyNzMwLCJzdWIiOiI3MGNiMjcwZTcyMTA4OWFiY2YxYjU5MWI1MGQ3YjJmNiJ9.kAeIPaNlKlw1Y-6paTvzPgYk41Spd87PEjxW1-yIYVI",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

If authentication succeeded, Atlant will respond with HTTP status `200` and
return a JSON object containing the access token. In addition, the response
object will contain a hint regarding the lifetime of the token (in seconds) in
the `expires_in` property. After the token has expired it can no longer be used
and client has to repeat the authentication process to acquire a new access
token.

In subsequent example commands we assume that the access token received in this
step has been stored in `ACCESS_TOKEN` variable.

### Container

By default, Atlant container does not limit access to the scanning API. With the
default configuration, anyone with access to the container's HTTP endpoint can
perform scanning requests without authentication. This could be acceptable in
environments where the access to Atlant's scanning API is limited via some other
method.

If authentication is required, Atlant container supports specifying a static API
key as a part of its configuration. If an API key is specified, then a client
needs to supply that API key via `X-Api-Key` HTTP header when it makes scan
requests. In Atlant container's configuration file, API key can be specified
using the `api_key` property inside the `authentication` object.

Here is an example of a simple Atlant container configuration file that
specifies a single scanning endpoint and enables API key based authentication:

**config.json**

```json
{
  "subscription_key": "ATLANT-LICENSE-KEY",
  "scanning": {
    "http_endpoints": [
      {
        "address": "0.0.0.0",
        "port": 8081
      }
    ]
  },
  "authentication": {
    "api_key": "6f082ace-1a8d-4f6d-a6f0-bd24076e8d7d"
  }
}
```

This configuration specifies that a single HTTP scanning endpoint should be
exposed on container's port 8080 and that requests to that endpoint need to must
include API key `6f082ace-1a8d-4f6d-a6f0-bd24076e8d7d` in `X-Api-Key` header.
API keys must be between 30 and 128 bytes long.

Note that to ensure the confidentiality of API keys, Atlant container should be
configured to use HTTPS.

In subsequent example commands we assume that the API key has been stored in
`API_KEY` variable.

## Scanning

In the scanning API all scans are performed by making `POST` requests to the API
endpoint at `/api/scan/v1`. Scan requests must contain a `multipart/form-data`
body with one or two parts.

The first part must always be present and have the content type
`application/json`. This part should contain JSON metadata for the scan. In the
simplest case, an empty JSON object can be provided if the default settings are
appropriate.

The second part, if present, should contain the data to be scanned in binary
format.

Depending on Atlant's configuration, requests to the scanning API may need to be
authenticated.

In the case of "regular" non-containerized Atlant installations, authentication
is always mandatory and happens using OAuth 2.0 (see [Authentication → Regular
Installation](#Regular Installation)). In this scheme the client needs to
include the access token received from the authentication API to each scanning
request using the `Authorization` header.

In the case of containerized Atlant installations, authentication is optional.
If authentication is used, it happens using preconfigured API keys (see
[Authentication → Container](#Container)). In this scheme the client needs to
specify the client needs to include the API key in each scanning request using
the `X-Api-Key` header.

The following sections present how to complete common scanning tasks using the
scanning API. For the full documentation of the API, refer to [Atlant user
manual][manual].

### Scanning Files

When doing a basic file scan, it is often enough to provide just an empty JSON
object (`{}`) as scan metadata. This means the scan will just use the default
settings.

In this example, we are scanning the file `/path/to/some/file` by including its
contents into the second part of the request. This is done using cURL's `@FILE`
syntax. See [cURL manual](https://curl.se/docs/manpage.html) for more details on
how to include file contents into requests.

**Request**

```sh
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -F 'metadata={};type=application/json' \
     -F 'data=@/path/to/some/file' \
     https://${ATLANT_HOST}:${ATLANT_SCAN_PORT}/api/scan/v1
```

The previous command is using OAuth 2.0 based authentication. This
authentication method is appropriate for "regular" non-containerized Atlant
installations. When Atlant container is used, authentication is an optional
feature which, if enabled uses a preconfigured API key. In the case of Atlant
container the scan request would look like this:

**Request**

```sh
curl -H "X-Api-Key: $API_KEY" \
     -F 'metadata={};type=application/json' \
     -F 'data=@/path/to/some/file' \
     https://${ATLANT_HOST}:${ATLANT_SCAN_PORT}/api/scan/v1
```

In the case of both requests, Atlant will return scan results as a JSON object:

**Response**

```json
{
  "scan_result": "clean",
  "detections": [],
  "warnings": {
    "corrupted": false,
    "encrypted": false,
    "max_nested": false,
    "max_results": false,
    "max_scan_time": false,
    "need_content": false
  },
  "status": "complete"
}
```

Here, the scan was fully completed as indicated by the `status` property. The
file was deemed to be safe as `scan_result` was set to `clean`. Possible values
for `scan_result` are as follows:

| Scan Result | Description |
| --- | --- |
| `clean` | The file is safe. |
| `whitelisted` | The file has been marked as safe. |
| `suspicious` | The file is suspicious. |
| `PUA` | The file is potentially unwanted application. |
| `UA` | The file is unwanted application. |
| `harmful` | The file is malicious. |
| `spam` | In case spam detection is enabled, this result indicates that the message was classified as spam. |

Similarly, if we try to scan EICAR antivirus test file. We get back the
following response:

**Response**

```json
{
  "scan_result": "harmful",
  "detections": [
    {
      "category": "harmful",
      "name": "EICAR_Test_File"
    },
    {
      "category": "harmful",
      "name": "Malware.Eicar-Test-Signature"
    }
  ],
  "warnings": {
    "corrupted": false,
    "encrypted": false,
    "max_nested": false,
    "max_results": false,
    "max_scan_time": false,
    "need_content": false
  },
  "status": "complete"
}
```

Here Atlant classified the file as harmful and provided a list of detections for
the file.

#### Polling for Slow Results

Atlant may not be able to respond with a full set of results immediately. In
this case Atlant will respond with HTTP `202 Accepted` status and the response
will have the `scan_result` property set to `pending` to indicate that the scan
was not fully completed. Pending responses will also include `Location` and
`Retry-After` headers. The `Location` header specifies a path that the client
should poll for results and the `Retry-After` header includes a suggestion for
the number of seconds that the client should wait before polling.

To poll for results, client should make an HTTP `GET` request to the path
specified in the `Location` header included in the response to the initial scan
request. Client should continue polling for results until the `status` property
in the response is set to `complete`.

### Detecting Spam

Atlant can also be used to detect spam. To do this, client needs to enable spam
detection functionality by setting `antispam` to `true` in `scan_settings` part
of the scan request. In order to help Atlant better classify emails, it is
beneficial to provide some additional metadata about the message. The
`content_meta` object in scan metadata includes a number of optional properties
that can be used to pass in additional details about the sender and the
recipients of the email, among other things.

In order to make the cURL command-line more readable, we store the metadata we
want to send in a separate `metadata.json` file and then include it into the
request by using the same `@FILE` notation we used earlier for including file
contents to the request

**metadata.json**

```json
{
    "scan_settings": {
        "antispam": true
    },
    "content_meta": {
       "ip": "127.0.0.1",
       "sender": "john@example.com",
       "recipients": [
          "jane@example.com",
          "bob@example.com"
       ]
    }
}
```

The scan request explicitly enables spam detection support by setting `antispam`
property to `true` inside `scan_settings`. In addition, the request supplies
Atlant with additional metadata about the message by specifying message's source
IP address using the `ip` property and details about the sender and the
recipients of the message using their respective properties.

The following command assumes `/path/to/some/email.txt` is a file containing the
email message to be scanned:

**Request**

```sh
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -F 'metadata=@metadata.json;type=application/json' \
     -F 'data=@/path/to/some/email.txt' \
     https://${ATLANT_HOST}:${ATLANT_SCAN_PORT}/api/scan/v1
```

**Response**

```json
{
  "scan_result": "spam",
  "detections": [
    {
      "category": "spam",
      "name": "Email_Spam"
    }
  ],
  "warnings": {
    "corrupted": false,
    "encrypted": false,
    "max_nested": false,
    "max_results": false,
    "max_scan_time": false,
    "need_content": false
  },
  "status": "complete"
}
```

In this case, the `scan_result` property of the response indicates that the
message was classified as spam.

### Scanning a File with a Hash of its Contents

Atlant can also try to detect if a file is malicious based only on its SHA1
hash. In this mode, the actual file content does not need to be transferred over
to the Atlant instance. All analysis steps can not be performed without having
the file contents available, if Atlant cannot classify the file using only its
hash, the response to the scan request will have `warnings` object's
`need_content` property set to `true`. This indicates that the client should do
a full scan by sending the actual file contents to Atlant for scanning.

In this example, we scan a file using only its SHA1 hash by including it into
the `sha1` property inside the `content_meta` object. We leave out the second
part of the multipart scan request, as we want to scan only using the metadata
we provided, without sending the actual file contents over to Atlant.

**metadata.json**

```json
{
    "content_meta": {
        "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    }
}
```

**Request**

```sh
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -F 'metadata=@metadata.json;type=application/json' \
     https://${ATLANT_HOST}:${ATLANT_SCAN_PORT}/api/scan/v1
```

**Response**

```json
{
  "scan_result": "whitelisted",
  "detections": [],
  "warnings": {
    "corrupted": false,
    "encrypted": false,
    "max_nested": false,
    "max_results": false,
    "max_scan_time": false,
    "need_content": false
  },
  "status": "complete"
}
```

In the response, Atlant classified the file as whitelisted. It is confident in
its classification as the `need_content` warning is not set.

### Classifying URLs

Atlant can also classify URLs into categories based on their content. To
classify a URL, include it in the `uri` property inside `content_meta` object
when making the scan request.

**metadata.json**

```json
{
    "content_meta": {
        "uri": "https://google.com"
    }
}
```

**Request**

```sh
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -F 'metadata=@metadata.json;type=application/json' \
     https://${ATLANT_HOST}:${ATLANT_SCAN_PORT}/api/scan/v1
```

Atlant will classify the URL and provide a list of categories assigned to it in
the `uri_categories` property of the response. This property might not always be
present if category information for the URL is not available.

**Response**

```json
{
  "scan_result": "clean",
  "detections": [],
  "uri_categories": [
    "search_engines"
  ],
  "warnings": {
    "corrupted": false,
    "encrypted": false,
    "max_nested": false,
    "max_results": false,
    "max_scan_time": false,
    "need_content": true
  },
  "status": "complete"
}
```

[manual]: https://help.f-secure.com/product.html#business/atlant/latest/en/concept_0C321E9CB5994555A9B0A0B793DD5E98-latest-en
[manual-system-requirements]: https://help.f-secure.com/product.html#business/atlant/latest/en/concept_FE8EDD82C8954CD2AF8A0546131B6E86-latest-en
[atlant-download]: https://www.withsecure.com/en/support/product-support/atlant#download
