# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Flowscale Python SDK is a client library for interacting with the FlowScale ComfyUI API. It provides a simple Python interface for executing workflows, managing runs, and retrieving outputs from the FlowScale platform.

## Architecture

### Core Components

- **FlowscaleAPI** (`flowscale/api.py`): Main client class that handles all API interactions
- **Type Definitions** (`flowscale/types.py`): TypedDict definitions for all API request/response structures
- **Package Initialization** (`flowscale/__init__.py`): Exports the main FlowscaleAPI class

### Key Design Patterns

- Uses `requests` library for HTTP communication with X-API-KEY header authentication
- Implements automatic file handling for workflow inputs (supports file paths, file objects, and regular values)
- Provides both synchronous (`execute_workflow`) and asynchronous (`execute_workflow_async`) workflow execution
- Uses TypedDict for type safety without runtime overhead

## Development Commands

### Project Setup
```bash
uv sync                    # Install dependencies and create virtual environment
uv sync --dev             # Install development dependencies
```

### Code Quality
```bash
uv run ruff check flowscale/     # Run linting
uv run ruff format flowscale/    # Run formatting
uv run ruff check --fix flowscale/ # Auto-fix linting issues
```

### Building the Package
```bash
uv build                  # Build package using uv (preferred)
```

### Publishing
```bash
uv publish               # Publish to PyPI using uv
```

### Installation for Development
```bash
uv pip install -e .      # Install in development mode
```

### Running Commands
```bash
uv run python <script>    # Run Python scripts in the project environment
```

## Environment Setup

The SDK requires two environment variables:
- `FLOWSCALE_API_KEY`: API key for authentication
- `FLOWSCALE_API_URL`: Base URL for the API endpoint

## Key API Methods

1. **Health & Queue Management**
   - `check_health()`: Check ComfyUI instance health
   - `get_queue()`: Get current workflow queue status

2. **Workflow Execution**
   - `execute_workflow(workflow_id, data, group_id=None)`: Execute workflow immediately
   - `execute_workflow_async(workflow_id, data, group_id=None, timeout=300, polling_interval=1)`: Execute and wait for completion

3. **Run Management**
   - `get_output(filename)`: Retrieve workflow output by filename
   - `cancel_run(run_id)`: Cancel running workflow
   - `get_run(run_id)`: Get detailed run information
   - `get_runs(group_id=None)`: List runs by group or all runs

## File Handling

The SDK automatically handles different input types:
- File objects (with `.read()` method) → direct upload
- File paths (strings that are valid file paths) → automatic file opening
- Regular values → form data

## Dependencies

- `requests>=2.25.0` (only runtime dependency)  
- `ruff>=0.12.4` (development dependency for linting and formatting)
- Python 3.10+ required

## Project Management

The project uses `uv` for modern Python project management:
- Dependencies are managed in `pyproject.toml`
- Virtual environment is automatically created and managed
- Build backend uses `hatchling`
- Code quality enforced with `ruff` for both linting and formatting

## Package Structure

```
flowscale/
├── __init__.py     # Package exports
├── api.py          # Main FlowscaleAPI class
└── types.py        # Type definitions
```

The codebase follows a simple, focused structure with minimal dependencies and clear separation of concerns between API logic, type definitions, and package initialization.