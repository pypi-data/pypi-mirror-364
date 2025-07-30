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

## Getting Started

### Prerequisites

*   [Nix](https://nixos.org/download/) (for reproducible development environment)

### Development Environment Setup

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

### Using with MCP Clients

The server can be integrated with MCP-compatible clients like Claude Desktop or other tools that support the Model Context Protocol.

#### Example configuration for Claude Desktop

Add the following to your Claude Desktop configuration:

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

#### Testing the Server

You can test the MCP server using the included test script:

```bash
python test_mcp_integration.py
```

This will send JSON-RPC messages to the server and display the responses.

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

```
