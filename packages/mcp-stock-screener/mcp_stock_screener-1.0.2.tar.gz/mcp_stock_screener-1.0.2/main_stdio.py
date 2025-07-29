#!/usr/bin/env python3
"""
Smart Stock Screener MCP Server - Stdio Transport
Entry point for running the MCP server via stdio (recommended for most MCP clients)
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.mcp_server import create_mcp_server
from src.config.settings import settings

def main():
    """Run MCP server with stdio transport."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Override transport setting for stdio
    settings.transport = "stdio"
    
    try:
        server = create_mcp_server()
        server.run_stdio()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()