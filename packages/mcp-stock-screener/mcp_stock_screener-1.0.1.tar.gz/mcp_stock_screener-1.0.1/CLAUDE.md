# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **pre-implementation startup project** for "Smart Stock Screener" - an AI-powered financial analysis system that processes natural language queries and returns structured stock analysis results. The project is currently in the specification phase with comprehensive documentation but no source code yet.

## Key Architecture Decisions

**Technology Stack (Planned)**:
- **Database**: QuestDB for high-performance time-series data (4.3M rows/sec proven throughput)
- **Caching**: Redis for sub-second response times
- **Backend**: Python with ML model integration (XGBoost, LSTM, BERT)
- **API**: MCP SDK for natural language interface
- **Data Sources**: Alpha Vantage, Polygon.io, news sentiment feeds, SEC filings

**Performance Requirements**:
- Stock screening queries: <500ms (95th percentile)
- Individual stock analysis: <200ms (95th percentile)
- Support 1000+ concurrent screening requests
- 99.9% uptime during market hours

## Critical Development Guidance

### 1. MVP Simplification is Essential
The current specifications describe a complex system with 23 implementation tasks across 6 phases. **STRONGLY RECOMMEND focusing on a simplified MVP first**:
- Single data source integration (not multiple APIs)
- Basic technical indicators (RSI, moving averages only)
- Simple query parsing (not full NLP)
- One ML model maximum for initial version

### 2. Financial Compliance Requirements
This is a **financial technology project** with specific requirements:
- Follow FINRA guidelines for financial data handling
- Implement audit logging for all system actions
- No storage of personally identifiable information (PII)
- TLS 1.3 for all API communications
- API key-based authentication required

### 3. Database Schema Foundation
When implementing QuestDB integration, use this proven schema design:
```sql
-- Primary market data table
CREATE TABLE market_data (
    timestamp TIMESTAMP,
    symbol SYMBOL CAPACITY 10000 CACHE,
    price DOUBLE,
    volume LONG,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    market_cap DOUBLE
) timestamp(timestamp) PARTITION BY DAY WAL;
```

### 4. MCP API Interface Pattern
The system uses MCP tools for natural language interface:
```python
@mcp_tool("stock_screener")
async def screen_stocks(query: str) -> ScreeningResult:
    """
    Process natural language stock screening queries.
    Examples: "Find momentum stocks with RSI under 30"
    """
```

## Project Structure Guidelines

When creating the project structure, follow this pattern:
```
src/
├── data/           # QuestDB integration and data pipeline
├── analysis/       # ML models and technical indicators
├── api/           # MCP interface and request handling
└── config/        # Configuration and environment management

tests/
├── unit/          # Component tests (80% coverage minimum)
├── integration/   # End-to-end workflow tests
└── performance/   # Load testing for response time requirements

config/
├── database.yaml  # QuestDB connection settings
├── redis.yaml     # Cache configuration
└── models.yaml    # ML model configurations
```

## Testing Strategy

- **Unit Tests**: 80% minimum code coverage requirement
- **Performance Tests**: Validate <500ms response time requirement
- **Integration Tests**: End-to-end API workflow testing
- **Security Tests**: Financial compliance validation

## Development Commands (To be implemented)

```bash
# Development environment setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Database operations
python -m src.data.setup_questdb  # Initialize QuestDB schema
python -m src.data.migrate        # Run database migrations

# Testing
pytest tests/unit/               # Run unit tests with coverage
pytest tests/performance/        # Run performance benchmarks
pytest tests/integration/        # Run end-to-end tests

# API development
python -m src.api.server         # Start MCP server for development
python -m src.api.test_queries   # Test natural language query processing
```

## Important Considerations

### Over-Engineering Risk
The specifications are comprehensive but may be over-engineered for an MVP. Consider implementing in this order:
1. **Phase 1**: Basic QuestDB + Redis + simple MCP endpoint
2. **Phase 2**: Single data source + basic screening
3. **Phase 3**: Add ML models incrementally
4. **Phase 4**: Scale to full specification

### Financial Data Handling
- All market data must be validated before storage
- Implement circuit breaker pattern for external API calls
- Cache frequently accessed data with appropriate TTLs
- Log all financial data access for compliance auditing

### Performance Monitoring
Set up monitoring for:
- Query response times (target <500ms)
- Model prediction accuracy (target >75%)
- Cache hit rates
- Error rates by component
- Data freshness during market hours

## Documentation
- **design.md**: Technical architecture and system components
- **requirements.md**: Functional and non-functional requirements with acceptance criteria
- **tasks.md**: 23-task implementation roadmap across 6 phases

Maintain this documentation-first approach throughout development - update specifications as implementation reveals new requirements or constraints.