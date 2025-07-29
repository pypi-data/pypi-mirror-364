"""Tests for client models."""

import pytest
from pydantic import ValidationError

from aceiot_models.clients import (
    Client,
    ClientBase,
    ClientCreate,
    ClientList,
    ClientPaginatedResponse,
    ClientReference,
    ClientResponse,
    ClientUpdate,
    create_client_not_found_error,
    validate_client_name_uniqueness,
)
from tests.conftest import assert_model_fields


class TestClientBase:
    """Test the ClientBase model."""

    def test_client_base_creation_valid(self, sample_client_data):
        """Test creating a valid ClientBase."""
        client = ClientBase(
            name=sample_client_data["name"],
            nice_name=sample_client_data["nice_name"],
            address=sample_client_data["address"],
            tech_contact=sample_client_data["tech_contact"],
            bus_contact=sample_client_data["bus_contact"],
        )

        assert client.name == sample_client_data["name"]
        assert client.nice_name == sample_client_data["nice_name"]
        assert client.address == sample_client_data["address"]
        assert client.tech_contact == sample_client_data["tech_contact"]
        assert client.bus_contact == sample_client_data["bus_contact"]

    def test_client_base_name_validation(self):
        """Test name validation in ClientBase."""
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name="")

        errors = exc_info.value.errors()
        assert any("cannot be empty" in error["msg"] for error in errors)

        # Test name with only whitespace
        with pytest.raises(ValidationError):
            ClientBase(name="   ")

        # Test name too short
        with pytest.raises(ValidationError):
            ClientBase(name="a")

    def test_client_base_name_trimming(self):
        """Test that name is trimmed of whitespace."""
        client = ClientBase(name="  test_client  ")
        assert client.name == "test_client"

    def test_client_base_nice_name_validation(self):
        """Test nice_name validation."""
        # Valid nice name
        client = ClientBase(name="test", nice_name="Test Client")
        assert client.nice_name == "Test Client"

        # Empty nice name should become None
        client = ClientBase(name="test", nice_name="")
        assert client.nice_name is None

        # Nice name too short
        with pytest.raises(ValidationError):
            ClientBase(name="test", nice_name="a")

    def test_client_base_optional_fields(self):
        """Test that optional fields work correctly."""
        client = ClientBase(name="test")

        assert client.name == "test"
        assert client.nice_name is None
        assert client.address is None
        assert client.tech_contact is None
        assert client.bus_contact is None


class TestClient:
    """Test the full Client model."""

    def test_client_creation_from_dict(self, sample_client_data):
        """Test creating Client from dictionary data."""
        client = Client.model_validate(sample_client_data)
        assert_model_fields(client, sample_client_data)

    def test_client_optional_id(self, sample_client_data):
        """Test that id is optional for Client."""
        data = sample_client_data.copy()
        del data["id"]

        # This should not raise an error since id is now optional
        client = Client.model_validate(data)
        assert client.id is None
        assert client.name == data["name"]

    def test_client_inheritance(self, sample_client_data):
        """Test that Client inherits from ClientBase and BaseEntityModel."""
        client = Client.model_validate(sample_client_data)

        # Should have ClientBase fields
        assert hasattr(client, "name")
        assert hasattr(client, "nice_name")

        # Should have BaseEntityModel fields
        assert hasattr(client, "id")
        assert hasattr(client, "created")
        assert hasattr(client, "updated")


class TestClientCreate:
    """Test the ClientCreate model."""

    def test_client_create_valid(self, sample_client_data):
        """Test creating ClientCreate with valid data."""
        create_data = {
            "name": sample_client_data["name"],
            "nice_name": sample_client_data["nice_name"],
            "address": sample_client_data["address"],
            "tech_contact": sample_client_data["tech_contact"],
            "bus_contact": sample_client_data["bus_contact"],
        }

        client_create = ClientCreate.model_validate(create_data)
        assert client_create.name == create_data["name"]
        assert client_create.nice_name == create_data["nice_name"]

    def test_client_create_no_id(self, sample_client_data):
        """Test that ClientCreate doesn't include id field."""
        client_create = ClientCreate.model_validate({"name": sample_client_data["name"]})

        # Should not have id field
        assert not hasattr(client_create, "id")

    def test_client_create_minimal(self):
        """Test ClientCreate with minimal required data."""
        client_create = ClientCreate(name="minimal_client")

        assert client_create.name == "minimal_client"
        assert client_create.nice_name is None


