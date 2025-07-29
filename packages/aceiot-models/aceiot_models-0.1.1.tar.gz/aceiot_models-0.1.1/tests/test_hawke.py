"""Tests for Hawke models and utilities."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from aceiot_models.hawke import (
    HawkeConfig,
    HawkeConfigBase,
    HawkeConfigCreate,
    HawkeConfigCreateList,
    HawkeConfigList,
    HawkeConfigPaginatedResponse,
    HawkeConfigReference,
    HawkeConfigResponse,
    HawkeConfigUpdate,
    HawkeConfigWithIdentity,
    calculate_hawke_content_hash,
    create_hawke_agent_not_found_error,
    create_hawke_config_not_found_error,
    merge_hawke_configs,
    validate_hawke_config_format,
    validate_hawke_identity_uniqueness,
)


class TestHawkeConfigBase:
    """Test the HawkeConfigBase model."""

    def test_hawke_config_base_creation(self):
        """Test creating a HawkeConfigBase instance."""
        config = HawkeConfigBase(content_blob='{"key": "value"}', content_hash="abc123")
        assert config.content_blob == '{"key": "value"}'
        assert config.content_hash == "abc123"

    def test_hawke_config_base_no_hash(self):
        """Test creating HawkeConfigBase without hash."""
        config = HawkeConfigBase(content_blob='{"key": "value"}')
        assert config.content_blob == '{"key": "value"}'
        assert config.content_hash is None

    def test_hawke_config_base_empty_content_blob(self):
        """Test validation fails for empty content blob."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigBase(content_blob="")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_base_whitespace_content_blob(self):
        """Test validation fails for whitespace-only content blob."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigBase(content_blob="   \n\t  ")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_validate_content_hash_base64(self):
        """Test content hash validation with base64 format."""
        # Valid base64 hash
        config = HawkeConfigBase(content_blob='{"key": "value"}', content_hash="SGVsbG8gV29ybGQ=")
        assert config.content_hash == "SGVsbG8gV29ybGQ="

    def test_validate_content_hash_hex(self):
        """Test content hash validation with hex format."""
        # Valid hex hash
        config = HawkeConfigBase(content_blob='{"key": "value"}', content_hash="abc123def456789")
        assert config.content_hash == "abc123def456789"

    def test_validate_content_hash_invalid(self):
        """Test content hash validation with invalid format."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigBase(content_blob='{"key": "value"}', content_hash="invalid!@#$%hash")

        errors = exc_info.value.errors()
        assert any("Invalid hash format" in error["msg"] for error in errors)

    def test_validate_content_hash_empty_string(self):
        """Test content hash validation with empty string after strip."""
        config = HawkeConfigBase(content_blob='{"key": "value"}', content_hash="   ")
        # The validator strips whitespace, so empty string becomes empty
        assert config.content_hash == ""


