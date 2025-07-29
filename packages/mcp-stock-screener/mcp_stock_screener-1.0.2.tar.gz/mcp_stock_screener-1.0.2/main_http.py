#!/usr/bin/env python3
"""
Smart Stock Screener MCP Server - HTTP Transport
Entry point for running the MCP server via Streamable HTTP on localhost:8080/mcp
"""

import asyncio
import sys
import logging
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.mcp_server import create_mcp_server
from src.config.settings import settings

def main():
    """Run MCP server with HTTP transport."""
    parser = argparse.ArgumentParser(description="Smart Stock Screener MCP Server - HTTP Transport")
    parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       help="Log level (default: INFO)")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Override transport setting for HTTP
    settings.transport = "http"
    
    try:
        server = create_mcp_server()
        logging.info(f"Starting HTTP server on {args.host}:{args.port}")
        server.run_http(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()