class TestClientUpdate:
    """Test the ClientUpdate model."""

    def test_client_update_all_optional(self):
        """Test that all fields are optional in ClientUpdate."""
        client_update = ClientUpdate()

        assert client_update.name is None
        assert client_update.nice_name is None
        assert client_update.address is None
        assert client_update.tech_contact is None
        assert client_update.bus_contact is None

    def test_client_update_partial(self, sample_client_data):
        """Test partial update with some fields."""
        client_update = ClientUpdate(name="updated_name", nice_name="Updated Name")

        assert client_update.name == "updated_name"
        assert client_update.nice_name == "Updated Name"
        assert client_update.address is None

    def test_client_update_name_validation(self):
        """Test name validation in ClientUpdate."""
        # Valid name
        client_update = ClientUpdate(name="valid_name")
        assert client_update.name == "valid_name"

        # Invalid name
        with pytest.raises(ValidationError):
            ClientUpdate(name="")

    def test_client_update_nice_name_validation(self):
        """Test nice_name validation in ClientUpdate."""
        # Valid nice name
        client_update = ClientUpdate(nice_name="Valid Nice Name")
        assert client_update.nice_name == "Valid Nice Name"

        # Empty nice name should become None
        client_update = ClientUpdate(nice_name="")
        assert client_update.nice_name is None


class TestClientResponse:
    """Test the ClientResponse model."""

    def test_client_response_same_as_client(self, sample_client_data):
        """Test that ClientResponse is same as Client model."""
        client_response = ClientResponse.model_validate(sample_client_data)
        client = Client.model_validate(sample_client_data)

        assert client_response.model_dump() == client.model_dump()


class TestClientReference:
    """Test the ClientReference model."""

    def test_client_reference_creation(self):
        """Test creating ClientReference."""
        client_ref = ClientReference(id=1, name="test_client")

        assert client_ref.id == 1
        assert client_ref.name == "test_client"

    def test_client_reference_required_fields(self):
        """Test that id and name are required."""
        with pytest.raises(ValidationError):
            ClientReference(id=1)  # Missing name

        with pytest.raises(ValidationError):
            ClientReference(name="test")  # Missing id


class TestClientList:
    """Test the ClientList model."""

    def test_client_list_creation(self, sample_client_data):
        """Test creating ClientList."""
        client = Client.model_validate(sample_client_data)
        client_list = ClientList(clients=[client])

        assert len(client_list.clients) == 1
        assert client_list.clients[0].name == client.name

    def test_client_list_empty(self):
        """Test creating empty ClientList."""
        client_list = ClientList(clients=[])
        assert len(client_list.clients) == 0


class TestClientPaginatedResponse:
    """Test the ClientPaginatedResponse model."""

    def test_client_paginated_response_creation(self, sample_client_data):
        """Test creating ClientPaginatedResponse."""
        client = Client.model_validate(sample_client_data)

        response = ClientPaginatedResponse(page=1, pages=1, per_page=10, total=1, items=[client])

        assert response.page == 1
        assert len(response.items) == 1
        assert response.items[0].name == client.name


class TestClientUtilities:
    """Test client utility functions."""

    def test_validate_client_name_uniqueness(self):
        """Test validate_client_name_uniqueness function."""
        existing_names = ["client1", "client2", "Client3"]

        # Test unique name
        assert validate_client_name_uniqueness("new_client", existing_names) is True

        # Test duplicate name (case insensitive)
        assert validate_client_name_uniqueness("client1", existing_names) is False
        assert validate_client_name_uniqueness("CLIENT1", existing_names) is False
        assert validate_client_name_uniqueness("Client3", existing_names) is False

        # Test with whitespace
        assert validate_client_name_uniqueness(" client1 ", existing_names) is False

    def test_create_client_not_found_error(self):
        """Test create_client_not_found_error function."""
        error = create_client_not_found_error("123")

        assert error.error == "Client not found."
        assert error.code == "not_found"
        assert error.details is not None
        assert error.details["resource"] == "Client"
        assert error.details["identifier"] == "123"


