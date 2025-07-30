#!/usr/bin/env python3
"""MCP Testing Sensei - Stdio Server Implementation."""

from mcp.server.fastmcp import FastMCP

import linter

# Create the MCP server
mcp = FastMCP("Testing Sensei")


@mcp.tool()
def lint_code(code: str) -> dict:
    """Lint a snippet of unit test code and return a list of any violations.

    Args:
        code: The unit test code to analyze

    Returns:
        A dictionary containing violations found in the code
    """
    violations = linter.check_test_code(code)
    return {"violations": violations}


@mcp.tool()
def get_testing_principles() -> dict:
    """Retrieve the core principles for writing effective unit tests.

    Returns:
        A dictionary containing the testing principles
    """
    principles = [
        "Tests should be written before implementation.",
        "Tests should document the behavior of the system under test.",
        "Tests should be small, clearly written, and have a single concern.",
        (
            "Tests should be deterministic and isolated from the side effects of "
            "their environment and other Tests."
        ),
        "Tests should be written in a declarative manner and never have branching logic.",
    ]
    return {"principles": principles}


@mcp.resource("file:///unit-testing-principles.md")
def get_principles_resource() -> str:
    """Provide unit testing principles as a resource."""
    principles = [
        "Tests should be written before implementation.",
        "Tests should document the behavior of the system under test.",
        "Tests should be small, clearly written, and have a single concern.",
        (
            "Tests should be deterministic and isolated from the side effects of "
            "their environment and other Tests."
        ),
        "Tests should be written in a declarative manner and never have branching logic.",
    ]
    return "\n".join(f"- {principle}" for principle in principles)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
