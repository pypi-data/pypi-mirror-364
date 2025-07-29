"""Data models for Smart Stock Screener MCP interface."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TechnicalIndicators(BaseModel):
    """Technical indicators for a stock."""

    rsi: float | None = Field(
        None, ge=0, le=100, description="Relative Strength Index"
    )
    macd: float | None = Field(None, description="MACD indicator")
    bollinger_upper: float | None = Field(None, description="Bollinger Band upper")
    bollinger_lower: float | None = Field(None, description="Bollinger Band lower")
    moving_avg_20: float | None = Field(None, description="20-day moving average")
    moving_avg_50: float | None = Field(None, description="50-day moving average")


class SentimentData(BaseModel):
    """Sentiment analysis data for a stock."""

    news_score: float = Field(
        ..., ge=-1, le=1, description="News sentiment score (-1 to 1)"
    )
    social_score: float | None = Field(
        None, ge=-1, le=1, description="Social media sentiment"
    )
    confidence: float = Field(..., ge=0, le=1, description="Sentiment confidence score")
    article_count: int = Field(default=0, description="Number of articles analyzed")


class StockData(BaseModel):
    """Core stock data structure."""

    symbol: str = Field(..., description="Stock ticker symbol")
    timestamp: datetime = Field(..., description="Data timestamp")
    price: float = Field(..., gt=0, description="Current stock price")
    volume: int = Field(..., ge=0, description="Trading volume")
    market_cap: float | None = Field(None, description="Market capitalization")
    high: float | None = Field(None, description="Day high")
    low: float | None = Field(None, description="Day low")
    close: float | None = Field(None, description="Previous close")
    sector: str | None = Field(None, description="Stock sector")

    technical_indicators: TechnicalIndicators | None = None
    sentiment: SentimentData | None = None


class ScreeningCriteria(BaseModel):
    """Criteria for stock screening queries."""

    market_cap_range: tuple[float | None, float | None] | None = Field(
        None, description="Market cap range (min, max)"
    )
    price_range: tuple[float | None, float | None] | None = Field(
        None, description="Price range (min, max)"
    )
    volume_threshold: int | None = Field(
        None, description="Minimum volume threshold"
    )

    # Technical filters
    rsi_range: tuple[float | None, float | None] | None = Field(
        None, description="RSI range (min, max)"
    )
    macd_signal: Literal["bullish", "bearish"] | None = Field(
        None, description="MACD signal"
    )

    # Sector and sentiment
    sectors: list[str] | None = Field(None, description="Sector filters")
    sentiment_threshold: float | None = Field(
        None, ge=-1, le=1, description="Minimum sentiment score"
    )

    # Result settings
    limit: int = Field(
        default=50, ge=1, le=500, description="Maximum results to return"
    )


class AnalysisResult(BaseModel):
    """AI analysis result for a stock."""

    symbol: str = Field(..., description="Stock ticker symbol")
    technical_score: float = Field(
        ..., ge=0, le=100, description="Technical analysis score"
    )
    trend_direction: Literal["bullish", "bearish", "neutral"] = Field(
        ..., description="Trend prediction"
    )
    sentiment_score: float = Field(
        ..., ge=-1, le=1, description="Overall sentiment score"
    )
    confidence: float = Field(..., ge=0, le=1, description="Analysis confidence")
    risk_level: Literal["low", "medium", "high"] = Field(
        ..., description="Risk assessment"
    )
    time_horizon: int = Field(
        ..., ge=1, le=30, description="Prediction time horizon in days"
    )
    reasoning: str = Field(..., description="Human-readable analysis reasoning")


class ScreeningResult(BaseModel):
    """Result of stock screening query."""

    matches: list[StockData] = Field(..., description="Matching stocks")
    total_results: int = Field(..., description="Total number of matches")
    query: str = Field(..., description="Original query string")
    execution_time: float = Field(..., description="Query execution time in seconds")
    confidence: float = Field(..., ge=0, le=1, description="Query parsing confidence")
    criteria_used: ScreeningCriteria = Field(
        ..., description="Parsed screening criteria"
    )


class DetailedAnalysis(BaseModel):
    """Comprehensive analysis for a specific stock."""

    stock_data: StockData = Field(..., description="Current stock data")
    analysis: AnalysisResult = Field(..., description="AI analysis results")
    historical_context: dict[str, Any] | None = Field(
        None, description="Historical context data"
    )
    peer_comparison: list[str] | None = Field(
        None, description="Peer stock symbols for comparison"
    )


class ErrorResponse(BaseModel):
    """Error response structure."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        None, description="Additional error details"
    )
    suggestions: list[str] | None = Field(None, description="Suggested corrections")


class HealthCheck(BaseModel):
    """System health check response."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="Overall system status"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")
    components: dict[str, dict[str, Any]] = Field(
        ..., description="Component-specific health data"
    )
    uptime_seconds: int = Field(..., description="System uptime in seconds")
