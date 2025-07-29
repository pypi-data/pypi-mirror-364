"""Natural language query processor for stock screening."""

import logging
import re

from .models import ScreeningCriteria

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Processes natural language queries and converts them to screening criteria."""

    def __init__(self):
        # Define pattern matching rules for common query types
        self.patterns = {
            # Market cap patterns
            "market_cap": {
                r"market cap (?:over|above|greater than|>)\s*\$?(\d+(?:\.\d+)?)\s*(billion|b|million|m)": "min",
                r"market cap (?:under|below|less than|<)\s*\$?(\d+(?:\.\d+)?)\s*(billion|b|million|m)": "max",
                r"market cap between\s*\$?(\d+(?:\.\d+)?)\s*(billion|b|million|m)?\s*(?:and|to|-)\s*\$?(\d+(?:\.\d+)?)\s*(billion|b|million|m)": "range",
                r"large cap": "large_cap",
                r"mid cap": "mid_cap",
                r"small cap": "small_cap",
                r"mega cap": "mega_cap",
            },
            # Price patterns
            "price": {
                r"price (?:over|above|greater than|>)\s*\$?(\d+(?:\.\d+)?)": "min",
                r"price (?:under|below|less than|<)\s*\$?(\d+(?:\.\d+)?)": "max",
                r"(?:price|stocks?) between\s*\$?(\d+(?:\.\d+)?)\s*(?:and|to|-)\s*\$?(\d+(?:\.\d+)?)": "range",
            },
            # Technical indicator patterns
            "rsi": {
                r"rsi (?:under|below|less than|<)\s*(\d+(?:\.\d+)?)": "max",
                r"rsi (?:over|above|greater than|>)\s*(\d+(?:\.\d+)?)": "min",
                r"rsi between\s*(\d+(?:\.\d+)?)\s*(?:and|to|-)\s*(\d+(?:\.\d+)?)": "range",
                r"oversold": "oversold",  # RSI < 30
                r"overbought": "overbought",  # RSI > 70
            },
            # MACD patterns
            "macd": {
                r"macd bullish|bullish macd|positive macd": "bullish",
                r"macd bearish|bearish macd|negative macd": "bearish",
            },
            # Volume patterns
            "volume": {
                r"volume (?:over|above|greater than|>)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(million|m|thousand|k)?": "min",
                r"high volume": "high_volume",
                r"heavy volume": "high_volume",
            },
            # Sector patterns
            "sectors": {
                r"tech(?:nology)? stocks?": ["Technology"],
                r"healthcare stocks?": ["Healthcare"],
                r"financial stocks?": ["Financials"],
                r"energy stocks?": ["Energy"],
                r"consumer stocks?": ["Consumer Discretionary", "Consumer Staples"],
                r"industrial stocks?": ["Industrials"],
                r"real estate stocks?": ["Real Estate"],
                r"utility stocks?": ["Utilities"],
                r"materials stocks?": ["Materials"],
                r"communication stocks?": ["Communication Services"],
            },
            # Sentiment patterns
            "sentiment": {
                r"positive sentiment|bullish sentiment": "positive",
                r"negative sentiment|bearish sentiment": "negative",
                r"strong sentiment": "strong_positive",
            },
            # Common stock types
            "stock_types": {
                r"momentum stocks?": "momentum",
                r"value stocks?": "value",
                r"growth stocks?": "growth",
                r"dividend stocks?": "dividend",
                r"penny stocks?": "penny",
            },
        }

    async def parse_query(self, query: str) -> ScreeningCriteria:
        """Parse natural language query into structured screening criteria."""
        query_lower = query.lower().strip()
        logger.info(f"Parsing query: {query}")

        criteria = ScreeningCriteria()

        # Parse market cap criteria
        criteria.market_cap_range = self._parse_market_cap(query_lower)

        # Parse price criteria
        criteria.price_range = self._parse_price(query_lower)

        # Parse RSI criteria
        criteria.rsi_range = self._parse_rsi(query_lower)

        # Parse MACD criteria
        criteria.macd_signal = self._parse_macd(query_lower)

        # Parse volume criteria
        criteria.volume_threshold = self._parse_volume(query_lower)

        # Parse sector criteria
        criteria.sectors = self._parse_sectors(query_lower)

        # Parse sentiment criteria
        criteria.sentiment_threshold = self._parse_sentiment(query_lower)

        # Apply stock type filters
        self._apply_stock_type_filters(query_lower, criteria)

        # Parse result limit
        criteria.limit = self._parse_limit(query_lower)

        logger.info(f"Parsed criteria: {criteria}")
        return criteria

    def _parse_market_cap(self, query: str) -> tuple[float, float] | None:
        """Parse market cap criteria from query."""
        for pattern, cap_type in self.patterns["market_cap"].items():
            match = re.search(pattern, query)
            if match:
                if cap_type == "large_cap":
                    return (10_000_000_000, None)  # > $10B
                elif cap_type == "mid_cap":
                    return (2_000_000_000, 10_000_000_000)  # $2B - $10B
                elif cap_type == "small_cap":
                    return (300_000_000, 2_000_000_000)  # $300M - $2B
                elif cap_type == "mega_cap":
                    return (200_000_000_000, None)  # > $200B
                elif cap_type == "range":
                    min_val = self._convert_to_number(match.group(1), match.group(2))
                    max_val = self._convert_to_number(match.group(3), match.group(4))
                    return (min_val, max_val)
                elif cap_type == "min":
                    val = self._convert_to_number(match.group(1), match.group(2))
                    return (val, None)
                elif cap_type == "max":
                    val = self._convert_to_number(match.group(1), match.group(2))
                    return (None, val)
        return None

    def _parse_price(self, query: str) -> tuple[float, float] | None:
        """Parse price criteria from query."""
        for pattern, price_type in self.patterns["price"].items():
            match = re.search(pattern, query)
            if match:
                if price_type == "range":
                    return (float(match.group(1)), float(match.group(2)))
                elif price_type == "min":
                    return (float(match.group(1)), None)
                elif price_type == "max":
                    return (None, float(match.group(1)))
        return None

    def _parse_rsi(self, query: str) -> tuple[float, float] | None:
        """Parse RSI criteria from query."""
        for pattern, rsi_type in self.patterns["rsi"].items():
            match = re.search(pattern, query)
            if match:
                if rsi_type == "oversold":
                    return (None, 30.0)
                elif rsi_type == "overbought":
                    return (70.0, None)
                elif rsi_type == "range":
                    return (float(match.group(1)), float(match.group(2)))
                elif rsi_type == "min":
                    return (float(match.group(1)), None)
                elif rsi_type == "max":
                    return (None, float(match.group(1)))
        return None

    def _parse_macd(self, query: str) -> str | None:
        """Parse MACD criteria from query."""
        for pattern, macd_type in self.patterns["macd"].items():
            if re.search(pattern, query):
                return macd_type
        return None

    def _parse_volume(self, query: str) -> int | None:
        """Parse volume criteria from query."""
        for pattern, vol_type in self.patterns["volume"].items():
            match = re.search(pattern, query)
            if match:
                if vol_type == "high_volume":
                    return 1_000_000  # Default high volume threshold
                elif vol_type == "min":
                    volume_str = match.group(1).replace(",", "")
                    volume = float(volume_str)
                    unit = match.group(2) if match.group(2) else ""

                    if unit.lower() in ["million", "m"]:
                        volume *= 1_000_000
                    elif unit.lower() in ["thousand", "k"]:
                        volume *= 1_000

                    return int(volume)
        return None

    def _parse_sectors(self, query: str) -> list[str] | None:
        """Parse sector criteria from query."""
        sectors = []
        for pattern, sector_list in self.patterns["sectors"].items():
            if re.search(pattern, query):
                if isinstance(sector_list, list):
                    sectors.extend(sector_list)
                else:
                    sectors.append(sector_list)
        return sectors if sectors else None

    def _parse_sentiment(self, query: str) -> float | None:
        """Parse sentiment criteria from query."""
        for pattern, sentiment_type in self.patterns["sentiment"].items():
            if re.search(pattern, query):
                if sentiment_type == "positive":
                    return 0.1  # Slightly positive sentiment
                elif sentiment_type == "negative":
                    return -0.1  # Slightly negative sentiment
                elif sentiment_type == "strong_positive":
                    return 0.5  # Strong positive sentiment
        return None

    def _apply_stock_type_filters(
        self, query: str, criteria: ScreeningCriteria
    ) -> None:
        """Apply filters based on stock type mentioned in query."""
        for pattern, stock_type in self.patterns["stock_types"].items():
            if re.search(pattern, query):
                if stock_type == "momentum":
                    # Momentum stocks: RSI > 50, high volume
                    if not criteria.rsi_range:
                        criteria.rsi_range = (50.0, None)
                    if not criteria.volume_threshold:
                        criteria.volume_threshold = 1_000_000
                elif stock_type == "value":
                    # Value stocks: lower P/E ratios, stable
                    pass  # Would need P/E data
                elif stock_type == "growth":
                    # Growth stocks: often higher prices, tech sectors
                    if not criteria.sectors:
                        criteria.sectors = [
                            "Technology",
                            "Healthcare",
                            "Consumer Discretionary",
                        ]
                elif stock_type == "dividend":
                    # Dividend stocks: typically larger, stable companies
                    if not criteria.market_cap_range:
                        criteria.market_cap_range = (1_000_000_000, None)  # > $1B
                elif stock_type == "penny":
                    # Penny stocks: < $5
                    if not criteria.price_range:
                        criteria.price_range = (None, 5.0)

    def _parse_limit(self, query: str) -> int:
        """Parse result limit from query."""
        # Look for explicit limit requests
        limit_match = re.search(r"(?:top|first|show me)\s*(\d+)", query)
        if limit_match:
            limit = int(limit_match.group(1))
            return min(limit, 500)  # Cap at 500

        return 50  # Default limit

    def _convert_to_number(self, value: str, unit: str) -> float:
        """Convert string value with unit to number."""
        num = float(value)
        if unit.lower() in ["billion", "b"]:
            return num * 1_000_000_000
        elif unit.lower() in ["million", "m"]:
            return num * 1_000_000
        elif unit.lower() in ["thousand", "k"]:
            return num * 1_000
        return num
