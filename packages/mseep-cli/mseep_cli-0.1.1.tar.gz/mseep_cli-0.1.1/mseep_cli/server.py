import asyncio
import argparse
import json
import urllib.request
import urllib.parse
import urllib.error
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Global variables to be set by command line arguments
SERVER_NAME = None
CLIENT = None
server = Server("mseep-cli")

async def _make_get_request(url: str) -> dict:
    """Make an async GET request using urllib"""
    def _sync_get():
        try:
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode())
                error_message = error_data.get('error', 'Unknown error')
            except:
                error_message = 'Unknown error'
            raise Exception(f"{error_message}. HTTP {e.code}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")

    return await asyncio.to_thread(_sync_get)

async def _make_post_request(url: str, payload: dict) -> dict:
    """Make an async POST request using urllib"""
    def _sync_post():
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode())
                error_message = error_data.get('error', 'Unknown error')
            except:
                error_message = 'Unknown error'
            raise Exception(f"{error_message}. HTTP {e.code}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")

    return await asyncio.to_thread(_sync_post)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Connects to the MseeP desktop app to get the list of tools.
    """
    try:
        # Get available tools of the server from the mseep app
        server_name_encoded = urllib.parse.quote(SERVER_NAME)
        data = await _make_get_request(f'http://localhost:9001/list-tools?server_name={server_name_encoded}&client={CLIENT}')

        tools = data.get('tools', [])
        return [
            types.Tool(
                name=tool['name'],
                description=tool['description'],
                inputSchema=tool['input_schema'],
            )
            for tool in tools
        ]
    except Exception as e:
        raise e


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool calling requests.
    """
    if not arguments:
        arguments = {}

    try:
        # Run the tool via the claude-desktop endpoint
        payload = {
            'tool': name,
            'server': SERVER_NAME,
            'client': CLIENT,
            'args': arguments
        }

        data = await _make_post_request('http://localhost:9001/run-tool', payload)
        result = data.get('result', '')
        return _format_result(result)

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error running tool: {str(e)}")]

def _format_result(result) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle different result formats
    """
    if isinstance(result, list):
        # If result is a list, format each item and combine the results into a list
        return [_format_item(item) for item in result]

    return [_format_item(result)]

def _format_item(item) -> types.TextContent | types.ImageContent | types.EmbeddedResource:
    if isinstance(item, dict) and item.get('type'):
        if item.get('type') == 'text':
            return types.TextContent(type="text", text=item.get('text', ''))
    elif isinstance(item, str):
        if item.startswith('data:image/'):
            return types.ImageContent(type="image", mimeType="image/png", data=item)

    return types.TextContent(type="text", text=str(item))

def start_server(server_name: str):
    """Start the MCP server with given parameters."""
    global SERVER_NAME, CLIENT

    SERVER_NAME = server_name
    # Extract client from server name prefix (e.g., "claude/skydeckai/skydeckai-code" -> "claude")
    CLIENT = server_name.split('/')[0] if '/' in server_name else "genstudio"

    async def async_main():
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=server_name,
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(async_main())

def main():
    """Entry point for the proxy-server command."""
    # Parse command line arguments with subcommands
    parser = argparse.ArgumentParser(
        description="MCP Proxy Server - Proxies requests to the desktop app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using uvx (recommended for PyPI package)
  uvx mseep-cli start --server-name "claude/skydeckai/skydeckai-code"

  # Direct python execution
  python -m mseep_cli.server start --server-name "claude/skydeckai/skydeckai-code"
  python -m mseep_cli.server start -s "genstudio/my-server"
        """
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start the MCP server')
    start_parser.add_argument(
        "--server-name", "-s",
        type=str,
        default="genstudio/skydeckai-code",
        help="Name of the MCP server (default: %(default)s)"
    )

    args = parser.parse_args()

    if args.command == 'start':
        start_server(args.server_name)
    else:
        parser.print_help()

# This is needed if you'd like to connect to a custom client
if __name__ == "__main__":
    main()
