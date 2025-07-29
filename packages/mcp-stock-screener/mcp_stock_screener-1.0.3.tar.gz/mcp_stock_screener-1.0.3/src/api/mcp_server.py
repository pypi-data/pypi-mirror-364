"""MCP server implementation for Smart Stock Screener."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..config.settings import settings
from .mock_data import MockDataProvider
from .models import (
    DetailedAnalysis,
    HealthCheck,
    ScreeningResult,
)
from .query_processor import QueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartStockScreenerMCP:
    """MCP server for Smart Stock Screener functionality using FastMCP."""

    def __init__(self):
        # Try to configure FastMCP with custom settings
        import os
        os.environ["HOST"] = settings.http.host
        os.environ["PORT"] = str(settings.http.port)
        
        self.mcp = FastMCP("smart-stock-screener")
        self.query_processor = QueryProcessor()
        self.mock_data = MockDataProvider()
        self.start_time = datetime.now(timezone.utc)

        # Register MCP tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tools using FastMCP decorators."""

        @self.mcp.tool()
        async def stock_screener(query: str) -> ScreeningResult:
            """Screen stocks using natural language queries.

            Examples:
            - "Find momentum stocks with RSI under 30"
            - "Show me tech stocks with strong earnings growth"
            - "What are the best value plays in healthcare?"
            """
            try:
                result = await self._handle_stock_screening({"query": query})
                logger.info(f"Tool returning result with {result.total_results} matches")
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                # Return a minimal valid result to test
                from .models import ScreeningCriteria
                return ScreeningResult(
                    matches=[],
                    total_results=0,
                    query=query,
                    execution_time=0.0,
                    confidence=0.0,
                    criteria_used=ScreeningCriteria()
                )

        @self.mcp.tool()
        async def stock_analysis(symbol: str) -> DetailedAnalysis:
            """Get comprehensive analysis for a specific stock symbol with AI-powered insights and predictions.

            Args:
                symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
            """
            return await self._handle_stock_analysis({"symbol": symbol})

        @self.mcp.tool()
        async def system_health() -> HealthCheck:
            """Check the health status of all system components including database, cache, and AI models."""
            return await self._handle_health_check({})

    async def _handle_stock_screening(
        self, arguments: dict[str, Any]
    ) -> ScreeningResult:
        """Handle stock screening requests."""
        logger.info(f"Received stock screening request: {arguments}")
        query = arguments.get("query", "").strip()

        if not query:
            raise ValueError(
                "Query cannot be empty. Try: 'Find momentum stocks with RSI under 30'"
            )

        try:
            # Process natural language query
            start_time = datetime.now(timezone.utc)
            criteria = await self.query_processor.parse_query(query)

            # Execute screening (using mock data for now)
            matching_stocks = self.mock_data.screen_stocks(criteria)
            logger.info(f"Mock data returned {len(matching_stocks)} stocks")

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Format response
            result = ScreeningResult(
                matches=matching_stocks,
                total_results=len(matching_stocks),
                query=query,
                execution_time=round(execution_time, 4),
                confidence=0.85,  # Mock confidence score
                criteria_used=criteria,
            )

            logger.info(f"Returning screening result: {result.total_results} matches found")
            
            # Debug: Log the result structure to identify validation issues
            try:
                result_dict = result.model_dump()
                logger.info(f"Result structure validation successful")
            except Exception as e:
                logger.error(f"Result validation error: {e}")
                logger.error(f"Result data: {result}")
                
            return result

        except Exception as e:
            logger.exception(f"Error in stock screening: {e}")
            raise ValueError(
                f"Failed to process screening query: {str(e)}. Try a simpler query or check if stock symbols are valid."
            )

    async def _handle_stock_analysis(
        self, arguments: dict[str, Any]
    ) -> DetailedAnalysis:
        """Handle individual stock analysis requests."""
        logger.info(f"Received stock analysis request: {arguments}")
        symbol = arguments.get("symbol", "").upper().strip()

        if not symbol or len(symbol) > 5:
            raise ValueError(
                "Invalid stock symbol format. Use valid ticker symbols like AAPL, GOOGL, TSLA"
            )

        try:
            # Get comprehensive analysis (using mock data for now)
            analysis = await self.mock_data.analyze_stock(symbol)
            return analysis

        except Exception as e:
            logger.exception(f"Error in stock analysis for {symbol}: {e}")
            raise ValueError(
                f"Failed to analyze stock {symbol}: {str(e)}. Check if the stock symbol exists or try again later."
            )

    async def _handle_health_check(self, arguments: dict[str, Any]) -> HealthCheck:
        """Handle system health check requests."""
        logger.info(f"Received health check request: {arguments}")
        try:
            uptime = int((datetime.now(timezone.utc) - self.start_time).total_seconds())

            # Mock health check data
            health_data = HealthCheck(
                status="healthy",
                timestamp=datetime.now(timezone.utc),
                uptime_seconds=uptime,
                components={
                    "database": {
                        "status": "healthy",
                        "response_time_ms": 12,
                        "connections": 5,
                    },
                    "cache": {
                        "status": "healthy",
                        "hit_rate": 0.85,
                        "memory_usage": "45%",
                    },
                    "ai_models": {
                        "status": "healthy",
                        "xgboost_loaded": True,
                        "lstm_loaded": True,
                        "bert_loaded": True,
                    },
                    "data_pipeline": {
                        "status": "healthy",
                        "last_update": "2024-01-15T10:30:00Z",
                        "symbols_tracked": 5000,
                    },
                },
            )

            return health_data

        except Exception as e:
            logger.exception(f"Error in health check: {e}")
            raise ValueError(f"Failed to check system health: {str(e)}")

    def run_stdio(self):
        """Run the MCP server using stdio transport."""
        logger.info(f"Starting {settings.app_name} v{settings.version} (stdio)")
        self.mcp.run(transport="stdio")

    def run_http(self):
        """Run the MCP server using streamable HTTP transport."""
        logger.info(f"Starting {settings.app_name} v{settings.version} (HTTP)")
        # Note: FastMCP currently defaults to port 8000, not the configured port
        logger.info(
            f"Server will be available at http://127.0.0.1:8000{settings.http.mount_path}"
        )
        logger.info(f"(Configured for {settings.http.host}:{settings.http.port}, but FastMCP uses port 8000)")
        logger.info("Available tools: stock_screener, stock_analysis, system_health")

        # Configure for stateful HTTP server
        # FastMCP.run() doesn't accept host/port parameters directly
        self.mcp.run(transport="streamable-http")

    async def run_both(self):
        """Run both stdio and HTTP transports concurrently."""
        logger.info(
            f"Starting {settings.app_name} v{settings.version} (both transports)"
        )
        logger.info(
            f"HTTP endpoint: http://{settings.http.host}:{settings.http.port}{settings.http.mount_path}"
        )
        logger.info("Stdio: Ready for stdin/stdout communication")

        # Create tasks for both transports
        tasks = []

        # HTTP transport task
        async def http_task():
            self.mcp.run(transport="streamable-http")

        # Stdio transport task
        async def stdio_task():
            self.mcp.run(transport="stdio")

        # Note: In practice, you might want to run these in separate processes
        # For now, we'll just run HTTP since stdio blocks
        await http_task()


def create_mcp_server() -> SmartStockScreenerMCP:
    """Factory function to create MCP server instance."""
    return SmartStockScreenerMCP()


async def main():
    """Main entry point for the MCP server."""
    server = create_mcp_server()

    transport = settings.transport.lower()

    if transport == "stdio":
        server.run_stdio()
    elif transport == "http":
        server.run_http()
    elif transport == "both":
        await server.run_both()
    else:
        logger.error(f"Unknown transport: {transport}. Use 'stdio', 'http', or 'both'")
        raise ValueError(f"Invalid transport setting: {transport}")


if __name__ == "__main__":
    asyncio.run(main())
