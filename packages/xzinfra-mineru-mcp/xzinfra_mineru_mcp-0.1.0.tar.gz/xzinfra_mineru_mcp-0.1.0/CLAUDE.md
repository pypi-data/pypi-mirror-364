# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python MCP (Model Context Protocol) server that provides document conversion services by integrating with MinerU. It converts various document formats (PDF, Word, PPT, images) to Markdown and JSON using a self-hosted MinerU service.

## Architecture

The codebase follows a simple FastMCP-based architecture:

- `src/xzinfra_mineru_mcp/cli.py` - CLI entry point with argument parsing for allowed paths
- `src/xzinfra_mineru_mcp/server.py` - FastMCP server implementation with MinerU document conversion tools
- `src/xzinfra_mineru_mcp/config.py` - Configuration management for MinerU API endpoints and allowed paths
- `pyproject.toml` - Python project configuration using hatchling build system

## Development Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Or using uv (preferred, as evidenced by uv.lock)
uv pip install -e .
```

### Running the Server
```bash
# Run the MCP server
xzinfra-mineru-mcp

# Run with specific allowed paths
xzinfra-mineru-mcp --allowed /path/to/documents --allowed /another/path
```

## Environment Variables

Required environment variables:
- `SELF_MINERU_BASE_URL` - Base URL for the self-hosted MinerU service
- `SELF_MINERU_API_KEY` - API key for authentication with MinerU service

## MCP Tools

The server provides the following MCP tools for document processing:
- `get_ocr_languages` - Get supported OCR languages
- `find_document_path` - Search for files in configured document directories  
- `parse_documents` - Parse local documents and extract content

## FastMCP Integration

This project uses FastMCP framework for MCP server implementation. The server runs in stdio mode and handles document conversion requests through the MinerU API integration.

see fastmcp-doc.md to use FastMCP  framework