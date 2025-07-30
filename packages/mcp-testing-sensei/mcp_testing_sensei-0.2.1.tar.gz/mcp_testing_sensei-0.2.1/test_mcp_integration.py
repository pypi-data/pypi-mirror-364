#!/usr/bin/env python3
"""Test script for the MCP stdio server."""

import asyncio
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print('Error: MCP module not found. Please run this in the nix develop environment.')
    sys.exit(1)


async def test_mcp_server():
    """Test the MCP server using the MCP client SDK."""
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(command=sys.executable, args=['mcp_server.py'], env=None)

    try:
        print('Starting MCP server...')
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                print('Initializing connection...')
                await session.initialize()
                print('✓ Connection initialized')

                # List available tools
                print('\nListing available tools...')
                tools = await session.list_tools()
                print(f'✓ Found {len(tools.tools)} tools:')
                for tool in tools.tools:
                    print(f'  - {tool.name}: {tool.description}')

                # List available resources
                print('\nListing available resources...')
                resources = await session.list_resources()
                print(f'✓ Found {len(resources.resources)} resources:')
                for resource in resources.resources:
                    print(f'  - {resource.uri}: {resource.name}')

                # Test lint_code tool
                print('\nTesting lint_code tool...')
                test_code = """def test_example():
    if True:
        pass"""

                result = await session.call_tool('lint_code', arguments={'code': test_code})
                print('✓ lint_code result:')
                print(f'  {result.content[0].text}')

                # Test get_testing_principles tool
                print('\nTesting get_testing_principles tool...')
                result = await session.call_tool('get_testing_principles', arguments={})
                print('✓ get_testing_principles result:')
                print(f'  {result.content[0].text}')

                print('\n✅ All tests passed!')
                return True

    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the async test."""
    success = asyncio.run(test_mcp_server())
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
