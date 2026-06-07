---
title: "HPE GreenLake MCP Servers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/mcp-server/public.md"
scraped_at: "2026-06-07T06:13:19.834595+00:00Z"
---

# HPE GreenLake MCP Servers

A collection of [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers that enable AI assistants to interact with HPE GreenLake cloud services.

## What is the Model Context Protocol?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need.

## HPE GreenLake MCP server GitHub repository

Visit the [HPE GreenLake MCP servers repository](https://github.com/hewlettPackard/gl-mcp) for an up-to-date listing of the HPE GreenLake services with MCP server support along with information on installation, configuration, and useful code samples.

## Overview

An MCP server is a service that implements the Model Context Protocol to expose specific resources, tools, or data sources to AI assistants. It acts as a bridge between AI models and external systems, allowing for:

### Key features

- **Standardized architecture**: All servers follow consistent patterns for authentication, configuration, and error handling
- **OAuth2 authentication**: Secure access using HPE GreenLake workspace credentials with automatic token management
- **Dual tool modes**: Each server supports both static (individual tools per endpoint) and dynamic (meta-tools) operation modes
- **Type-safe**: Built with Pydantic models for runtime validation and type safety
- **Production ready**: Comprehensive logging, error handling, and Docker support
- **Well tested**: Extensive unit and integration test coverage


### Local MCP servers

At this time, HPE GreenLake MCP servers support **local deployment only**. The servers run on customer environment, providing secure, read-only access to HPE GreenLake cloud services.

**Benefits of local MCP servers:**

- **Development & testing**: Perfect for local development, testing, and debugging
- **Data privacy**: Keep sensitive credentials and workspace data on your local machine
- **Low latency**: Minimal network overhead for faster response times
- **Resource control**: Direct control over server resources and configuration


## Available MCP servers

### Infrastructure and platform management

#### Devices

Manage and query HPE GreenLake devices in your workspace. Filter devices by type, serial number, tags, and other properties.

**Key capabilities:**

- Retrieve device lists with advanced filtering
- Get detailed device information by ID
- Query devices by tags, device type, serial number, and more


#### Workspaces

Interact with HPE GreenLake workspace management APIs. View workspace details and manage workspace-level configurations.

**Key capabilities:**

- List and query workspaces
- Retrieve workspace details and configurations
- Access workspace-level settings


#### Service Catalog

Browse and query HPE GreenLake service offers, service provisions, and service managers in your workspace.

**Key capabilities:**

- List and filter service offers and service offer regions
- Retrieve service provision details for a workspace
- Query service managers and service manager provisions by region


#### Subscriptions

Access subscription information and licensing details for your HPE GreenLake services.

**Key capabilities:**

- View active subscriptions
- Query subscription details and licensing
- Monitor subscription status


### Security and compliance

#### Audit Logs

Query and analyze HPE GreenLake audit logs with powerful filtering capabilities.

**Key capabilities:**

- Search audit logs by category, user, timestamp, and more
- Filter logs using advanced query operators (eq, contains, in)
- Retrieve detailed audit log information
- Track user activities and system events


### User and access management

#### Users

Manage user accounts and access controls in HPE GreenLake workspaces.

**Key capabilities:**

- List and query workspace users
- View user details and permissions
- Monitor user activity


### Analytics and reporting

#### Reporting

Access HPE GreenLake reporting data and monitor report statuses for your workspace.

**Key capabilities:**

- Retrieve report export metadata including supported columns, filter criteria, and operators
- Fetch status of all reports for a workspace with pagination support
- Retrieve the status of a specific report by ID


## Getting started with MCP servers

HPE GreenLake MCP servers run locally on customer environment, providing secure read-only access to HPE GreenLake workspace. The servers act as a bridge between AI assistants and HPE GreenLake cloud services, allowing customers to query devices, audit logs, subscriptions, and other resources without modifying any data.

1. [Downloading prerequisite software](#downloading-prerequisite-software)
2. [Gathering the required credentials](#gathering-the-required-credentials)
3. [Installing an MCP server](#installing-an-mcp-server)
4. [Configuring an MCP client](#configuring-an-mcp-client)


### Downloading prerequisite software

You must download and configure the following software before you can use HPE GreenLake cloud MCP servers.

- Python 3.10 or higher, see the following to [download Python](https://www.python.org/downloads/).
- The uv package manager, which is a fast Python package installer. See the following to [get UV](https://github.com/astral-sh/uv).
- An MCP client of your choice. See [Example Clients](https://modelcontextprotocol.io/clients). This documentation uses Claude Desktop as an example, but HPE GreenLake cloud MCP servers will work with all MCP clients.
- An integration development environment, such as Microsoft Visual Studio.


### Gathering the required credentials

**Prerequisites:**

You need an HPE GreenLake account and workspace. See [Getting started with HPE GreenLake cloud](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-497192AA-FDC2-49C5-B572-0D2F58A23745.html).

**About this task:**

Before creating your MCP server, you need to gather an HPE GreenLake workspace ID, the client ID, and the client secret from a personal API client.

If you already have the credentials
If you already have and know your workspace ID, client ID, and client secret, you can skip this task.

**Procedure:**

1. Log in to HPE GreenLake and select a workspace.
2. On the HPE GreenLake cloud header, click the workspace menu and then select **Manage Workspace**. The Workspace ID is listed under your name. Make a note or copy this ID.
3. From **Manage Workspace**, click **Personal API clients**.
4. From **Personal API clients**, click on an existing API client to view the **Client ID**.
5. If you do not know the client secret, there are three options to generate a new one.


- Use the UI: see [Creating a personal API client](/assets/_generate-glcp-access-token.c9040080c656241094df1bf740fde08af9f1c5e8fc1f17e0fba0a9982208fe74.52cee7a9.md) or [Resetting your client secret](/assets/_generate-glcp-access-token.c9040080c656241094df1bf740fde08af9f1c5e8fc1f17e0fba0a9982208fe74.52cee7a9.md)
- Use the [API Client Credentials API](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public).


Copy the client ID and secret
Take note or copy the client ID and secret.

### Installing an MCP server

**Prerequisites:**

- Ensure you have installed the required [prerequisite software](#downloading-prerequisite-software).
- Complete [Gathering the required credentials](#gathering-the-required-credentials).


**About this task:**

Install and configure an MCP server for AI assistant integration.

**Procedure:**

1. Clone the MCP server with `git clone https://github.com/hewlettPackard/gl-mcp`.
2. Navigate to the directory of your chosen service.
Generic example:

```bash

cd src/{INSERT SERVICE}
```
Subscriptions example:

```bash

cd src/subscriptions
```
3. Install dependencies with the command `uv sync`.
4. Configure environment variables. See the example shell command below (Linux/macOS). You need to provide the specific information for the credential information (`GREENLAKE_CLIENT_ID`, `GREENLAKE_CLIENT_SECRET`, and `GREENLAKE_WORKSPACE_ID`). Refer to the [Environment variables](#environment-variables) for more information.

```bash

cat > .env.local << EOF
GREENLAKE_API_BASE_URL=https://global.api.greenlake.hpe.com
GREENLAKE_CLIENT_ID={your-client-id}
GREENLAKE_CLIENT_SECRET={your-client-secret}
GREENLAKE_WORKSPACE_ID={your-workspace-id}
EOF
```
5. Test the server startup using the command `make test`.
6. Verify authentication by checking console output for successful OAuth2 token acquisition, tool registration completion, and no authentication errors. The MCP server is installed and ready for integration with AI assistants.


HPE GreenLake cloud MCP servers repository
View the [HPE GreenLake cloud MCP servers repository](https://github.com/hewlettPackard/gl-mcp) for specific and detailed code samples for all available services.

### Configuring an MCP client

**Prerequisites:**

- Complete the steps in [Installing an MCP server](#installing-an-mcp-server).
- Complete the steps in [Gathering the required credentials](#gathering-the-required-credentials).
- Download and install an MCP client.


**About this task:**

This procedure shows an example of adding an MCP server to Claude Desktop. However, HPE GreenLake cloud MCP servers will work with any MCP client (refer to their documentation).

**Procedure:**

1. Locate the Claude Desktop configuration file, `claude_desktop_config.json`.
2. Add your chosen MCP server configuration. You need to provide the specific information for `cwd` (the path to your server) as well as the credential information (`GREENLAKE_CLIENT_ID`, `GREENLAKE_CLIENT_SECRET`, and `GREENLAKE_WORKSPACE_ID`).

```json
{
"mcpServers": {
    "greenlake-subscriptions": {
      "command": "uv",
      "args": ["run", "python", "__main__.py"],
      "cwd": "C:\\path\\to\\gl-mcp\\src\\subscriptions",
      "env": {
        "GREENLAKE_API_BASE_URL": "https://global.api.greenlake.hpe.com",
        "GREENLAKE_CLIENT_ID": "your-client-id",
        "GREENLAKE_CLIENT_SECRET": "your-client-secret",
        "GREENLAKE_WORKSPACE_ID": "your-workspace-id"
    }
    }
}
}
```
3. Restart Claude Desktop by completely closing the application and restarting it.
4. Verify the MCP server appears in the available tools.


### Switching tools mode

**About this task:**

Configure your MCP server to use static or dynamic tool modes based on your use case.

- Use static mode (recommended for production) for standard workflows, type-safe operations with validation, clear tool discoverability in MCP clients, and optimal performance for known operations.
- Use dynamic mode (recommended for development) for exploring new subscription API endpoints, flexible schema discovery, development and testing scenarios, and unknown or changing API requirements.


**Procedure:**

1. Set the environment variable.
  - Static mode: `export MCP_TOOL_MODE=static`
  - Dynamic mode: `export MCP_TOOL_MODE=dynamic`
2. Update configuration files by adding the mode to your MCP client configuration.

```json
"env": {

"MCP_TOOL_MODE": "static"

}
```
3. Restart the server.
4. Verify the mode change by checking available tools in your MCP client. Static mode shows the name of the API endpoints available. Dynamic mode shows `list_endpoints`, `get_endpoint_schema`, and `invoke_dynamic_tool`.


| Tool | Description |
|  --- | --- |
| `list_endpoints` | Used to discover available API endpoints with optional filtering |
| `get_endpoint_schema` | Used to get detailed schema information for specific endpoints |
| `invoke_dynamic_tool` | Execute API calls with runtime parameter validation |


### Environment variables

| Variable | Required | Description | Example |
|  --- | --- | --- | --- |
| `GREENLAKE_API_BASE_URL` | Yes | The base URL for HPE GreenLake APIs | `https://global.api.greenlake.hpe.com` |
| `GREENLAKE_CLIENT_ID` | Yes | The OAuth2 client ID | `12345678-1234-4567-8901-123456789abc` |
| `GREENLAKE_CLIENT_SECRET` | Yes | The OAuth2 client secret | `1234567890abcdef1234567890abcdef` |
| `GREENLAKE_WORKSPACE_ID` | Yes | The unique identifier of an HPE GreenLake workspace | `12345678-1234-4567-8901-123456789abc` |
| `GREENLAKE_TOKEN_ISSUER` | No | The OAuth2 token endpoint | Auto-generated if not provided |
| `MCP_TOOL_MODE` | No | The tools operation mode | `static` (default) or `dynamic` |
| `GREENLAKE_LOG_LEVEL` | No | The logging level for stderr output | `ERROR` (default), `WARNING`, `INFO`, `DEBUG` |
| `GREENLAKE_FILE_LOGGING` | No | Enable file logging to disk | `false` (default) or `true` |


## Architecture overview

### Shared components

All servers share a common architecture:


```text
server/
├── __main__.py           # Entry point
├── auth/                 # OAuth2 authentication
├── config/               # Settings and logging
├── models/               # Pydantic data models
├── server/               # MCP server core
├── tools/                # Tool implementations
│   ├── base.py          # Base tool class
│   ├── registry.py      # Tool registration
│   └── implementations/ # Tool implementations
├── utils/                # HTTP client and utilities
└── tests/                # Unit and integration tests
```

### Authentication

All servers use OAuth2 client credentials flow with automatic token management:

- Tokens are cached and automatically refreshed
- Thread-safe token management
- Configurable retry logic with exponential backoff


### Logging

Servers use structured logging with MCP protocol compliance:

- **stderr**: Diagnostic logs (controlled by `GREENLAKE_LOG_LEVEL`)
- **File logging**: Optional detailed logging to `~/.hpe/mcp-logs/`
- **stdout**: Reserved for JSON-RPC messages only


## Security considerations

- **Read-only access**: All servers provide read-only API access by design
- **Local operation**: MCP servers run entirely on customer environment
- **Credential management**: Never commit credentials to version control
- **Token security**: OAuth2 tokens are cached in memory only
- **Workspace isolation**: Operations are scoped to the configured workspace
- **HTTPS only**: All API communications use TLS encryption


## Troubleshooting

### Common issues

**Server won't start:**

- Verify all required environment variables are set
- Check that `uv` is installed and dependencies are synced
- Review stderr output for configuration errors


**Authentication failures:**

- Verify client credentials are valid for your workspace
- Ensure `GREENLAKE_WORKSPACE_ID` matches your credential scope
- Check network connectivity to GreenLake APIs


**MCP client connection issues:**

- Verify the `cwd` path in client configuration is correct
- Check that the server starts successfully when run manually
- Review client logs for specific error messages


### Debug Logging

Enable detailed logging for troubleshooting:


```bash
export GREENLAKE_LOG_LEVEL=DEBUG
export GREENLAKE_FILE_LOGGING=true
```

Log files are written to: `~/.hpe/mcp-logs/{service-name}/`

## Support and documentation

For support, use GitHub Issues for bug reports or feature requests, and GitHub Discussions for general inquiries.

## Resources

- [HPE GreenLake API Documentation](https://developer.greenlake.hpe.com/docs/greenlake/services)
- [HPE GreenLake MCP servers repository](https://github.com/hewlettPackard/gl-mcp)
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)


## License

This project is licensed under the Apache 2.0 - see the LICENSE file for details.