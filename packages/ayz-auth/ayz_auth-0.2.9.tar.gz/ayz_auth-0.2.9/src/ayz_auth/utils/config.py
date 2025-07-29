"""
Configuration management for ayz-auth package.

Uses Pydantic settings for type-safe configuration with environment variable support.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

# Detect test environment
_IS_TEST_ENV = (
    os.getenv("PYTEST_CURRENT_TEST") is not None
    or os.getenv("CI") is not None
    or os.getenv("GITHUB_ACTIONS") is not None
    or "pytest" in os.getenv("_", "").lower()
)


class AuthSettings(BaseSettings):
    """
    Configuration settings for Stytch authentication middleware.

    All settings can be provided via environment variables with the STYTCH_ prefix.
    """

    # Stytch B2B API configuration
    project_id: str = Field(
        default="test_project_id" if _IS_TEST_ENV else ...,
        description="Stytch project ID (set via STYTCH_PROJECT_ID env var)",
    )
    secret: str = Field(
        default="test_secret_key" if _IS_TEST_ENV else ...,
        description="Stytch API secret (set via STYTCH_SECRET env var)",
    )
    environment: str = Field(
        default="test", description="Stytch environment: 'test' or 'live'"
    )
    organization_id: str = Field(
        default="test_organization_id" if _IS_TEST_ENV else ...,
        description="Stytch organization ID (set via STYTCH_ORGANIZATION_ID env var)",
    )

    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0

    # Caching configuration
    cache_ttl: int = 300  # 5 minutes default
    cache_prefix: str = "ayz_auth"

    # Logging configuration
    log_level: str = "INFO"
    log_sensitive_data: bool = False  # Never log tokens in production

    # Request configuration
    request_timeout: int = 10  # seconds
    max_retries: int = 3

    model_config = {
        "env_prefix": "STYTCH_",
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Global settings instance
settings = AuthSettings()
