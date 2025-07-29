"""Volttron agent and configuration models for ACE IoT API."""

import json

import yaml
from pydantic import Field, field_validator

from .common import BaseModel, BaseUUIDEntityModel, PaginatedResponse


class VolttronAgentPackage(BaseUUIDEntityModel):
    """Volttron agent package model."""

    id: str | None = Field(None, description="Unique UUID for package")
    package_name: str = Field(..., description="Name of the package")
    object_hash: str | None = Field(None, description="SHA hash of the package object")
    object_path: str | None = Field(None, description="Storage path of the package object")
    description: str | None = Field(None, description="Package description")

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Validate package name is not empty."""
        if not v or not v.strip():
            raise ValueError("Package name cannot be empty")

        v = v.strip()
        if len(v) < 2:
            raise ValueError("Package name must be at least 2 characters long")

        return v

    @field_validator("object_hash")
    @classmethod
    def validate_object_hash(cls, v: str | None) -> str | None:
        """Validate object hash format if provided."""
        if v is not None:
            v = v.strip()
            if v:
                # Basic hash validation (assuming SHA256 - 64 hex chars)
                import re

                if not re.match(r"^[a-fA-F0-9]{64}$", v):
                    raise ValueError("Invalid hash format - expected 64 character hex string")
        return v


class VolttronAgentBase(BaseModel):
    """Base Volttron agent model with common fields."""

    identity: str = Field(..., description="Unique agent identity")
    package_name: str = Field(..., description="Name of the agent package")
    revision: str | None = Field(None, description="Package revision")
    tag: str | None = Field(None, description="Agent tag")
    active: bool | None = Field(True, description="Whether the agent is active")

    @field_validator("identity")
    @classmethod
    def validate_identity(cls, v: str) -> str:
        """Validate agent identity is not empty and follows naming conventions."""
        if not v or not v.strip():
            raise ValueError("Agent identity cannot be empty")

        v = v.strip()
        if len(v) < 2:
            raise ValueError("Agent identity must be at least 2 characters long")

        # Agent identities should be valid identifiers (no spaces, special chars)
        import re

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "Agent identity must start with a letter and contain only letters, numbers, underscores, and hyphens"
            )

        return v

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Validate package name is not empty."""
        if not v or not v.strip():
            raise ValueError("Package name cannot be empty")
        return v.strip()


class VolttronAgent(VolttronAgentBase, BaseUUIDEntityModel):
    """Full Volttron agent model with all fields including ID and timestamps."""

    id: str | None = Field(None, description="Unique UUID for agent")
    package_id: str | None = Field(None, description="ID of associated package")
    volttron_agent_package_id: str | None = Field(None, description="Volttron agent package ID")


class VolttronAgentCreate(VolttronAgentBase):
    """Volttron agent creation model - excludes ID and timestamps."""

    volttron_agent_package_id: str | None = Field(
        None, description="ID of the package to associate with this agent"
    )


class VolttronAgentUpdate(BaseModel):
    """Volttron agent update model - all fields optional."""

    identity: str | None = Field(None, description="Unique agent identity")
    package_name: str | None = Field(None, description="Name of the agent package")
    revision: str | None = Field(None, description="Package revision")
    tag: str | None = Field(None, description="Agent tag")
    active: bool | None = Field(None, description="Whether the agent is active")
    volttron_agent_package_id: str | None = Field(
        None, description="ID of the package to associate with this agent"
    )

    @field_validator("identity")
    @classmethod
    def validate_identity(cls, v: str | None) -> str | None:
        """Validate agent identity if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Agent identity cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Agent identity must be at least 2 characters long")

            import re

            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
                raise ValueError(
                    "Agent identity must start with a letter and contain only letters, numbers, underscores, and hyphens"
                )

        return v


class VolttronAgentResponse(VolttronAgent):
    """Volttron agent response model - same as full VolttronAgent model."""


class AgentConfigBase(BaseModel):
    """Base agent configuration model."""

    agent_identity: str = Field(..., description="Identity of the agent this config belongs to")
    config_name: str | None = Field("config", description="Name of the configuration")
    config_hash: str | None = Field(None, description="Hash of the configuration content")
    blob: str = Field(..., description="Configuration blob/content")
    active: bool | None = Field(True, description="Whether this configuration is active")

    @field_validator("agent_identity")
    @classmethod
    def validate_agent_identity(cls, v: str) -> str:
        """Validate agent identity is not empty."""
        if not v or not v.strip():
            raise ValueError("Agent identity cannot be empty")
        return v.strip()

    @field_validator("blob")
    @classmethod
    def validate_blob(cls, v: str) -> str:
        """Validate configuration blob is not empty."""
        if not v or not v.strip():
            raise ValueError("Configuration blob cannot be empty")
        return v

    @field_validator("config_hash")
    @classmethod
    def validate_config_hash(cls, v: str | None) -> str | None:
        """Validate configuration hash format if provided."""
        if v is not None:
            v = v.strip()
            if v:
                # Accept both base64 and hex hash formats
                import re

                # Base64 hash pattern (roughly)
                if not (re.match(r"^[A-Za-z0-9+/]+=*$", v) or re.match(r"^[a-fA-F0-9]+$", v)):
                    raise ValueError("Invalid hash format - expected base64 or hex string")
        return v


class AgentConfig(AgentConfigBase, BaseUUIDEntityModel):
    """Full agent configuration model with all fields including ID and timestamps."""

    id: str | None = Field(None, description="Unique UUID for agent config")


class AgentConfigCreate(AgentConfigBase):
    """Agent configuration creation model - excludes ID and timestamps."""


class AgentConfigUpdate(BaseModel):
    """Agent configuration update model - all fields optional except agent identity."""

    config_name: str | None = Field(None, description="Name of the configuration")
    config_hash: str | None = Field(None, description="Hash of the configuration content")
    blob: str | None = Field(None, description="Configuration blob/content")
    active: bool | None = Field(None, description="Whether this configuration is active")

    @field_validator("blob")
    @classmethod
    def validate_blob(cls, v: str | None) -> str | None:
        """Validate configuration blob if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Configuration blob cannot be empty")
        return v


