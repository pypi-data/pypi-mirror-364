#!/usr/bin/env python3
"""Manual test for the MCP server - requires mcp module."""

import json
import subprocess
import sys
import time


def send_request(process, request):
    """Send a JSON-RPC request and read the response."""
    request_str = json.dumps(request)
    print(f'\n→ Sending: {request_str}')
    process.stdin.write(request_str + '\n')
    process.stdin.flush()

    # Give the server time to process
    time.sleep(0.1)

    # Read response
    response_line = process.stdout.readline()
    if response_line:
        response = json.loads(response_line)
        print(f'← Response: {json.dumps(response, indent=2)}')
        return response
    return None


def main():
    """Run manual tests against the MCP server."""
    print('Starting MCP server for manual testing...')

    # Start the server
    process = subprocess.Popen(
        [sys.executable, 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Give server time to start
        time.sleep(0.5)

        # Check if server started properly
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f'Server failed to start: {stderr}')
            return

        print('Server started successfully!')

        # Test 1: Send initialize request
        init_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2025-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'manual-test', 'version': '1.0.0'},
            },
        }
        send_request(process, init_request)

        # Test 2: List tools
        list_tools = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}
        send_request(process, list_tools)

        # Test 3: Call lint_code
        lint_code = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'lint_code',
                'arguments': {'code': 'def test_example():\n    if True:\n        pass'},
            },
        }
        send_request(process, lint_code)

        print('\n✓ Manual test completed!')

    except Exception as e:
        print(f'\n✗ Test failed: {e}')
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        process.terminate()
        process.wait()
        print('\nServer stopped.')


if __name__ == '__main__':
    main()