class TestHawkeConfigModels:
    """Test HawkeConfig and related models."""

    def test_hawke_config_creation(self, sample_hawke_config_data):
        """Test creating a HawkeConfig instance."""
        config = HawkeConfig(**sample_hawke_config_data)
        assert config.id == sample_hawke_config_data["id"]
        assert config.content_blob == sample_hawke_config_data["content_blob"]
        assert config.content_hash == sample_hawke_config_data["content_hash"]

    def test_hawke_config_with_identity_creation(self, sample_hawke_config_data):
        """Test creating a HawkeConfigWithIdentity instance."""
        config = HawkeConfigWithIdentity(**sample_hawke_config_data)
        assert config.id == sample_hawke_config_data["id"]
        assert config.hawke_identity == sample_hawke_config_data["hawke_identity"]
        assert config.content_blob == sample_hawke_config_data["content_blob"]

    def test_hawke_config_with_identity_empty_identity(self):
        """Test validation fails for empty hawke_identity."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigWithIdentity(content_blob='{"key": "value"}', hawke_identity="")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_with_identity_whitespace_identity(self):
        """Test validation fails for whitespace-only hawke_identity."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigWithIdentity(content_blob='{"key": "value"}', hawke_identity="   ")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_with_identity_too_short(self):
        """Test validation fails for hawke_identity less than 2 characters."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigWithIdentity(content_blob='{"key": "value"}', hawke_identity="a")

        errors = exc_info.value.errors()
        assert any("at least 2 characters" in error["msg"] for error in errors)

    def test_hawke_config_with_identity_invalid_format(self):
        """Test validation fails for invalid hawke_identity format."""
        invalid_identities = [
            "123start",  # Starts with number
            "special!char",  # Contains special character
            "space in name",  # Contains space
            "_underscore_start",  # Starts with underscore
            "-hyphen-start",  # Starts with hyphen
            ".dot.start",  # Starts with dot
        ]

        for invalid_identity in invalid_identities:
            with pytest.raises(PydanticValidationError) as exc_info:
                HawkeConfigWithIdentity(
                    content_blob='{"key": "value"}', hawke_identity=invalid_identity
                )

            errors = exc_info.value.errors()
            assert any("must start with a letter" in error["msg"] for error in errors)

    def test_hawke_config_with_identity_valid_formats(self):
        """Test valid hawke_identity formats."""
        valid_identities = [
            "hawke",
            "hawkeAgent",
            "hawke_agent",
            "hawke-agent",
            "hawke.agent",
            "hawke123",
            "h2",
            "hawke_123_agent",
            "hawke.monitoring.agent",
            "HawkeAgent123",
        ]

        for valid_identity in valid_identities:
            config = HawkeConfigWithIdentity(
                content_blob='{"key": "value"}', hawke_identity=valid_identity
            )
            assert config.hawke_identity == valid_identity.strip()


class TestHawkeConfigCreate:
    """Test HawkeConfigCreate model."""

    def test_hawke_config_create_with_identity(self):
        """Test creating HawkeConfigCreate with identity."""
        config = HawkeConfigCreate(content_blob='{"key": "value"}', hawke_identity="hawke.agent")
        assert config.content_blob == '{"key": "value"}'
        assert config.hawke_identity == "hawke.agent"

    def test_hawke_config_create_without_identity(self):
        """Test creating HawkeConfigCreate without identity."""
        config = HawkeConfigCreate(content_blob='{"key": "value"}')
        assert config.content_blob == '{"key": "value"}'
        assert config.hawke_identity is None

    def test_hawke_config_create_empty_identity(self):
        """Test validation fails for empty hawke_identity when provided."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigCreate(content_blob='{"key": "value"}', hawke_identity="")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_create_invalid_identity(self):
        """Test validation fails for invalid hawke_identity format."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigCreate(content_blob='{"key": "value"}', hawke_identity="123invalid")

        errors = exc_info.value.errors()
        assert any("must start with a letter" in error["msg"] for error in errors)

    def test_hawke_config_create_identity_too_short(self):
        """Test validation fails for hawke_identity that is too short."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigCreate(content_blob='{"key": "value"}', hawke_identity="a")

        errors = exc_info.value.errors()
        assert any("at least 2 characters" in error["msg"] for error in errors)


