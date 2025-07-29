"""Configuration management for ACE IoT models."""

import os
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator


class ValidationConfig(PydanticBaseModel):
    """Configuration for field validation rules."""

    # Name validation
    name_min_length: int = Field(2, ge=1, description="Minimum length for name fields")
    name_max_length: int = Field(512, ge=1, description="Maximum length for name fields")
    nice_name_max_length: int = Field(256, ge=1, description="Maximum length for nice name fields")

    # Address validation
    address_max_length: int = Field(512, ge=1, description="Maximum length for address fields")

    # Contact validation
    contact_max_length: int = Field(512, ge=1, description="Maximum length for contact fields")

    # Pagination
    valid_per_page_values: list[int] = Field(
        default=[2, 10, 20, 30, 40, 50, 100, 500, 1000, 5000, 10000, 100000],
        description="Valid values for per_page parameter",
    )
    default_per_page: int = Field(10, description="Default items per page")
    default_page: int = Field(1, ge=1, description="Default page number")
    max_page_size: int = Field(100000, ge=1, description="Maximum items per page")

    # Password requirements
    password_min_length: int = Field(8, ge=1, description="Minimum password length")
    password_require_uppercase: bool = Field(True, description="Require uppercase letter")
    password_require_lowercase: bool = Field(True, description="Require lowercase letter")
    password_require_digit: bool = Field(True, description="Require digit")
    password_require_special: bool = Field(True, description="Require special character")

    # File upload
    max_file_size: int = Field(10485760, ge=0, description="Maximum file size in bytes (10MB)")
    allowed_file_extensions: list[str] = Field(
        default=[".json", ".yaml", ".yml", ".toml", ".csv", ".txt"],
        description="Allowed file extensions",
    )

    @field_validator("valid_per_page_values")
    @classmethod
    def validate_per_page_values(cls, v: list[int]) -> list[int]:
        """Ensure per_page values are positive and sorted."""
        if not v:
            raise ValueError("At least one per_page value must be provided")
        if any(val <= 0 for val in v):
            raise ValueError("All per_page values must be positive")
        return sorted(set(v))


class FeatureFlags(PydanticBaseModel):
    """Feature flags for enabling/disabling functionality."""

    enable_caching: bool = Field(True, description="Enable caching for expensive operations")
    enable_async_operations: bool = Field(False, description="Enable async operation support")
    enable_audit_logging: bool = Field(True, description="Enable audit logging")
    enable_soft_delete: bool = Field(True, description="Enable soft delete for records")
    enable_field_encryption: bool = Field(False, description="Enable field-level encryption")
    enable_rate_limiting: bool = Field(True, description="Enable API rate limiting")
    enable_webhooks: bool = Field(False, description="Enable webhook notifications")
    enable_bulk_operations: bool = Field(True, description="Enable bulk create/update/delete")


class CacheConfig(PydanticBaseModel):
    """Configuration for caching behavior."""

    default_ttl: int = Field(300, ge=0, description="Default cache TTL in seconds")
    max_cache_size: int = Field(1000, ge=0, description="Maximum number of cached items")
    cache_key_prefix: str = Field("aceiot", description="Prefix for cache keys")
    enable_cache_stats: bool = Field(True, description="Track cache hit/miss statistics")


class SecurityConfig(PydanticBaseModel):
    """Security-related configuration."""

    jwt_algorithm: str = Field("HS256", description="JWT signing algorithm")
    jwt_expiration: int = Field(3600, ge=60, description="JWT expiration in seconds")
    api_key_length: int = Field(32, ge=16, description="Length of generated API keys")
    bcrypt_rounds: int = Field(12, ge=10, le=20, description="BCrypt hashing rounds")
    allowed_cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )
    require_https: bool = Field(True, description="Require HTTPS for API calls")
    max_login_attempts: int = Field(5, ge=1, description="Maximum login attempts before lockout")
    lockout_duration: int = Field(900, ge=60, description="Account lockout duration in seconds")


