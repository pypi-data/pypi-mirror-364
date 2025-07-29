"""Mock data provider for testing MCP endpoints."""

import random
from datetime import datetime, timedelta, timezone

from .models import (
    AnalysisResult,
    DetailedAnalysis,
    ScreeningCriteria,
    SentimentData,
    StockData,
    TechnicalIndicators,
)


class MockDataProvider:
    """Provides mock stock data for testing and development."""

    def __init__(self):
        # Mock stock universe
        self.mock_stocks = {
            "AAPL": {
                "name": "Apple Inc.",
                "sector": "Technology",
                "market_cap": 3_000_000_000_000,  # $3T
                "base_price": 190.0,
            },
            "GOOGL": {
                "name": "Alphabet Inc.",
                "sector": "Technology",
                "market_cap": 1_800_000_000_000,  # $1.8T
                "base_price": 140.0,
            },
            "TSLA": {
                "name": "Tesla Inc.",
                "sector": "Consumer Discretionary",
                "market_cap": 800_000_000_000,  # $800B
                "base_price": 250.0,
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "market_cap": 2_800_000_000_000,  # $2.8T
                "base_price": 380.0,
            },
            "NVDA": {
                "name": "NVIDIA Corporation",
                "sector": "Technology",
                "market_cap": 1_600_000_000_000,  # $1.6T
                "base_price": 480.0,
            },
            "JPM": {
                "name": "JPMorgan Chase & Co.",
                "sector": "Financials",
                "market_cap": 500_000_000_000,  # $500B
                "base_price": 170.0,
            },
            "JNJ": {
                "name": "Johnson & Johnson",
                "sector": "Healthcare",
                "market_cap": 450_000_000_000,  # $450B
                "base_price": 160.0,
            },
            "XOM": {
                "name": "Exxon Mobil Corporation",
                "sector": "Energy",
                "market_cap": 400_000_000_000,  # $400B
                "base_price": 110.0,
            },
            "V": {
                "name": "Visa Inc.",
                "sector": "Financials",
                "market_cap": 520_000_000_000,  # $520B
                "base_price": 240.0,
            },
            "WMT": {
                "name": "Walmart Inc.",
                "sector": "Consumer Staples",
                "market_cap": 470_000_000_000,  # $470B
                "base_price": 165.0,
            },
            "PG": {
                "name": "Procter & Gamble Co.",
                "sector": "Consumer Staples",
                "market_cap": 380_000_000_000,  # $380B
                "base_price": 155.0,
            },
            "HD": {
                "name": "Home Depot Inc.",
                "sector": "Consumer Discretionary",
                "market_cap": 330_000_000_000,  # $330B
                "base_price": 320.0,
            },
            "BAC": {
                "name": "Bank of America Corp.",
                "sector": "Financials",
                "market_cap": 280_000_000_000,  # $280B
                "base_price": 34.0,
            },
            "KO": {
                "name": "Coca-Cola Co.",
                "sector": "Consumer Staples",
                "market_cap": 260_000_000_000,  # $260B
                "base_price": 60.0,
            },
            "AMD": {
                "name": "Advanced Micro Devices Inc.",
                "sector": "Technology",
                "market_cap": 220_000_000_000,  # $220B
                "base_price": 135.0,
            },
        }

    def _generate_stock_data(self, symbol: str) -> StockData:
        """Generate mock stock data for a symbol."""
        if symbol not in self.mock_stocks:
            # Generate random data for unknown symbols
            stock_info = {
                "name": f"{symbol} Corp.",
                "sector": random.choice(
                    ["Technology", "Healthcare", "Financials", "Energy"]
                ),
                "market_cap": random.randint(1_000_000_000, 100_000_000_000),
                "base_price": random.uniform(10.0, 500.0),
            }
        else:
            stock_info = self.mock_stocks[symbol]

        # Add some random variation to the base price
        price_variation = random.uniform(-0.05, 0.05)  # ±5%
        current_price = stock_info["base_price"] * (1 + price_variation)

        # Generate technical indicators
        technical_indicators = TechnicalIndicators(
            rsi=round(random.uniform(20.0, 80.0), 2),
            macd=round(random.uniform(-2.0, 2.0), 4),
            bollinger_upper=round(current_price * 1.05, 2),
            bollinger_lower=round(current_price * 0.95, 2),
            moving_avg_20=round(current_price * random.uniform(0.98, 1.02), 2),
            moving_avg_50=round(current_price * random.uniform(0.95, 1.05), 2),
        )

        # Generate sentiment data
        sentiment_data = SentimentData(
            news_score=round(random.uniform(-0.5, 0.5), 3),
            social_score=round(random.uniform(-0.3, 0.3), 3),
            confidence=round(random.uniform(0.6, 0.9), 3),
            article_count=random.randint(5, 50),
        )

        return StockData(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            price=round(current_price, 2),
            volume=random.randint(1_000_000, 50_000_000),
            market_cap=float(stock_info["market_cap"]),  # Ensure it's a float
            high=round(current_price * 1.02, 2),
            low=round(current_price * 0.98, 2),
            close=round(current_price * random.uniform(0.99, 1.01), 2),
            sector=stock_info["sector"],
            technical_indicators=technical_indicators,
            sentiment=sentiment_data,
        )

    def screen_stocks(self, criteria: ScreeningCriteria) -> list[StockData]:
        """Screen stocks based on criteria and return matching results."""
        matching_stocks = []

        # Start with all available stocks
        for symbol in list(self.mock_stocks.keys()):
            stock_data = self._generate_stock_data(symbol)

            # Apply filtering criteria
            if self._matches_criteria(stock_data, criteria):
                matching_stocks.append(stock_data)

        # Sort by a mock relevance score (using price as proxy)
        matching_stocks.sort(key=lambda x: x.price, reverse=True)

        # Apply limit
        return matching_stocks[: criteria.limit]

    def _matches_criteria(
        self, stock_data: StockData, criteria: ScreeningCriteria
    ) -> bool:
        """Check if stock data matches the screening criteria."""
        stock_info = self.mock_stocks.get(stock_data.symbol, {})

        # Market cap filter
        if criteria.market_cap_range:
            min_cap, max_cap = criteria.market_cap_range
            if min_cap and stock_data.market_cap < min_cap:
                return False
            if max_cap and stock_data.market_cap > max_cap:
                return False

        # Price filter
        if criteria.price_range:
            min_price, max_price = criteria.price_range
            if min_price and stock_data.price < min_price:
                return False
            if max_price and stock_data.price > max_price:
                return False

        # Volume filter
        if criteria.volume_threshold and stock_data.volume < criteria.volume_threshold:
            return False

        # RSI filter
        if criteria.rsi_range and stock_data.technical_indicators:
            min_rsi, max_rsi = criteria.rsi_range
            rsi = stock_data.technical_indicators.rsi
            # Skip stocks with None RSI values
            if rsi is None:
                return False
            if min_rsi and rsi < min_rsi:
                return False
            if max_rsi and rsi > max_rsi:
                return False

        # MACD filter
        if criteria.macd_signal and stock_data.technical_indicators:
            macd = stock_data.technical_indicators.macd
            if criteria.macd_signal == "bullish" and macd <= 0:
                return False
            if criteria.macd_signal == "bearish" and macd >= 0:
                return False

        # Sector filter
        if criteria.sectors:
            stock_sector = stock_info.get("sector")
            if stock_sector not in criteria.sectors:
                return False

        # Sentiment filter
        if criteria.sentiment_threshold and stock_data.sentiment:
            if stock_data.sentiment.news_score < criteria.sentiment_threshold:
                return False

        return True

    async def analyze_stock(self, symbol: str) -> DetailedAnalysis:
        """Provide comprehensive analysis for a specific stock."""
        stock_data = self._generate_stock_data(symbol)

        # Generate mock AI analysis
        analysis_result = AnalysisResult(
            symbol=symbol,
            technical_score=random.uniform(60.0, 90.0),
            trend_direction=random.choice(["bullish", "bearish", "neutral"]),
            sentiment_score=(
                stock_data.sentiment.news_score if stock_data.sentiment else 0.0
            ),
            confidence=random.uniform(0.7, 0.95),
            risk_level=random.choice(["low", "medium", "high"]),
            time_horizon=random.randint(7, 30),
            reasoning=self._generate_analysis_reasoning(symbol, stock_data),
        )

        # Mock historical context
        historical_context = {
            "52_week_high": stock_data.price * random.uniform(1.1, 1.3),
            "52_week_low": stock_data.price * random.uniform(0.7, 0.9),
            "avg_volume_30d": random.randint(5_000_000, 25_000_000),
            "earnings_date": (
                datetime.now() + timedelta(days=random.randint(10, 90))
            ).isoformat(),
            "dividend_yield": (
                random.uniform(0.0, 4.0) if random.random() > 0.3 else None
            ),
        }

        # Mock peer comparison
        peer_symbols = [
            s
            for s in self.mock_stocks.keys()
            if s != symbol
            and self.mock_stocks[s].get("sector")
            == self.mock_stocks.get(symbol, {}).get("sector")
        ]
        peer_comparison = peer_symbols[:3] if peer_symbols else []

        return DetailedAnalysis(
            stock_data=stock_data,
            analysis=analysis_result,
            historical_context=historical_context,
            peer_comparison=peer_comparison,
        )

    def _generate_analysis_reasoning(self, symbol: str, stock_data: StockData) -> str:
        """Generate mock analysis reasoning text."""
        stock_info = self.mock_stocks.get(symbol, {})
        sector = stock_info.get("sector", "Unknown")

        reasoning_parts = [f"{symbol} is currently trading at ${stock_data.price:.2f}"]

        if stock_data.technical_indicators:
            rsi = stock_data.technical_indicators.rsi
            if rsi < 30:
                reasoning_parts.append("with RSI indicating oversold conditions")
            elif rsi > 70:
                reasoning_parts.append("with RSI showing overbought levels")
            else:
                reasoning_parts.append(
                    f"with RSI at {rsi:.1f} indicating neutral momentum"
                )

        if stock_data.sentiment:
            sentiment = stock_data.sentiment.news_score
            if sentiment > 0.1:
                reasoning_parts.append("News sentiment is positive")
            elif sentiment < -0.1:
                reasoning_parts.append("News sentiment shows some concern")
            else:
                reasoning_parts.append("News sentiment is neutral")

        reasoning_parts.append(
            f"As a {sector} stock, it benefits from sector-specific trends"
        )

        if stock_data.volume > 10_000_000:
            reasoning_parts.append(
                "Trading volume is above average, indicating strong interest"
            )

        return ". ".join(reasoning_parts) + "."

    def generate_stock_data(self, symbol: str) -> StockData:
        """Generate mock stock data for a symbol (public method for testing)."""
        return self._generate_stock_data(symbol)

    def get_detailed_analysis(self, symbol: str) -> DetailedAnalysis:
        """Get detailed analysis for a symbol (synchronous version for testing)."""
        import asyncio
        return asyncio.run(self.analyze_stock(symbol))

    def _generate_technical_indicators(self) -> TechnicalIndicators:
        """Generate mock technical indicators."""
        return TechnicalIndicators(
            rsi=random.uniform(20.0, 80.0),
            macd=random.uniform(-2.0, 2.0),
            bollinger_upper=random.uniform(100.0, 200.0),
            bollinger_lower=random.uniform(50.0, 100.0),
            moving_avg_20=random.uniform(80.0, 120.0),
            moving_avg_50=random.uniform(70.0, 130.0),
        )

    def _generate_sentiment_data(self) -> SentimentData:
        """Generate mock sentiment data."""
        return SentimentData(
            news_score=random.uniform(-0.5, 0.5),
            social_score=random.uniform(-0.3, 0.3),
            confidence=random.uniform(0.6, 0.9),
            article_count=random.randint(5, 50),
        )
