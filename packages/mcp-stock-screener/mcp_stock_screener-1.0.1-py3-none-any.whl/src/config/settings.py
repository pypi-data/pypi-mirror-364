"""Configuration settings for Smart Stock Screener MCP server."""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """QuestDB database configuration."""
    
    model_config = SettingsConfigDict(env_prefix="QUESTDB_")

    host: str = "localhost"
    port: int = 8812
    username: str = "admin"
    password: str = "quest"
    database: str = "qdb"


class RedisConfig(BaseSettings):
    """Redis cache configuration."""
    
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    password: str | None = None
    db: int = 0
    ttl: int = 300  # 5 minutes default


class APIConfig(BaseSettings):
    """External API configurations."""
    
    model_config = SettingsConfigDict()

    alpha_vantage_key: str | None = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    polygon_api_key: str | None = Field(default=None, alias="POLYGON_API_KEY")
    rate_limit_per_minute: int = Field(default=100, alias="API_RATE_LIMIT")


class ModelConfig(BaseSettings):
    """ML model configurations."""
    
    model_config = SettingsConfigDict()

    models_dir: str = Field(default="./models", alias="MODELS_DIR")
    xgboost_model_path: str = Field(
        default="./models/xgboost_patterns.pkl", alias="XGBOOST_MODEL_PATH"
    )
    lstm_model_path: str = Field(
        default="./models/lstm_trends.pkl", alias="LSTM_MODEL_PATH"
    )
    bert_model_path: str = Field(
        default="./models/bert_sentiment.pkl", alias="BERT_MODEL_PATH"
    )
    prediction_confidence_threshold: float = Field(
        default=0.7, alias="CONFIDENCE_THRESHOLD"
    )


class HTTPConfig(BaseSettings):
    """HTTP server configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HTTP_")

    host: str = "127.0.0.1"
    port: int = 8080
    mount_path: str = "/mcp"
    cors_origins: list[str] = ["http://localhost:3000"]
    session_timeout: int = 3600  # 1 hour


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Smart Stock Screener MCP"
    version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")

    # Transport settings
    transport: str = Field(
        default="stdio", alias="MCP_TRANSPORT"
    )  # "stdio" or "http" or "both"

    # Performance settings
    max_screening_results: int = Field(default=500, alias="MAX_SCREENING_RESULTS")
    default_screening_results: int = Field(default=50, alias="DEFAULT_SCREENING_RESULTS")
    query_timeout_seconds: int = Field(default=30, alias="QUERY_TIMEOUT")

    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    http: HTTPConfig = Field(default_factory=HTTPConfig)


# Global settings instance
settings = Settings()
