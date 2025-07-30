#!/usr/bin/env python3
"""
Slack MCP Server using FastMCP

A Model Context Protocol server for Slack workspace integration with multiuser support.
Provides tools for conversations and resources for workspace metadata.
"""

import os
import csv
import io
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

# Initialize FastMCP server
mcp = FastMCP("Slack MCP Server")

class SlackClient:
    """Slack Web API client with token-based authentication"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Slack API"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        
        if response.status_code != 200:
            raise Exception(f"Slack API error: {response.status_code} - {response.text}")
            
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Slack API error: {data.get('error', 'Unknown error')}")
            
        return data

def get_slack_client() -> SlackClient:
    """Get Slack client from request context or environment"""
    # First try to get token from HTTP headers
    headers = get_http_headers()
    token = headers.get("SLACK_MCP_XOXP_TOKEN") or headers.get("slack_mcp_xoxp_token")
    
    # Fall back to environment variable
    if not token:
        token = os.environ.get("SLACK_MCP_XOXP_TOKEN")
    
    if not token:
        raise Exception("SLACK_MCP_XOXP_TOKEN not provided in headers or environment")
    return SlackClient(token)

def parse_limit(limit_str: str, default_days: int = 1) -> Dict[str, Any]:
    """Parse limit parameter into API parameters"""
    if not limit_str:
        return {"limit": 100}
    
    # Check if it's a time-based limit (e.g., "1d", "1w", "30d")
    if limit_str.endswith(('d', 'w')):
        if limit_str.endswith('d'):
            days = int(limit_str[:-1])
        elif limit_str.endswith('w'):
            days = int(limit_str[:-1]) * 7
        
        # Convert to timestamp
        oldest_ts = (datetime.now() - timedelta(days=days)).timestamp()
        return {"oldest": str(oldest_ts), "limit": 1000}
    
    # Numeric limit
    try:
        return {"limit": min(int(limit_str), 1000)}
    except ValueError:
        return {"limit": 100}

@mcp.tool
def conversations_history(
    channel_id: str,
    include_activity_messages: bool = False,
    cursor: Optional[str] = None,
    limit: str = "1d"
) -> Dict[str, Any]:
    """
    Get messages from the channel (or DM) by channel_id
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @...
        include_activity_messages: If true, include activity messages like channel_join/leave
        cursor: Cursor for pagination
        limit: Limit of messages - time format (1d, 1w, 30d) or number (50)
    """
    client = get_slack_client()
    
    params = {
        "channel": channel_id,
        "include_all_metadata": include_activity_messages
    }
    
    if cursor:
        params["cursor"] = cursor
    else:
        # Apply limit only when cursor is not provided
        limit_params = parse_limit(limit)
        params.update(limit_params)
    
    data = client._make_request("conversations.history", params)
    
    return {
        "messages": data.get("messages", []),
        "has_more": data.get("has_more", False),
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def conversations_replies(
    channel_id: str,
    thread_ts: str,
    include_activity_messages: bool = False,
    cursor: Optional[str] = None,
    limit: str = "1d"
) -> Dict[str, Any]:
    """
    Get a thread of messages posted to a conversation by channelID and thread_ts
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or name starting with #... or @...
        thread_ts: Unique identifier of thread's parent message (timestamp format 1234567890.123456)
        include_activity_messages: If true, include activity messages like channel_join/leave
        cursor: Cursor for pagination
        limit: Limit of messages - time format (1d, 1w, 30d) or number (50)
    """
    client = get_slack_client()
    
    params = {
        "channel": channel_id,
        "ts": thread_ts,
        "include_all_metadata": include_activity_messages
    }
    
    if cursor:
        params["cursor"] = cursor
    else:
        # Apply limit only when cursor is not provided
        limit_params = parse_limit(limit)
        params.update(limit_params)
    
    data = client._make_request("conversations.replies", params)
    
    return {
        "messages": data.get("messages", []),
        "has_more": data.get("has_more", False),
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def conversations_add_message(
    channel_id: str,
    payload: str,
    thread_ts: Optional[str] = None,
    content_type: str = "text/markdown"
) -> Dict[str, Any]:
    """
    Add a message to a public channel, private channel, or direct message
    
    Note: Posting messages is disabled by default for safety. 
    Set SLACK_MCP_ADD_MESSAGE_TOOL environment variable to enable.
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or name starting with #... or @...
        payload: Message payload in specified content_type format
        thread_ts: Optional thread timestamp to reply to (format 1234567890.123456)
        content_type: Content type of message (text/markdown or text/plain)
    """
    # Check if message posting is enabled (check headers first, then environment)
    headers = get_http_headers()
    add_message_setting = (
        headers.get("SLACK_MCP_ADD_MESSAGE_TOOL") or 
        headers.get("slack_mcp_add_message_tool") or
        os.environ.get("SLACK_MCP_ADD_MESSAGE_TOOL")
    )
    if not add_message_setting:
        raise Exception("Message posting is disabled. Set SLACK_MCP_ADD_MESSAGE_TOOL in headers or environment to enable.")
    
    # If setting contains channel IDs, check if this channel is allowed
    if add_message_setting != "1" and add_message_setting.lower() != "true":
        allowed_channels = [ch.strip() for ch in add_message_setting.split(",")]
        if channel_id not in allowed_channels:
            raise Exception(f"Message posting not allowed for channel {channel_id}")
    
    client = get_slack_client()
    
    # Convert markdown to Slack format if needed
    text = payload
    if content_type == "text/markdown":
        # Basic markdown to Slack conversion
        text = text.replace("**", "*").replace("__", "_")
    
    params = {
        "channel": channel_id,
        "text": text
    }
    
    if thread_ts:
        params["thread_ts"] = thread_ts
    
    # Use POST for chat.postMessage
    url = f"{client.base_url}/chat.postMessage"
    response = requests.post(url, headers=client.headers, json=params)
    
    if response.status_code != 200:
        raise Exception(f"Slack API error: {response.status_code} - {response.text}")
        
    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error', 'Unknown error')}")
    
    return {
        "message": data.get("message", {}),
        "ts": data.get("ts"),
        "channel": data.get("channel")
    }

@mcp.tool
def conversations_search_messages(
    search_query: Optional[str] = None,
    filter_in_channel: Optional[str] = None,
    filter_in_im_or_mpim: Optional[str] = None,
    filter_users_with: Optional[str] = None,
    filter_users_from: Optional[str] = None,
    filter_date_before: Optional[str] = None,
    filter_date_after: Optional[str] = None,
    filter_date_on: Optional[str] = None,
    filter_date_during: Optional[str] = None,
    filter_threads_only: bool = False,
    cursor: str = "",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search messages in conversations using filters
    
    Args:
        search_query: Search query to filter messages or full URL of Slack message
        filter_in_channel: Filter messages in specific channel by ID or name (#general)
        filter_in_im_or_mpim: Filter messages in DM/MPIM by ID or name (@username_dm)
        filter_users_with: Filter messages with specific user by ID or display name
        filter_users_from: Filter messages from specific user by ID or display name
        filter_date_before: Filter messages before date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_after: Filter messages after date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_on: Filter messages on specific date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_during: Filter messages during period (July, Yesterday, Today)
        filter_threads_only: If true, include only messages from threads
        cursor: Cursor for pagination
        limit: Maximum number of items to return (1-100)
    """
    client = get_slack_client()
    
    if not search_query and not any([filter_in_channel, filter_in_im_or_mpim, filter_users_with, filter_users_from]):
        raise Exception("search_query is required when no filters are provided")
    
    # Check if search_query is a Slack URL
    if search_query and "slack.com/archives/" in search_query:
        # Extract channel and timestamp from URL
        # Format: https://slack.com/archives/C1234567890/p1234567890123456
        parts = search_query.split('/')
        if len(parts) >= 6:
            channel_id = parts[-2]
            ts_part = parts[-1]
            if ts_part.startswith('p'):
                # Convert permalink timestamp to message timestamp
                ts = ts_part[1:]  # Remove 'p' prefix
                ts = f"{ts[:10]}.{ts[10:]}"  # Insert decimal point
                
                # Get single message
                params = {"channel": channel_id, "ts": ts, "limit": 1}
                data = client._make_request("conversations.history", params)
                return {
                    "messages": data.get("messages", []),
                    "total": len(data.get("messages", [])),
                    "next_cursor": None
                }
    
    # Build search query with filters
    query_parts = []
    if search_query:
        query_parts.append(search_query)
    
    if filter_in_channel:
        query_parts.append(f"in:{filter_in_channel}")
    if filter_in_im_or_mpim:
        query_parts.append(f"in:{filter_in_im_or_mpim}")
    if filter_users_with:
        query_parts.append(f"with:{filter_users_with}")
    if filter_users_from:
        query_parts.append(f"from:{filter_users_from}")
    if filter_date_before:
        query_parts.append(f"before:{filter_date_before}")
    if filter_date_after:
        query_parts.append(f"after:{filter_date_after}")
    if filter_date_on:
        query_parts.append(f"on:{filter_date_on}")
    if filter_date_during:
        query_parts.append(f"during:{filter_date_during}")
    
    if filter_threads_only:
        query_parts.append("has:thread")
    
    query = " ".join(query_parts)
    
    params = {
        "query": query,
        "count": min(max(limit, 1), 100),
        "sort": "timestamp"
    }
    
    if cursor:
        params["cursor"] = cursor
    
    data = client._make_request("search.messages", params)
    
    messages = data.get("messages", {})
    return {
        "messages": messages.get("matches", []),
        "total": messages.get("total", 0),
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def channels_list(
    channel_types: str,
    sort: Optional[str] = None,
    limit: int = 100,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of channels
    
    Args:
        channel_types: Comma-separated channel types (mpim,im,public_channel,private_channel)
        sort: Type of sorting (popularity - sort by number of members/participants)
        limit: Maximum number of items to return (1-1000, max 999)
        cursor: Cursor for pagination
    """
    client = get_slack_client()
    
    # Validate channel types
    valid_types = {"mpim", "im", "public_channel", "private_channel"}
    types = [t.strip() for t in channel_types.split(",")]
    
    for t in types:
        if t not in valid_types:
            raise Exception(f"Invalid channel type: {t}. Valid types: {', '.join(valid_types)}")
    
    params = {
        "types": channel_types,
        "limit": min(max(limit, 1), 999)
    }
    
    if cursor:
        params["cursor"] = cursor
    
    data = client._make_request("conversations.list", params)
    
    channels = data.get("channels", [])
    
    # Sort by popularity if requested
    if sort == "popularity":
        channels.sort(key=lambda x: x.get("num_members", 0), reverse=True)
    
    return {
        "channels": channels,
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.resource("slack://{workspace}/channels")
def get_channels_directory(workspace: str) -> str:
    """
    Directory of Channels - CSV format with channel metadata
    
    Args:
        workspace: Slack workspace name
    
    Returns:
        CSV directory of all channels in the workspace
    """
    client = get_slack_client()
    
    # Get all channel types
    all_channels = []
    for channel_type in ["public_channel", "private_channel", "im", "mpim"]:
        try:
            data = client._make_request("conversations.list", {
                "types": channel_type,
                "limit": 999
            })
            all_channels.extend(data.get("channels", []))
        except Exception:
            continue  # Skip if no permission for certain channel types
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["id", "name", "topic", "purpose", "memberCount"])
    
    # Write channel data
    for channel in all_channels:
        name = channel.get("name", "")
        if channel.get("is_im"):
            name = f"@{name}_dm"
        elif channel.get("is_mpim"):
            name = f"@{name}_group"
        elif name:
            name = f"#{name}"
        
        writer.writerow([
            channel.get("id", ""),
            name,
            channel.get("topic", {}).get("value", ""),
            channel.get("purpose", {}).get("value", ""),
            channel.get("num_members", 0)
        ])
    
    return output.getvalue()

@mcp.resource("slack://{workspace}/users")
def get_users_directory(workspace: str) -> str:
    """
    Directory of Users - CSV format with user metadata
    
    Args:
        workspace: Slack workspace name
    
    Returns:
        CSV directory of all users in the workspace
    """
    client = get_slack_client()
    
    # Get all users
    data = client._make_request("users.list", {"limit": 999})
    users = data.get("members", [])
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["userID", "userName", "realName"])
    
    # Write user data
    for user in users:
        if not user.get("deleted", False):  # Skip deleted users
            writer.writerow([
                user.get("id", ""),
                user.get("name", ""),
                user.get("real_name", "")
            ])
    
    return output.getvalue()


def main():
    """Main entry point for the slack-mcp-server command."""
    # Run server with HTTP transport
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )

if __name__ == "__main__":
    main()