class TestHawkeConfigUpdate:
    """Test HawkeConfigUpdate model."""

    def test_hawke_config_update_all_fields(self):
        """Test updating all fields."""
        update = HawkeConfigUpdate(
            content_blob='{"updated": true}',
            content_hash="newHash123",
            hawke_identity="updated.agent",
        )
        assert update.content_blob == '{"updated": true}'
        assert update.content_hash == "newHash123"
        assert update.hawke_identity == "updated.agent"

    def test_hawke_config_update_partial_fields(self):
        """Test updating partial fields."""
        update = HawkeConfigUpdate(content_blob='{"updated": true}')
        assert update.content_blob == '{"updated": true}'
        assert update.content_hash is None
        assert update.hawke_identity is None

    def test_hawke_config_update_empty_content_blob(self):
        """Test validation fails for empty content_blob when provided."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigUpdate(content_blob="")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_update_whitespace_content_blob(self):
        """Test validation fails for whitespace-only content_blob."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigUpdate(content_blob="   ")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_update_empty_identity(self):
        """Test validation fails for empty hawke_identity when provided."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigUpdate(hawke_identity="")

        errors = exc_info.value.errors()
        assert any("empty" in error["msg"] for error in errors)

    def test_hawke_config_update_invalid_identity(self):
        """Test validation fails for invalid hawke_identity format."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigUpdate(hawke_identity="_invalid")

        errors = exc_info.value.errors()
        assert any("must start with a letter" in error["msg"] for error in errors)

    def test_hawke_config_update_identity_too_short(self):
        """Test validation fails for hawke_identity that is too short."""
        with pytest.raises(PydanticValidationError) as exc_info:
            HawkeConfigUpdate(hawke_identity="x")

        errors = exc_info.value.errors()
        assert any("at least 2 characters" in error["msg"] for error in errors)


class TestHawkeConfigResponse:
    """Test HawkeConfigResponse model."""

    def test_hawke_config_response_creation(self, sample_hawke_config_data):
        """Test creating a HawkeConfigResponse instance."""
        response = HawkeConfigResponse(**sample_hawke_config_data)
        assert response.id == sample_hawke_config_data["id"]
        assert response.hawke_identity == sample_hawke_config_data["hawke_identity"]
        assert response.content_blob == sample_hawke_config_data["content_blob"]


class TestHawkeConfigReference:
    """Test HawkeConfigReference model."""

    def test_hawke_config_reference_creation(self):
        """Test creating a HawkeConfigReference instance."""
        ref = HawkeConfigReference(
            id="550e8400-e29b-41d4-a716-446655440000",
            hawke_identity="hawke.agent",
            content_hash="abc123",
        )
        assert ref.id == "550e8400-e29b-41d4-a716-446655440000"
        assert ref.hawke_identity == "hawke.agent"
        assert ref.content_hash == "abc123"

    def test_hawke_config_reference_no_hash(self):
        """Test creating HawkeConfigReference without hash."""
        ref = HawkeConfigReference(
            id="550e8400-e29b-41d4-a716-446655440000", hawke_identity="hawke.agent"
        )
        assert ref.content_hash is None


class TestHawkeConfigList:
    """Test HawkeConfigList model."""

    def test_hawke_config_list_creation(self, sample_hawke_config_data):
        """Test creating a HawkeConfigList instance."""
        config_list = HawkeConfigList(
            hawke_agents=[
                HawkeConfigWithIdentity(**sample_hawke_config_data),
                HawkeConfigWithIdentity(
                    content_blob='{"another": "config"}', hawke_identity="another.agent"
                ),
            ]
        )
        assert len(config_list.hawke_agents) == 2
        assert (
            config_list.hawke_agents[0].hawke_identity == sample_hawke_config_data["hawke_identity"]
        )

    def test_hawke_config_list_empty(self):
        """Test creating an empty HawkeConfigList."""
        config_list = HawkeConfigList(hawke_agents=[])
        assert len(config_list.hawke_agents) == 0


class TestHawkeConfigCreateList:
    """Test HawkeConfigCreateList model."""

    def test_hawke_config_create_list(self):
        """Test creating a HawkeConfigCreateList instance."""
        create_list = HawkeConfigCreateList(
            hawke_agents=[
                HawkeConfigCreate(content_blob='{"config": 1}', hawke_identity="agent1"),
                HawkeConfigCreate(content_blob='{"config": 2}'),
            ]
        )
        assert len(create_list.hawke_agents) == 2
        assert create_list.hawke_agents[0].hawke_identity == "agent1"
        assert create_list.hawke_agents[1].hawke_identity is None


