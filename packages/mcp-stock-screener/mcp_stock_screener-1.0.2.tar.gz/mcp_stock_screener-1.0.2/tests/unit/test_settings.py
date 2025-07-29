"""Unit tests for configuration settings."""

import os
import pytest

from src.config.settings import (
    DatabaseConfig,
    RedisConfig,
    APIConfig,
    ModelConfig,
    Settings,
    settings
)


class TestDatabaseConfig:
    """Test cases for DatabaseConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = DatabaseConfig()
        
        assert config.host == "localhost"
        assert config.port == 8812
        assert config.username == "admin"
        assert config.password == "quest"
        assert config.database == "qdb"

    def test_environment_override(self):
        """Test environment variable override."""
        # Store original values
        original_host = os.environ.get("QUESTDB_HOST")
        original_port = os.environ.get("QUESTDB_PORT")
        
        try:
            os.environ["QUESTDB_HOST"] = "test-host"
            os.environ["QUESTDB_PORT"] = "9999"
            
            config = DatabaseConfig()
            
            assert config.host == "test-host"
            assert config.port == 9999
        finally:
            # Clean up
            if original_host is not None:
                os.environ["QUESTDB_HOST"] = original_host
            elif "QUESTDB_HOST" in os.environ:
                del os.environ["QUESTDB_HOST"]
                
            if original_port is not None:
                os.environ["QUESTDB_PORT"] = original_port
            elif "QUESTDB_PORT" in os.environ:
                del os.environ["QUESTDB_PORT"]


class TestRedisConfig:
    """Test cases for RedisConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RedisConfig()
        
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
        assert config.ttl == 300

    def test_environment_override(self):
        """Test environment variable override."""
        # Store original values
        original_host = os.environ.get("REDIS_HOST")
        original_password = os.environ.get("REDIS_PASSWORD")
        
        try:
            os.environ["REDIS_HOST"] = "redis-server"
            os.environ["REDIS_PASSWORD"] = "secret"
            
            config = RedisConfig()
            
            assert config.host == "redis-server"
            assert config.password == "secret"
        finally:
            # Clean up
            if original_host is not None:
                os.environ["REDIS_HOST"] = original_host
            elif "REDIS_HOST" in os.environ:
                del os.environ["REDIS_HOST"]
                
            if original_password is not None:
                os.environ["REDIS_PASSWORD"] = original_password
            elif "REDIS_PASSWORD" in os.environ:
                del os.environ["REDIS_PASSWORD"]


class TestAPIConfig:
    """Test cases for APIConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = APIConfig()
        
        assert config.alpha_vantage_key is None
        assert config.polygon_api_key is None
        assert config.rate_limit_per_minute == 100

    def test_environment_override(self):
        """Test environment variable override."""
        # Store original values
        original_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        original_limit = os.environ.get("API_RATE_LIMIT")
        
        try:
            os.environ["ALPHA_VANTAGE_API_KEY"] = "test-key"
            os.environ["API_RATE_LIMIT"] = "200"
            
            config = APIConfig()
            
            assert config.alpha_vantage_key == "test-key"
            assert config.rate_limit_per_minute == 200
        finally:
            # Clean up
            if original_key is not None:
                os.environ["ALPHA_VANTAGE_API_KEY"] = original_key
            elif "ALPHA_VANTAGE_API_KEY" in os.environ:
                del os.environ["ALPHA_VANTAGE_API_KEY"]
                
            if original_limit is not None:
                os.environ["API_RATE_LIMIT"] = original_limit
            elif "API_RATE_LIMIT" in os.environ:
                del os.environ["API_RATE_LIMIT"]


class TestModelConfig:
    """Test cases for ModelConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ModelConfig()
        
        assert config.models_dir == "./models"
        assert config.xgboost_model_path == "./models/xgboost_patterns.pkl"
        assert config.lstm_model_path == "./models/lstm_trends.pkl"
        assert config.bert_model_path == "./models/bert_sentiment.pkl"
        assert config.prediction_confidence_threshold == 0.7

    def test_environment_override(self):
        """Test environment variable override."""
        # Store original values
        original_dir = os.environ.get("MODELS_DIR")
        original_threshold = os.environ.get("CONFIDENCE_THRESHOLD")
        
        try:
            os.environ["MODELS_DIR"] = "/custom/models"
            os.environ["CONFIDENCE_THRESHOLD"] = "0.8"
            
            config = ModelConfig()
            
            assert config.models_dir == "/custom/models"
            assert config.prediction_confidence_threshold == 0.8
        finally:
            # Clean up
            if original_dir is not None:
                os.environ["MODELS_DIR"] = original_dir
            elif "MODELS_DIR" in os.environ:
                del os.environ["MODELS_DIR"]
                
            if original_threshold is not None:
                os.environ["CONFIDENCE_THRESHOLD"] = original_threshold
            elif "CONFIDENCE_THRESHOLD" in os.environ:
                del os.environ["CONFIDENCE_THRESHOLD"]


class TestSettings:
    """Test cases for Settings class."""

    def test_settings_initialization(self):
        """Test that settings object initializes correctly."""
        assert settings.database is not None
        assert settings.redis is not None
        assert settings.api is not None
        assert settings.models is not None

    def test_settings_singleton(self):
        """Test that settings behaves as singleton."""
        from src.config.settings import settings as settings2
        assert settings is settings2