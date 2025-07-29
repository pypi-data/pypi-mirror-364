"""Unit tests for query processor."""

import pytest

from src.api.models import ScreeningCriteria
from src.api.query_processor import QueryProcessor


class TestQueryProcessor:
    """Test cases for QueryProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = QueryProcessor()

    @pytest.mark.asyncio
    async def test_parse_basic_query(self):
        """Test parsing of a basic query."""
        query = "Find tech stocks with market cap over $1 billion"
        criteria = await self.processor.parse_query(query)

        assert isinstance(criteria, ScreeningCriteria)
        assert criteria.sectors == ["Technology"]
        assert criteria.market_cap_range == (1_000_000_000, None)

    @pytest.mark.asyncio
    async def test_parse_rsi_query(self):
        """Test parsing of RSI-based query."""
        query = "Show me momentum stocks with RSI under 30"
        criteria = await self.processor.parse_query(query)

        assert criteria.rsi_range == (None, 30.0)
        assert criteria.volume_threshold == 1_000_000  # From momentum filter

    @pytest.mark.asyncio
    async def test_parse_complex_query(self):
        """Test parsing of complex multi-criteria query."""
        query = "Find large cap healthcare stocks with positive sentiment and RSI between 40 and 60"
        criteria = await self.processor.parse_query(query)

        assert criteria.market_cap_range == (10_000_000_000, None)  # Large cap
        assert criteria.sectors == ["Healthcare"]
        assert criteria.sentiment_threshold == 0.1  # Positive sentiment
        assert criteria.rsi_range == (40.0, 60.0)

    @pytest.mark.asyncio
    async def test_parse_price_range(self):
        """Test parsing of price range criteria."""
        query = "Show stocks between $50 and $200"
        criteria = await self.processor.parse_query(query)

        assert criteria.price_range == (50.0, 200.0)

    @pytest.mark.asyncio
    async def test_parse_limit(self):
        """Test parsing of result limits."""
        query = "Show me top 10 tech stocks"
        criteria = await self.processor.parse_query(query)

        assert criteria.limit == 10
        assert criteria.sectors == ["Technology"]

    @pytest.mark.asyncio
    async def test_parse_oversold_query(self):
        """Test parsing of oversold condition."""
        query = "Find oversold stocks"
        criteria = await self.processor.parse_query(query)

        assert criteria.rsi_range == (None, 30.0)

    @pytest.mark.asyncio
    async def test_parse_volume_query(self):
        """Test parsing of volume criteria."""
        query = "High volume stocks with volume over 5 million"
        criteria = await self.processor.parse_query(query)

        assert criteria.volume_threshold >= 5_000_000
