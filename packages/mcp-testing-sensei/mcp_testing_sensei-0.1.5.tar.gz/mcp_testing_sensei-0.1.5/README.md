# MCP Testing Sensei

This project implements an MCP (Model Context Protocol) stdio server designed to enforce and guide agentic coding tools (like Gemini CLI or Claude Code) in adhering to language agnostic unit testing principles.

## Core Principles Enforced

This tool aims to promote the following unit testing principles:

*   **Tests should be written before implementation.** (BDD/TDD for the win)
*   **Tests should document the behavior of the system under test.**
*   **Tests should be small, clearly written, and have a single concern.**
*   **Tests should be deterministic and isolated from the side effects of their environment and other tests.**
*   **Tests should be written in a declarative manner and never have branching logic.**

## Features

*   **`lint_code` tool**: Analyzes provided code snippets for violations of the defined unit testing standards.
*   **`get_testing_principles` tool**: Provides the core unit testing principles to guide LLMs in generating better tests.
*   **`unit-testing-principles` resource**: Exposes testing principles as an MCP resource.

## Installation

### Option 1: Install from PyPI (Recommended)

The easiest way to install MCP Testing Sensei is via pip:

```bash
pip install mcp-testing-sensei
```

This installs the `mcp-testing-sensei` command globally.

### Option 2: Install from npm

If you prefer using npm:

```bash
npm install -g @kourtni/mcp-testing-sensei
```

Note: This still requires Python to be installed on your system.

### Option 3: Using Docker

```bash
docker pull kourtni/mcp-testing-sensei
```

### Option 4: Development Setup with Nix

For development or if you want to build from source:

#### Prerequisites

*   [Nix](https://nixos.org/download/) (for reproducible development environment)

#### Development Environment Setup

To enter the development environment with all dependencies:

```bash
nix develop
```

### Building the Standalone Executable

To build the standalone executable using Nix, run the following command:

```bash
nix build
```

This will create a `result` symlink in your project root, pointing to the built executable.

### Running the Server

#### Using the Standalone Executable

After building, you can run the MCP stdio server directly from the `result` symlink:

```bash
./result/bin/mcp-testing-sensei
```

This will start the MCP server that communicates via standard input/output.

#### Running from Development Environment

Alternatively, if you are in the `nix develop` shell, you can run the MCP server:

```bash
python mcp_server.py
```

The server communicates via stdio, reading JSON-RPC messages from stdin and writing responses to stdout.

## Using with MCP Clients

The server can be integrated with MCP-compatible clients like Claude Desktop or other tools that support the Model Context Protocol.

### Configuration for Claude Desktop

#### If installed via pip:

```json
{
  "mcpServers": {
    "testing-sensei": {
      "command": "mcp-testing-sensei"
    }
  }
}
```

#### If installed via npm:

```json
{
  "mcpServers": {
    "testing-sensei": {
      "command": "npx",
      "args": ["@kourtni/mcp-testing-sensei"]
    }
  }
}
```

#### If using Docker:

```json
{
  "mcpServers": {
    "testing-sensei": {
      "command": "docker",
      "args": ["run", "-i", "kourtni/mcp-testing-sensei"]
    }
  }
}
```

#### If running from source:

```json
{
  "mcpServers": {
    "testing-sensei": {
      "command": "python",
      "args": ["/path/to/mcp-testing-sensei/mcp_server.py"]
    }
  }
}
```

### Testing the Server

To verify the server is working correctly, you can use the integration test script:

```bash
# For development testing
python test_mcp_integration.py
```

This will:
- Start the MCP server
- Send test requests to verify the tools are working
- Display the responses

The server itself doesn't have a standalone test mode - it's designed to be used with MCP clients.

## Development

### Running Tests

To run the unit tests locally, first ensure you are in the Nix development environment:

```bash
nix develop
```

Then, execute `pytest`:

```bash
pytest
```

## Project Structure

```
flake.lock
flake.nix
linter.py           # Core linting logic
mcp_server.py       # MCP stdio server implementation
main.py             # Legacy HTTP server (can be removed)
pyproject.toml
test_mcp_integration.py  # Integration test script for the MCP server
tests/
    test_linter.py  # Unit tests for the linter logic
```

## Contributing

Contributions are welcome! Please ensure your changes adhere to the established unit testing principles and project conventions.

## Additional Documentation

- [DISTRIBUTION.md](DISTRIBUTION.md) - Detailed guide for all distribution methods
- [RELEASE.md](RELEASE.md) - Release process and version management
