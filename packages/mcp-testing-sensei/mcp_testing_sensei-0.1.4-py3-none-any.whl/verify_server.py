#!/usr/bin/env python3
"""Verify the MCP server can start without the MCP client SDK."""

import subprocess
import sys
import time


def verify_server_starts():
    """Check if the MCP server can start successfully."""
    print("Attempting to start MCP server...")

    # Try to start the server
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give it a moment to start
    time.sleep(2)

    # Check if it's still running
    if process.poll() is None:
        print("✓ Server is running!")
        print("  The server is waiting for JSON-RPC input on stdin")
        process.terminate()
        process.wait()
        return True
    else:
        # Server crashed
        stdout, stderr = process.communicate()
        print("✗ Server failed to start")
        if stderr:
            print(f"Error output:\n{stderr}")
        return False


def check_imports():
    """Check if we can import the necessary modules."""
    print("Checking module imports...")

    try:
        import linter  # noqa: F401
        print("✓ linter module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import linter: {e}")
        return False

    try:
        # Try importing MCP
        import mcp  # noqa: F401
        print("✓ mcp module imported successfully")
        from mcp.server.fastmcp import FastMCP  # noqa: F401
        print("✓ FastMCP imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import MCP: {e}")
        print("\nTo run the server, you need to install MCP:")
        print("  pip install mcp")
        print("Or use the nix develop environment")
        return False


def main():
    """Run verification checks."""
    print("MCP Server Verification")
    print("=" * 50)

    # First check imports
    if not check_imports():
        print("\n⚠️  Cannot verify server without MCP module")
        return

    print()

    # Then try to start the server
    if verify_server_starts():
        print("\n✅ Server verification successful!")
        print("\nThe MCP stdio server is ready to use.")
        print("It can be integrated with MCP clients like Claude Desktop.")
    else:
        print("\n❌ Server verification failed!")


if __name__ == "__main__":
    main()