class TestHawkeConfigPaginatedResponse:
    """Test HawkeConfigPaginatedResponse model."""

    def test_hawke_config_paginated_response(self, sample_hawke_config_data):
        """Test creating a HawkeConfigPaginatedResponse instance."""
        paginated = HawkeConfigPaginatedResponse(
            page=1,
            pages=2,
            per_page=10,
            total=15,
            items=[HawkeConfigWithIdentity(**sample_hawke_config_data)],
        )
        assert paginated.page == 1
        assert paginated.pages == 2
        assert paginated.total == 15
        assert len(paginated.items) == 1


class TestHawkeUtilityFunctions:
    """Test Hawke utility functions."""

    def test_create_hawke_config_not_found_error(self):
        """Test creating a Hawke config not found error."""
        error = create_hawke_config_not_found_error("config-123")
        assert error.error == "Hawke Configuration not found."
        assert error.details is not None
        assert error.details["resource"] == "Hawke Configuration"
        assert error.details["identifier"] == "config-123"
        assert error.code == "not_found"

    def test_create_hawke_agent_not_found_error(self):
        """Test creating a Hawke agent not found error."""
        error = create_hawke_agent_not_found_error("agent-456")
        assert error.error == "Hawke Agent Identity not found."
        assert error.details is not None
        assert error.details["resource"] == "Hawke Agent Identity"
        assert error.details["identifier"] == "agent-456"
        assert error.code == "not_found"

    def test_validate_hawke_identity_uniqueness_unique(self):
        """Test validating unique Hawke identity."""
        existing = ["agent1", "agent2", "agent3"]
        assert validate_hawke_identity_uniqueness("agent4", existing) is True
        assert validate_hawke_identity_uniqueness("AGENT4", existing) is True

    def test_validate_hawke_identity_uniqueness_duplicate(self):
        """Test validating duplicate Hawke identity."""
        existing = ["agent1", "agent2", "agent3"]
        assert validate_hawke_identity_uniqueness("agent1", existing) is False
        assert validate_hawke_identity_uniqueness("AGENT1", existing) is False
        assert validate_hawke_identity_uniqueness("  agent1  ", existing) is False

    def test_calculate_hawke_content_hash_hex(self):
        """Test calculating content hash in hex format."""
        content = '{"key": "value"}'
        hash_hex = calculate_hawke_content_hash(content, use_base64=False)
        # Should be a valid hex string
        assert all(c in "0123456789abcdef" for c in hash_hex)
        assert len(hash_hex) == 64  # SHA256 hex is 64 characters

    def test_calculate_hawke_content_hash_base64(self):
        """Test calculating content hash in base64 format."""
        content = '{"key": "value"}'
        hash_b64 = calculate_hawke_content_hash(content, use_base64=True)
        # Should be a valid base64 string
        assert hash_b64.endswith("=") or all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
            for c in hash_b64.rstrip("=")
        )

    def test_calculate_hawke_content_hash_consistency(self):
        """Test that same content produces same hash."""
        content = '{"key": "value"}'
        hash1 = calculate_hawke_content_hash(content)
        hash2 = calculate_hawke_content_hash(content)
        assert hash1 == hash2


