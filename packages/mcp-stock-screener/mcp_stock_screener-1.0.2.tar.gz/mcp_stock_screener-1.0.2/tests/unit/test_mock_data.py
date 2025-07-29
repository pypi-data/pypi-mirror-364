"""Unit tests for mock data provider."""

import pytest
from datetime import datetime

from src.api.mock_data import MockDataProvider
from src.api.models import ScreeningCriteria, StockData


class TestMockDataProvider:
    """Test cases for MockDataProvider class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.provider = MockDataProvider()

    def test_initialization(self):
        """Test that mock data provider initializes correctly."""
        assert self.provider.mock_stocks is not None
        assert len(self.provider.mock_stocks) > 0
        assert "AAPL" in self.provider.mock_stocks
        assert "GOOGL" in self.provider.mock_stocks

    def test_generate_stock_data(self):
        """Test stock data generation."""
        symbol = "AAPL"
        stock_data = self.provider.generate_stock_data(symbol)
        
        assert isinstance(stock_data, StockData)
        assert stock_data.symbol == symbol
        assert stock_data.sector == "Technology"
        assert stock_data.price > 0
        assert stock_data.market_cap > 0

    def test_generate_stock_data_unknown_symbol(self):
        """Test stock data generation for unknown symbol."""
        symbol = "UNKNOWN"
        stock_data = self.provider.generate_stock_data(symbol)
        
        assert isinstance(stock_data, StockData)
        assert stock_data.symbol == symbol
        assert stock_data.price > 0

    def test_screen_stocks_basic(self):
        """Test basic stock screening."""
        criteria = ScreeningCriteria(
            sectors=["Technology"],
            limit=5
        )
        
        results = self.provider.screen_stocks(criteria)
        assert len(results) <= 5
        for stock in results:
            assert stock.sector == "Technology"

    def test_screen_stocks_price_range(self):
        """Test stock screening with price range."""
        criteria = ScreeningCriteria(
            price_range=(100.0, 300.0),
            limit=10
        )
        
        results = self.provider.screen_stocks(criteria)
        for stock in results:
            assert 100.0 <= stock.price <= 300.0

    def test_screen_stocks_market_cap(self):
        """Test stock screening with market cap filter."""
        criteria = ScreeningCriteria(
            market_cap_range=(1_000_000_000_000, None),  # $1T+
            limit=10
        )
        
        results = self.provider.screen_stocks(criteria)
        for stock in results:
            assert stock.market_cap >= 1_000_000_000_000

    def test_screen_stocks_rsi_range(self):
        """Test stock screening with RSI range."""
        criteria = ScreeningCriteria(
            rsi_range=(20.0, 40.0),
            limit=10
        )
        
        results = self.provider.screen_stocks(criteria)
        for stock in results:
            assert 20.0 <= stock.technical_indicators.rsi <= 40.0

    def test_get_detailed_analysis(self):
        """Test detailed analysis generation."""
        symbol = "AAPL"
        analysis = self.provider.get_detailed_analysis(symbol)
        
        assert analysis.stock_data.symbol == symbol
        assert analysis.analysis.trend_direction in ["bullish", "bearish", "neutral"]
        assert 0 <= analysis.analysis.confidence <= 1
        assert len(analysis.analysis.reasoning) > 0

    def test_generate_technical_indicators(self):
        """Test technical indicators generation."""
        indicators = self.provider._generate_technical_indicators()
        
        assert 0 <= indicators.rsi <= 100
        assert indicators.macd is not None
        assert indicators.bollinger_upper is not None
        assert indicators.bollinger_lower is not None

    def test_generate_sentiment_data(self):
        """Test sentiment data generation."""
        sentiment = self.provider._generate_sentiment_data()
        
        assert -1 <= sentiment.news_score <= 1
        assert sentiment.article_count >= 0
        assert 0 <= sentiment.confidence <= 1