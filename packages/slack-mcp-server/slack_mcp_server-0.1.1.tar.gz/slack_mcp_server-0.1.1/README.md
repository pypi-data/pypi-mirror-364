# Slack MCP Server

A Model Context Protocol (MCP) server for Slack workspace integration using FastMCP with HTTP transport and multiuser support.

## Features

### Tools
- **conversations_history** - Get messages from channels/DMs with pagination
- **conversations_replies** - Get thread messages with pagination  
- **conversations_add_message** - Post messages to channels/DMs (safety disabled by default)
- **conversations_search_messages** - Search messages with advanced filters
- **channels_list** - List all channels with sorting options

### Resources
- **slack://workspace/channels** - CSV directory of all channels with metadata
- **slack://workspace/users** - CSV directory of all users with metadata

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables
- `SLACK_MCP_XOXP_TOKEN` - Slack bot token (xoxb-) or user token (xoxp-)

### Optional Environment Variables
- `SLACK_MCP_ADD_MESSAGE_TOOL` - Enable message posting:
  - Not set = disabled (default for safety)
  - `true` or `1` = enabled for all channels
  - Comma-separated channel IDs = enabled only for specific channels

## Usage

### Start HTTP Server
```bash
python slack_mcp_server.py
```

Server runs on `http://0.0.0.0:8000/mcp` by default.

### Authentication
For multiuser support, pass the Slack token in request headers:
```
SLACK_MCP_XOXP_TOKEN: xoxb-your-slack-token
```

Optional message posting control via headers:
```
SLACK_MCP_ADD_MESSAGE_TOOL: true
```

Alternatively, set `SLACK_MCP_XOXP_TOKEN` environment variable for single-user mode.

## API Examples

### Get Channel History
```json
{
  "method": "conversations_history",
  "params": {
    "channel_id": "#general",
    "limit": "1d",
    "include_activity_messages": false
  }
}
```

### Search Messages
```json
{
  "method": "conversations_search_messages", 
  "params": {
    "search_query": "project update",
    "filter_in_channel": "#general",
    "filter_users_from": "@john",
    "limit": 50
  }
}
```

### Get Channels Directory
```json
{
  "method": "resource",
  "params": {
    "uri": "slack://myworkspace/channels"
  }
}
```

## Slack Permissions

Required scopes for your Slack app:
- **channels:history** - Read public channel messages
- **groups:history** - Read private channel messages  
- **im:history** - Read direct messages
- **mpim:history** - Read group direct messages
- **channels:read** - List public channels
- **groups:read** - List private channels
- **users:read** - List workspace users
- **chat:write** - Post messages (if enabled)

## Security

- Message posting disabled by default for safety
- Token-based authentication for multiuser support
- No secrets logged or committed to repository
- Follows Slack API rate limits and best practices