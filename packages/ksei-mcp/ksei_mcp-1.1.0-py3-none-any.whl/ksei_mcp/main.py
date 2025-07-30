#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Any, Sequence

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Import your existing KSEI client
import os

from .ksei_client import Client, FileAuthStore, PortfolioType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ksei-mcp")

server = Server("ksei-mcp")

# Global client instance
client: Client = None

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available KSEI resources"""
    return [
        Resource(
            uri="ksei://portfolio/summary",
            name="Portfolio Summary",
            description="Get portfolio summary with total value and breakdown by asset type",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/cash",
            name="Cash Balances",
            description="Get cash balances across all accounts",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/equity",
            name="Equity Holdings",
            description="Get equity/stock holdings",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/mutual-fund",
            name="Mutual Fund Holdings", 
            description="Get mutual fund holdings",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/bond",
            name="Bond Holdings",
            description="Get bond holdings",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://account/identity",
            name="Account Identity",
            description="Get global identity information",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read KSEI resource data"""
    if not client:
        raise ValueError("KSEI client not initialized. Use configure_auth tool first.")
    
    try:
        if uri == "ksei://portfolio/summary":
            data = client.get_portfolio_summary()
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        elif uri == "ksei://portfolio/cash":
            data = client.get_cash_balances()
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        elif uri == "ksei://portfolio/equity":
            data = client.get_share_balances(PortfolioType.EQUITY)
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        elif uri == "ksei://portfolio/mutual-fund":
            data = client.get_share_balances(PortfolioType.MUTUAL_FUND)
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        elif uri == "ksei://portfolio/bond":
            data = client.get_share_balances(PortfolioType.BOND)
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        elif uri == "ksei://account/identity":
            data = client.get_global_identity()
            return json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        raise RuntimeError(f"Failed to read resource: {str(e)}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available KSEI tools"""
    return [
        Tool(
            name="configure_auth",
            description="Configure KSEI authentication credentials",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "KSEI username/email"
                    },
                    "password": {
                        "type": "string", 
                        "description": "KSEI password"
                    },
                    "auth_store_path": {
                        "type": "string",
                        "description": "Path to store auth tokens (optional)",
                        "default": "./auth_store"
                    }
                },
                "required": ["username", "password"]
            }
        ),
        Tool(
            name="get_portfolio_summary",
            description="Get portfolio summary with total value and asset breakdown",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_cash_balances", 
            description="Get cash balances across all accounts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_holdings",
            description="Get holdings for specific asset type",  
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_type": {
                        "type": "string",
                        "enum": ["equity", "mutual_fund", "bond", "other"],
                        "description": "Type of asset holdings to retrieve"
                    }
                },
                "required": ["asset_type"]
            }
        ),
        Tool(
            name="get_account_info",
            description="Get account identity information",
            inputSchema={
                "type": "object", 
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle KSEI tool calls"""
    global client
    
    try:
        if name == "configure_auth":
            # Only allow if not already configured
            if client:
                return [TextContent(type="text", text="KSEI client already configured")]
            
            username = arguments.get("username")
            password = arguments.get("password") 
            auth_store_path = arguments.get("auth_store_path", "./auth_store")
            
            if not username or not password:
                raise ValueError("Username and password are required")
            
            auth_store = FileAuthStore(directory=auth_store_path)
            client = Client(auth_store=auth_store, username=username, password=password)
            
            return [TextContent(type="text", text="KSEI authentication configured successfully")]
        
        if not client:
            raise ValueError("KSEI client not initialized. Use configure_auth tool first.")
        
        if name == "get_portfolio_summary":
            data = client.get_portfolio_summary()
            result = json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_cash_balances":
            data = client.get_cash_balances()
            result = json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_holdings":
            asset_type = arguments.get("asset_type")
            type_mapping = {
                "equity": PortfolioType.EQUITY,
                "mutual_fund": PortfolioType.MUTUAL_FUND, 
                "bond": PortfolioType.BOND,
                "other": PortfolioType.OTHER
            }
            
            portfolio_type = type_mapping.get(asset_type)
            if not portfolio_type:
                raise ValueError(f"Invalid asset type: {asset_type}")
            
            data = client.get_share_balances(portfolio_type)
            result = json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_account_info":
            data = client.get_global_identity()
            result = json.dumps(data.__dict__, default=lambda o: o.__dict__, indent=2)
            return [TextContent(type="text", text=result)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

def load_config():
    """Load configuration from environment or config file"""
    global client
    
    # Try environment variables first
    username = os.getenv("KSEI_USERNAME")
    password = os.getenv("KSEI_PASSWORD")
    
    if username and password:
        auth_store = FileAuthStore(directory=os.getenv("KSEI_AUTH_PATH", "./auth_store"))
        client = Client(auth_store=auth_store, username=username, password=password)
        logger.info("KSEI client configured from environment")
        return
    
    # Try config file
    config_paths = [
        os.path.expanduser("~/.config/ksei-mcp/config.json"),
        "./config.json"
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                
                creds = config.get("credentials", {})
                username = creds.get("username")
                password = creds.get("password")
                
                if username and password:
                    auth_path = config.get("auth_store_path", "./auth_store")
                    auth_store = FileAuthStore(directory=os.path.expanduser(auth_path))
                    client = Client(auth_store=auth_store, username=username, password=password)
                    logger.info(f"KSEI client configured from {config_path}")
                    return
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

async def main():
    # Load configuration on startup
    load_config()
    
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ksei-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def run():
    asyncio.run(main())