class TestValidateHawkeConfigFormat:
    """Test validate_hawke_config_format function."""

    def test_validate_json_valid(self):
        """Test validating valid JSON content."""
        json_content = '{"key": "value", "number": 42}'
        assert validate_hawke_config_format(json_content, "json") is True

    def test_validate_json_invalid(self):
        """Test validating invalid JSON content."""
        with pytest.raises(ValueError) as exc_info:
            validate_hawke_config_format('{"key": invalid}', "json")
        assert "not valid JSON" in str(exc_info.value)

    def test_validate_yaml_valid(self):
        """Test validating valid YAML content."""
        yaml_content = """
key: value
number: 42
list:
  - item1
  - item2
"""
        assert validate_hawke_config_format(yaml_content, "yaml") is True

    def test_validate_yaml_invalid(self):
        """Test validating invalid YAML content."""
        # Use actually invalid YAML syntax - unclosed quote
        with pytest.raises(ValueError) as exc_info:
            validate_hawke_config_format('key: "unclosed quote', "yaml")
        assert "not valid YAML" in str(exc_info.value)

    def test_validate_toml_valid(self):
        """Test validating valid TOML content."""
        toml_content = """
[section]
key = "value"
number = 42
"""
        assert validate_hawke_config_format(toml_content, "toml") is True

    def test_validate_toml_invalid(self):
        """Test validating invalid TOML content."""
        with pytest.raises(ValueError) as exc_info:
            validate_hawke_config_format('[section]\nkey = invalid"', "toml")
        assert "not valid TOML" in str(exc_info.value)

    def test_validate_empty_content(self):
        """Test validating empty content."""
        with pytest.raises(ValueError) as exc_info:
            validate_hawke_config_format("", "json")
        assert "cannot be empty" in str(exc_info.value)

    def test_validate_whitespace_content(self):
        """Test validating whitespace-only content."""
        with pytest.raises(ValueError) as exc_info:
            validate_hawke_config_format("   \n\t  ", "json")
        assert "cannot be empty" in str(exc_info.value)

    def test_validate_no_format_specified(self):
        """Test validating content without format specification."""
        assert validate_hawke_config_format("any content here") is True
        assert validate_hawke_config_format('{"json": "content"}') is True
        assert validate_hawke_config_format("key: value") is True


class TestMergeHawkeConfigs:
    """Test merge_hawke_configs function."""

    def test_merge_hawke_configs_all_fields(self, sample_hawke_config_data):
        """Test merging configs with all fields updated."""
        # Create existing config
        existing = HawkeConfigWithIdentity(**sample_hawke_config_data)

        # Create update
        update = HawkeConfigUpdate(
            content_blob='{"updated": true}', content_hash="newHash", hawke_identity="updated.agent"
        )

        # Merge
        merged = merge_hawke_configs(existing, update)

        # Verify updates
        assert merged.content_blob == '{"updated": true}'
        assert merged.content_hash == "newHash"
        assert merged.hawke_identity == "updated.agent"

        # Verify unchanged fields
        assert merged.id == existing.id
        assert merged.created == existing.created

        # Verify updated timestamp changed
        assert merged.updated is not None and existing.updated is not None
        assert merged.updated > existing.updated

    def test_merge_hawke_configs_partial_update(self, sample_hawke_config_data):
        """Test merging configs with partial update."""
        # Create existing config
        existing = HawkeConfigWithIdentity(**sample_hawke_config_data)

        # Create partial update
        update = HawkeConfigUpdate(content_blob='{"partially": "updated"}')

        # Merge
        merged = merge_hawke_configs(existing, update)

        # Verify updates
        assert merged.content_blob == '{"partially": "updated"}'

        # Verify unchanged fields
        assert merged.content_hash == existing.content_hash
        assert merged.hawke_identity == existing.hawke_identity
        assert merged.id == existing.id

    def test_merge_hawke_configs_no_update(self, sample_hawke_config_data):
        """Test merging configs with empty update."""
        # Create existing config
        existing = HawkeConfigWithIdentity(**sample_hawke_config_data)

        # Create empty update
        update = HawkeConfigUpdate()

        # Merge
        merged = merge_hawke_configs(existing, update)

        # Verify all fields unchanged except updated timestamp
        assert merged.content_blob == existing.content_blob
        assert merged.content_hash == existing.content_hash
        assert merged.hawke_identity == existing.hawke_identity
        assert merged.id == existing.id
        assert merged.created == existing.created
        assert merged.updated is not None and existing.updated is not None
        assert merged.updated > existing.updated
