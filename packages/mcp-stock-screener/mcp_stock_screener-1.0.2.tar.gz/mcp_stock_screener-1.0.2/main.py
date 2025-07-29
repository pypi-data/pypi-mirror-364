#!/usr/bin/env python3
"""
Smart Stock Screener MCP Server
Main entry point for the MCP server.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.mcp_server import create_mcp_server

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        from src.config.settings import settings
        server = create_mcp_server()
        transport = settings.transport.lower()
        
        if transport == "stdio":
            server.run_stdio()
        elif transport == "http":
            server.run_http()
        elif transport == "both":
            # Only use asyncio.run for the 'both' transport case
            asyncio.run(server.run_both())
        else:
            logging.error(f"Unknown transport: {transport}. Use 'stdio', 'http', or 'both'")
            sys.exit(1)
                
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)