class DatabaseConfig(PydanticBaseModel):
    """Database-related configuration."""

    connection_pool_size: int = Field(10, ge=1, description="Database connection pool size")
    connection_timeout: int = Field(30, ge=1, description="Connection timeout in seconds")
    query_timeout: int = Field(60, ge=1, description="Query timeout in seconds")
    enable_query_logging: bool = Field(False, description="Log all database queries")
    enable_slow_query_logging: bool = Field(True, description="Log slow queries")
    slow_query_threshold: float = Field(1.0, gt=0, description="Slow query threshold in seconds")


class NotificationConfig(PydanticBaseModel):
    """Configuration for notifications and alerts."""

    email_from: str = Field("noreply@aceiot.com", description="Default from email address")
    email_reply_to: str | None = Field(None, description="Reply-to email address")
    smtp_host: str | None = Field(None, description="SMTP server host")
    smtp_port: int = Field(587, ge=1, le=65535, description="SMTP server port")
    smtp_use_tls: bool = Field(True, description="Use TLS for SMTP")
    webhook_timeout: int = Field(10, ge=1, description="Webhook request timeout in seconds")
    webhook_retry_attempts: int = Field(3, ge=0, description="Number of webhook retry attempts")
    webhook_retry_delay: int = Field(
        60, ge=1, description="Delay between webhook retries in seconds"
    )


class ModelConfig(PydanticBaseModel):
    """Main configuration class combining all config sections."""

    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    # Environment
    environment: str = Field("development", description="Current environment")
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load configuration from environment variables."""
        config_data = {}

        # Map environment variables to config fields
        env_mappings = {
            "ACEIOT_ENV": "environment",
            "ACEIOT_DEBUG": "debug",
            "ACEIOT_LOG_LEVEL": "log_level",
            # Validation
            "ACEIOT_NAME_MIN_LENGTH": "validation.name_min_length",
            "ACEIOT_DEFAULT_PER_PAGE": "validation.default_per_page",
            # Features
            "ACEIOT_ENABLE_CACHING": "features.enable_caching",
            "ACEIOT_ENABLE_ASYNC": "features.enable_async_operations",
            # Cache
            "ACEIOT_CACHE_TTL": "cache.default_ttl",
            # Security
            "ACEIOT_JWT_EXPIRATION": "security.jwt_expiration",
            "ACEIOT_REQUIRE_HTTPS": "security.require_https",
            # Database
            "ACEIOT_DB_POOL_SIZE": "database.connection_pool_size",
            "ACEIOT_DB_TIMEOUT": "database.connection_timeout",
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert to appropriate type
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)

                # Set nested config value
                parts = config_path.split(".")
                current = config_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value

        return cls(**config_data)

    def get_nested(self, path: str, default: Any = None) -> Any:
        """Get nested configuration value by dot-separated path."""
        parts = path.split(".")
        current = self

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return default

        return current


# Create global configuration instance
_config: ModelConfig | None = None


def get_config() -> ModelConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ModelConfig.from_env()
    return _config


def set_config(config: ModelConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = None


# Configuration context manager
class ConfigContext:
    """Context manager for temporary configuration changes."""

    def __init__(self, **overrides):
        self.overrides = overrides
        self.original_values = {}

    def __enter__(self):
        config = get_config()
        for path, value in self.overrides.items():
            # Store original value
            self.original_values[path] = config.get_nested(path)

            # Set new value
            parts = path.split(".")
            current = config
            for part in parts[:-1]:
                current = getattr(current, part)
            setattr(current, parts[-1], value)

        return config

    def __exit__(self, exc_type, exc_val, exc_tb):
        config = get_config()
        for path, original_value in self.original_values.items():
            parts = path.split(".")
            current = config
            for part in parts[:-1]:
                current = getattr(current, part)
            setattr(current, parts[-1], original_value)


# Export configuration
__all__ = [
    "CacheConfig",
    "ConfigContext",
    "DatabaseConfig",
    "FeatureFlags",
    "ModelConfig",
    "NotificationConfig",
    "SecurityConfig",
    "ValidationConfig",
    "get_config",
    "reset_config",
    "set_config",
]
