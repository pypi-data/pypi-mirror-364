"""Hawke configuration models for ACE IoT API."""

import json

import toml
import yaml
from pydantic import Field, field_validator

from .common import BaseModel, BaseUUIDEntityModel, PaginatedResponse


class HawkeConfigBase(BaseModel):
    """Base Hawke configuration model."""

    content_hash: str | None = Field(None, description="Hash of the configuration content")
    content_blob: str = Field(..., description="Hawke Config Content Blob")

    @field_validator("content_blob")
    @classmethod
    def validate_content_blob(cls, v: str) -> str:
        """Validate configuration content blob is not empty."""
        if not v or not v.strip():
            raise ValueError("Hawke configuration content cannot be empty")
        return v

    @field_validator("content_hash")
    @classmethod
    def validate_content_hash(cls, v: str | None) -> str | None:
        """Validate content hash format if provided."""
        if v is not None:
            v = v.strip()
            if v:
                # Accept both base64 and hex hash formats
                import re

                # Base64 hash pattern (roughly) or hex pattern
                if not (re.match(r"^[A-Za-z0-9+/]+=*$", v) or re.match(r"^[a-fA-F0-9]+$", v)):
                    raise ValueError("Invalid hash format - expected base64 or hex string")
        return v


class HawkeConfig(HawkeConfigBase, BaseUUIDEntityModel):
    """Full Hawke configuration model with all fields including ID and timestamps."""

    id: str | None = Field(None, description="Unique UUID for Hawke config")


class HawkeConfigWithIdentity(HawkeConfigBase, BaseUUIDEntityModel):
    """Hawke configuration model with agent identity."""

    id: str | None = Field(None, description="Unique UUID for Hawke config")
    hawke_identity: str = Field(..., description="Hawke agent identity")

    @field_validator("hawke_identity")
    @classmethod
    def validate_hawke_identity(cls, v: str) -> str:
        """Validate Hawke agent identity is not empty and follows naming conventions."""
        if not v or not v.strip():
            raise ValueError("Hawke agent identity cannot be empty")

        v = v.strip()
        if len(v) < 2:
            raise ValueError("Hawke agent identity must be at least 2 characters long")

        # Agent identities should be valid identifiers (no spaces, special chars)
        import re

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_.-]*$", v):
            raise ValueError(
                "Hawke agent identity must start with a letter and contain only letters, numbers, underscores, dots, and hyphens"
            )

        return v


class HawkeConfigCreate(HawkeConfigBase):
    """Hawke configuration creation model - excludes ID and timestamps."""

    hawke_identity: str | None = Field(None, description="Hawke agent identity")

    @field_validator("hawke_identity")
    @classmethod
    def validate_hawke_identity(cls, v: str | None) -> str | None:
        """Validate Hawke agent identity if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Hawke agent identity cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Hawke agent identity must be at least 2 characters long")

            import re

            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_.-]*$", v):
                raise ValueError(
                    "Hawke agent identity must start with a letter and contain only letters, numbers, underscores, dots, and hyphens"
                )

        return v


class HawkeConfigUpdate(BaseModel):
    """Hawke configuration update model - all fields optional."""

    content_hash: str | None = Field(None, description="Hash of the configuration content")
    content_blob: str | None = Field(None, description="Hawke Config Content Blob")
    hawke_identity: str | None = Field(None, description="Hawke agent identity")

    @field_validator("content_blob")
    @classmethod
    def validate_content_blob(cls, v: str | None) -> str | None:
        """Validate configuration content blob if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Hawke configuration content cannot be empty")
        return v

    @field_validator("hawke_identity")
    @classmethod
    def validate_hawke_identity(cls, v: str | None) -> str | None:
        """Validate Hawke agent identity if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Hawke agent identity cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Hawke agent identity must be at least 2 characters long")

            import re

            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_.-]*$", v):
                raise ValueError(
                    "Hawke agent identity must start with a letter and contain only letters, numbers, underscores, dots, and hyphens"
                )

        return v


class HawkeConfigResponse(HawkeConfigWithIdentity):
    """Hawke configuration response model - same as full HawkeConfigWithIdentity model."""


class HawkeConfigReference(BaseModel):
    """Minimal Hawke configuration reference for use in other models."""

    id: str = Field(..., description="Hawke config UUID")
    hawke_identity: str = Field(..., description="Hawke agent identity")
    content_hash: str | None = Field(None, description="Configuration hash")


# List models
class HawkeConfigList(BaseModel):
    """List of Hawke configurations wrapper."""

    hawke_agents: list[HawkeConfigWithIdentity] = Field(
        ..., description="List of Hawke configurations"
    )


class HawkeConfigCreateList(BaseModel):
    """List of Hawke configurations for bulk creation."""

    hawke_agents: list[HawkeConfigCreate] = Field(
        ..., description="List of Hawke configurations to create"
    )


class HawkeConfigPaginatedResponse(PaginatedResponse[HawkeConfigWithIdentity]):
    """Paginated response for Hawke configurations."""


# Utility functions
def create_hawke_config_not_found_error(config_identifier: str):
    """Create a standard Hawke config not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Hawke Configuration", config_identifier)