class AgentConfigResponse(AgentConfig):
    """Agent configuration response model - same as full AgentConfig model."""


# Combined models for complex operations
class VolttronAgentConfigPackage(BaseModel):
    """Combined model for agent, config, and package operations."""

    volttron_agent: VolttronAgent = Field(..., description="Volttron agent")
    agent_config: AgentConfig | None = Field(None, description="Agent configuration")
    volttron_agent_package: VolttronAgentPackage | None = Field(
        None, description="Associated package"
    )


class VolttronAgentConfigPackageCreate(BaseModel):
    """Combined model for creating agent with config and package."""

    volttron_agent: VolttronAgentCreate = Field(..., description="Volttron agent to create")
    agent_config: AgentConfigCreate | None = Field(
        None, description="Agent configuration to create"
    )


# List models
class VolttronAgentList(BaseModel):
    """List of Volttron agents wrapper."""

    volttron_agents: list[VolttronAgent] = Field(..., description="List of Volttron agents")


class AgentConfigList(BaseModel):
    """List of agent configurations wrapper."""

    agent_configs: list[AgentConfig] = Field(..., description="List of agent configurations")


class VolttronAgentPaginatedResponse(PaginatedResponse[VolttronAgent]):
    """Paginated response for Volttron agents."""


class AgentConfigPaginatedResponse(PaginatedResponse[AgentConfig]):
    """Paginated response for agent configurations."""


class VolttronAgentPackagePaginatedResponse(PaginatedResponse[VolttronAgentPackage]):
    """Paginated response for Volttron agent packages."""


# Utility functions
def create_volttron_agent_not_found_error(agent_identifier: str):
    """Create a standard Volttron agent not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Volttron Agent", agent_identifier)


def create_agent_config_not_found_error(config_identifier: str):
    """Create a standard agent config not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Agent Config", config_identifier)


def validate_agent_identity_uniqueness(identity: str, existing_identities: list[str]) -> bool:
    """Validate that agent identity is unique."""
    return identity.lower().strip() not in [
        existing.lower().strip() for existing in existing_identities
    ]


def calculate_config_hash(content: str, use_base64: bool = False) -> str:
    """Calculate hash of configuration content."""
    import base64
    import hashlib

    # Calculate SHA256 hash
    hash_obj = hashlib.sha256(content.encode("utf-8"))

    if use_base64:
        return base64.b64encode(hash_obj.digest()).decode("ascii")
    else:
        return hash_obj.hexdigest()


def validate_config_blob_format(blob: str, expected_format: str | None = None) -> bool:
    """Validate configuration blob format (JSON, YAML, etc.)."""
    if expected_format == "json":
        try:
            json.loads(blob)
            return True
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError("Configuration blob is not valid JSON") from e

    elif expected_format == "yaml":
        try:
            yaml.safe_load(blob)
            return True
        except yaml.YAMLError as e:
            raise ValueError("Configuration blob is not valid YAML") from e

    # If no format specified, just check it's not empty
    return bool(blob.strip())


# Export all models
__all__ = [
    "AgentConfig",
    "AgentConfigBase",
    "AgentConfigCreate",
    "AgentConfigList",
    "AgentConfigPaginatedResponse",
    "AgentConfigResponse",
    "AgentConfigUpdate",
    "VolttronAgent",
    "VolttronAgentBase",
    "VolttronAgentConfigPackage",
    "VolttronAgentConfigPackageCreate",
    "VolttronAgentCreate",
    "VolttronAgentList",
    "VolttronAgentPackage",
    "VolttronAgentPackagePaginatedResponse",
    "VolttronAgentPaginatedResponse",
    "VolttronAgentResponse",
    "VolttronAgentUpdate",
    "calculate_config_hash",
    "create_agent_config_not_found_error",
    "create_volttron_agent_not_found_error",
    "validate_agent_identity_uniqueness",
    "validate_config_blob_format",
]
