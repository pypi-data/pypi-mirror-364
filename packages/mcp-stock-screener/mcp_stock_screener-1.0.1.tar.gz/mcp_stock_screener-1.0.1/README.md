# Smart Stock Screener MCP Server

An AI-powered financial analysis system that processes natural language queries and returns structured stock analysis results via MCP (Model Context Protocol).

## Features

- **Natural Language Queries**: Screen stocks using plain English
  - "Find momentum stocks with RSI under 30"
  - "Show me tech stocks with market cap over $1B"
  - "What are oversold healthcare stocks?"

- **Comprehensive Analysis**: Get detailed stock analysis with AI insights
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Sentiment Analysis**: News and social media sentiment scoring
- **Health Monitoring**: System component health checks

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Choose Your Transport Mode**

   **Option A: Stdio Transport (Default)**
   ```bash
   python main.py
   ```

   **Option B: HTTP Transport (Streamable HTTP)**
   ```bash
   python main_http.py
   ```
   Server available at: `http://localhost:8080/mcp`

   **Option C: Configure via Environment**
   ```bash
   export MCP_TRANSPORT=http
   python main.py
   ```

3. **Test with MCP Client**
   The server exposes three MCP tools:
   - `stock_screener`: Natural language stock screening
   - `stock_analysis`: Detailed individual stock analysis  
   - `system_health`: System health monitoring

## MCP Tools

### stock_screener
Screen stocks using natural language queries.

**Input:**
```json
{
  "query": "Find momentum stocks with RSI under 30"
}
```

**Output:**
```json
{
  "matches": [...],
  "total_results": 15,
  "query": "Find momentum stocks with RSI under 30",
  "execution_time": 0.245,
  "confidence": 0.85,
  "criteria_used": {...}
}
```

### stock_analysis
Get comprehensive analysis for a specific stock.

**Input:**
```json
{
  "symbol": "AAPL"
}
```

**Output:**
```json
{
  "stock_data": {...},
  "analysis": {
    "technical_score": 78.5,
    "trend_direction": "bullish",
    "confidence": 0.82,
    "reasoning": "AAPL is currently trading at $190.25 with RSI at 65.2..."
  },
  "historical_context": {...},
  "peer_comparison": ["MSFT", "GOOGL", "NVDA"]
}
```

### system_health
Check system component health.

**Output:**
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy", "response_time_ms": 12},
    "cache": {"status": "healthy", "hit_rate": 0.85},
    "ai_models": {"status": "healthy", "xgboost_loaded": true}
  }
}
```

## Development

### Running Tests
```bash
pytest tests/unit/
```

### HTTP Client Examples

**Using curl to test the HTTP endpoint:**
```bash
# Test health check
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "system_health",
      "arguments": {}
    }
  }'

# Test stock screening
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "stock_screener",
      "arguments": {
        "query": "Find tech stocks with RSI under 30"
      }
    }
  }'
```

**Using Python client:**
```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_mcp_http():
    async with streamablehttp_client("http://localhost:8080/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            
            # Call stock screener tool
            result = await session.call_tool(
                "stock_screener", 
                arguments={"query": "Find momentum stocks with RSI under 30"}
            )
            print(result)

asyncio.run(test_mcp_http())
```

### Query Examples

The system supports various query patterns:

**Market Cap Filters:**
- "large cap stocks" (>$10B)
- "market cap over $5 billion"
- "small cap between $300M and $2B"

**Technical Indicators:**
- "RSI under 30" (oversold)
- "RSI between 40 and 60"
- "bullish MACD"
- "overbought stocks"

**Sectors:**
- "tech stocks"
- "healthcare companies"
- "financial sector"

**Stock Types:**
- "momentum stocks"
- "value plays"
- "dividend stocks"
- "penny stocks"

**Sentiment:**
- "positive sentiment"
- "strong bullish sentiment"

**Volume:**
- "high volume stocks"
- "volume over 10 million"

## Architecture

The system follows the architecture outlined in the project specifications:

- **MCP Interface**: Natural language API using MCP SDK
- **Query Processor**: Parses natural language into structured criteria
- **Mock Data Provider**: Generates realistic test data for development
- **Configuration Management**: Environment-based settings
- **Error Handling**: Comprehensive error responses with suggestions

## Configuration

Settings can be configured via environment variables or `.env` file:

```bash
# Database
QUESTDB_HOST=localhost
QUESTDB_PORT=8812

# Cache  
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Performance
MAX_SCREENING_RESULTS=500
QUERY_TIMEOUT=30
```

## Next Steps

This MCP implementation provides the foundation for the Smart Stock Screener system. To complete the full system:

1. **Database Integration**: Replace mock data with QuestDB integration
2. **Real Data Sources**: Connect Alpha Vantage, Polygon.io APIs
3. **ML Models**: Implement XGBoost, LSTM, and BERT models
4. **Caching Layer**: Add Redis for performance optimization
5. **Production Deployment**: Add monitoring, logging, security features

## Performance Targets

- Stock screening queries: <500ms (95th percentile)
- Individual stock analysis: <200ms (95th percentile)  
- Support 1000+ concurrent screening requests
- 99.9% uptime during market hours

The current mock implementation demonstrates the MCP interface and query processing capabilities that will be used with the production data pipeline.