def create_hawke_agent_not_found_error(agent_identifier: str):
    """Create a standard Hawke agent not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Hawke Agent Identity", agent_identifier)


def validate_hawke_identity_uniqueness(identity: str, existing_identities: list[str]) -> bool:
    """Validate that Hawke agent identity is unique within a gateway."""
    return identity.lower().strip() not in [
        existing.lower().strip() for existing in existing_identities
    ]


def calculate_hawke_content_hash(content: str, use_base64: bool = False) -> str:
    """Calculate hash of Hawke configuration content."""
    import base64
    import hashlib

    # Calculate SHA256 hash
    hash_obj = hashlib.sha256(content.encode("utf-8"))

    if use_base64:
        return base64.b64encode(hash_obj.digest()).decode("ascii")
    else:
        return hash_obj.hexdigest()


def validate_hawke_config_format(content_blob: str, expected_format: str | None = None) -> bool:
    """Validate Hawke configuration content format."""
    if not content_blob or not content_blob.strip():
        raise ValueError("Hawke configuration content cannot be empty")

    if expected_format == "json":
        try:
            json.loads(content_blob)
            return True
        except (json.JSONDecodeError, ValueError):
            raise ValueError("Hawke configuration content is not valid JSON") from None

    elif expected_format == "yaml":
        try:
            yaml.safe_load(content_blob)
            return True
        except yaml.YAMLError:
            raise ValueError("Hawke configuration content is not valid YAML") from None

    elif expected_format == "toml":
        try:
            toml.loads(content_blob)
            return True
        except toml.TomlDecodeError:
            raise ValueError("Hawke configuration content is not valid TOML") from None

    # If no format specified, just check it's not empty
    return bool(content_blob.strip())


def merge_hawke_configs(
    existing_config: HawkeConfigWithIdentity, new_config: HawkeConfigUpdate
) -> HawkeConfigWithIdentity:
    """Merge existing Hawke config with updates."""
    updated_data = existing_config.model_dump()

    # Update fields that are provided in the update
    if new_config.content_blob is not None:
        updated_data["content_blob"] = new_config.content_blob

    if new_config.content_hash is not None:
        updated_data["content_hash"] = new_config.content_hash

    if new_config.hawke_identity is not None:
        updated_data["hawke_identity"] = new_config.hawke_identity

    # Update timestamp
    from datetime import UTC, datetime

    updated_data["updated"] = datetime.now(UTC)

    return HawkeConfigWithIdentity(**updated_data)


# Export all models
__all__ = [
    "HawkeConfig",
    "HawkeConfigBase",
    "HawkeConfigCreate",
    "HawkeConfigCreateList",
    "HawkeConfigList",
    "HawkeConfigPaginatedResponse",
    "HawkeConfigReference",
    "HawkeConfigResponse",
    "HawkeConfigUpdate",
    "HawkeConfigWithIdentity",
    "calculate_hawke_content_hash",
    "create_hawke_agent_not_found_error",
    "create_hawke_config_not_found_error",
    "merge_hawke_configs",
    "validate_hawke_config_format",
    "validate_hawke_identity_uniqueness",
]