class TestClientModelIntegration:
    """Test integration between different client models."""

    def test_create_update_response_flow(self, sample_client_data):
        """Test flow from create to update to response."""
        # Create
        create_data = {"name": "new_client", "nice_name": "New Client", "address": "123 New Street"}
        client_create = ClientCreate.model_validate(create_data)

        # Simulate DB save (add id and timestamps)
        client_data = client_create.model_dump()
        client_data.update(
            {"id": 1, "created": "2024-01-15T10:30:45Z", "updated": "2024-01-15T10:30:45Z"}
        )
        client = Client.model_validate(client_data)

        # Update
        client_update = ClientUpdate(nice_name="Updated Client")
        assert client_update.nice_name == "Updated Client"

        # Response
        client_response = ClientResponse.model_validate(client.model_dump())
        assert client_response.id == client.id
        assert client_response.name == client.name

    def test_model_serialization_consistency(self, sample_client_data):
        """Test that models serialize/deserialize consistently."""
        original_client = Client.model_validate(sample_client_data)

        # Serialize to dict
        client_dict = original_client.model_dump()

        # Deserialize back
        reconstructed_client = Client.model_validate(client_dict)

        # Should be identical
        assert original_client.model_dump() == reconstructed_client.model_dump()

    def test_model_json_serialization(self, sample_client_data):
        """Test JSON serialization/deserialization."""
        original_client = Client.model_validate(sample_client_data)

        # Serialize to JSON
        json_str = original_client.model_dump_json()

        # Deserialize from JSON
        reconstructed_client = Client.model_validate_json(json_str)

        # Should be identical
        assert original_client.model_dump() == reconstructed_client.model_dump()


class TestClientFieldLengthLimits:
    """Test field length limits and constraints."""

    def test_name_length_limit(self):
        """Test name field length limit."""
        # Valid length
        long_name = "a" * 512
        client = ClientBase(name=long_name)
        assert client.name == long_name

        # Test very long name - should raise ValidationError due to max_length=512
        very_long_name = "a" * 1000
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name=very_long_name)
        assert "string_too_long" in str(exc_info.value)

    def test_nice_name_length_limit(self):
        """Test nice_name field length limit."""
        # Valid length
        long_nice_name = "a" * 256
        client = ClientBase(name="test", nice_name=long_nice_name)
        assert client.nice_name == long_nice_name

    def test_address_length_limit(self):
        """Test address field length limit."""
        # Valid length
        long_address = "a" * 512
        client = ClientBase(name="test", address=long_address)
        assert client.address == long_address


class TestClientEdgeCases:
    """Test edge cases and error conditions."""

    def test_client_with_special_characters(self):
        """Test client with special characters in fields."""
        client = ClientBase(
            name="test_client",
            nice_name="Test & Client Co.",
            address="123 Main St., Suite #456",
            tech_contact="tech@test-client.com",
            bus_contact="Contact: John O'Connor",
        )

        assert client.nice_name is not None and "Test & Client Co." in client.nice_name
        assert client.address is not None and "Suite #456" in client.address
        assert client.bus_contact is not None and "O'Connor" in client.bus_contact

    def test_client_unicode_support(self):
        """Test client with unicode characters."""
        client = ClientBase(
            name="test_client",
            nice_name="Tëst Çlíënt",
            address="123 Straße München",
            tech_contact="técnico@test.com",
        )

        assert client.nice_name == "Tëst Çlíënt"
        assert client.address is not None and "München" in client.address
        assert client.tech_contact is not None and "técnico" in client.tech_contact

    def test_client_none_values(self):
        """Test client with None values for optional fields."""
        client = ClientBase(
            name="test_client", nice_name=None, address=None, tech_contact=None, bus_contact=None
        )

        assert client.name == "test_client"
        assert client.nice_name is None
        assert client.address is None
        assert client.tech_contact is None
        assert client.bus_contact is None
