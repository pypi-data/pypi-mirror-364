"""Legacy HTTP server implementation (deprecated - use mcp_server.py instead)."""

import argparse

import fastapi
import pydantic
import uvicorn

import linter

app = fastapi.FastAPI()


class LintRequest(pydantic.BaseModel):
    """Request body for the /lint endpoint."""

    code: str


@app.post('/lint')
async def lint_code(request: LintRequest):
    """Lints a snippet of unit test code and returns a list of any violations."""
    return {'violations': linter.check_test_code(request.code)}


@app.get('/.well-known/model-context-protocol')
async def get_mcp_discovery():
    """Return the Model Context Protocol discovery information."""
    return {
        'name': 'Testing Sensei',
        'description': (
            'An MCP server to enforce/guide agentic coding tools to use general testing standards.'
        ),
        'tools': [
            {
                'name': 'lint_code',
                'description': (
                    'Lints a snippet of unit test code and returns a list of any '
                    'violations of our defined standards.'
                ),
                'input_schema': {
                    'type': 'object',
                    'properties': {'code': {'type': 'string', 'description': 'The code to lint.'}},
                    'required': ['code'],
                },
                'output_schema': {
                    'type': 'object',
                    'properties': {'violations': {'type': 'array', 'items': {'type': 'string'}}},
                },
            },
            {
                'name': 'get_testing_principles',
                'description': 'Retrieves the core principles for writing effective unit tests.',
                'input_schema': {'type': 'object', 'properties': {}},
                'output_schema': {
                    'type': 'object',
                    'properties': {'principles': {'type': 'array', 'items': {'type': 'string'}}},
                },
            },
        ],
    }


@app.get('/testing-principles')
async def get_testing_principles():
    """Return the core principles for writing effective unit tests."""
    principles = [
        'Tests should be written before implementation.',
        'Tests should document the behavior of the system under test.',
        'Tests should be small, clearly written, and have a single concern.',
        (
            'Tests should be deterministic and isolated from the side effects of '
            'their environment and other Tests.'
        ),
        'Tests should be written in a declarative manner and never have branching logic.',
    ]
    return {'principles': principles}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run MCP Testing Sensei FastAPI application.')
    parser.add_argument(
        '--port', type=int, default=8181, help='Port to run the FastAPI application on.'
    )
    args = parser.parse_args()

    uvicorn.run(app, host='0.0.0.0', port=args.port)
