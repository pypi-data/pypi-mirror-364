"""Client models for ACE IoT API."""

from pydantic import Field, field_validator

from .cache import cache_model_operation
from .common import BaseEntityModel, BaseModel, PaginatedResponse
from .events import EventType, publish_event, publishes_events
from .model_factory import BulkOperationMixin, ModelMixin
from .validators import validate_name, validate_string_length


@publishes_events(created=True, updated=True, deleted=True)
class ClientBase(BaseModel, ModelMixin, BulkOperationMixin):
    """Base client model with common fields."""

    name: str = Field(..., description="Client name", max_length=512)
    nice_name: str | None = Field(None, description="Display name for client", max_length=256)
    address: str | None = Field(None, description="Client address", max_length=512)
    tech_contact: str | None = Field(
        None, description="Technical contact information", max_length=512
    )
    bus_contact: str | None = Field(
        None, description="Business contact information", max_length=512
    )

    # Use reusable validators with field_validator decorator

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, v: str) -> str:
        """Validate the name field."""
        return validate_name(v, min_length=2, strip_whitespace=True)

    @field_validator("nice_name")
    @classmethod
    def validate_nice_name_field(cls, v: str | None) -> str | None:
        """Validate the nice_name field."""
        return validate_string_length(v, min_length=2, strip_whitespace=True)

    @field_validator("address")
    @classmethod
    def validate_address_field(cls, v: str | None) -> str | None:
        """Validate the address field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    @field_validator("tech_contact")
    @classmethod
    def validate_tech_contact_field(cls, v: str | None) -> str | None:
        """Validate the tech_contact field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    @field_validator("bus_contact")
    @classmethod
    def validate_bus_contact_field(cls, v: str | None) -> str | None:
        """Validate the bus_contact field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    def get_display_name_cached(self) -> str:
        """Get the display name for this client (cached method)."""
        return self.get_display_name()

    @cache_model_operation("Client", "search_by_name", ttl=600, key_params=["name"])
    def search_similar_names(self, threshold: float = 0.8) -> list[str]:
        """Search for clients with similar names (cached)."""
        # This would typically query a database
        # For now, return empty list as demonstration
        _ = threshold  # Mark as intentionally unused
        return []


class Client(ClientBase, BaseEntityModel):
    """Full client model with all fields including ID and timestamps."""

    # Override to make id required (non-None)
    id: int | None = Field(None, description="Unique ID for client")


class ClientCreate(ClientBase):
    """Client creation model - excludes ID and timestamps."""


class ClientUpdate(BaseModel):
    """Client update model - all fields optional."""

    name: str | None = Field(None, description="Client name", max_length=512)
    nice_name: str | None = Field(None, description="Display name for client", max_length=256)
    address: str | None = Field(None, description="Client address", max_length=512)
    tech_contact: str | None = Field(
        None, description="Technical contact information", max_length=512
    )
    bus_contact: str | None = Field(
        None, description="Business contact information", max_length=512
    )

    # Reuse validators from base model but allow None
    @field_validator("name")
    @classmethod
    def validate_name_field(cls, v: str | None) -> str | None:
        """Validate the name field."""
        return validate_name(v, min_length=2, strip_whitespace=True)

    @field_validator("nice_name")
    @classmethod
    def validate_nice_name_field(cls, v: str | None) -> str | None:
        """Validate the nice_name field."""
        return validate_string_length(v, min_length=2, strip_whitespace=True)

    @field_validator("address")
    @classmethod
    def validate_address_field(cls, v: str | None) -> str | None:
        """Validate the address field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    @field_validator("tech_contact")
    @classmethod
    def validate_tech_contact_field(cls, v: str | None) -> str | None:
        """Validate the tech_contact field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    @field_validator("bus_contact")
    @classmethod
    def validate_bus_contact_field(cls, v: str | None) -> str | None:
        """Validate the bus_contact field."""
        return validate_string_length(v, max_length=512, strip_whitespace=True)

    def apply_updates(self, target: "Client") -> "Client":
        """Apply updates to target client instance."""
        update_data = self.model_dump(exclude_unset=True, exclude_none=True)

        for field, value in update_data.items():
            if hasattr(target, field):
                old_value = getattr(target, field)
                if old_value != value:
                    setattr(target, field, value)
                    # Publish update event
                    publish_event(
                        EventType.MODEL_UPDATED,
                        model_name="Client",
                        model_id=target.id,
                        data={"field": field, "old_value": old_value, "new_value": value},
                    )

        return target


class ClientResponse(Client):
    """Client response model - same as full Client model."""


class ClientReference(BaseModel):
    """Minimal client reference for use in other models."""

    id: int = Field(..., description="Client ID")
    name: str = Field(..., description="Client name")


class ClientList(BaseModel):
    """List of clients wrapper."""

    clients: list[Client] = Field(..., description="List of clients")


class ClientPaginatedResponse(PaginatedResponse[Client]):
    """Paginated response for clients."""


# Enhanced utility functions for client operations
@cache_model_operation("Client", "not_found_error", ttl=300, key_params=["client_identifier"])
def create_client_not_found_error(client_identifier: str):
    """Create a standard client not found error (cached)."""
    from .common import create_not_found_error

    return create_not_found_error("Client", client_identifier)


@cache_model_operation("Client", "validate_uniqueness", ttl=60, key_params=["name"])
def validate_client_name_uniqueness(name: str, existing_names: list[str]) -> bool:
    """Validate that client name is unique (cached)."""
    normalized_name = name.lower().strip()
    normalized_existing = [existing.lower().strip() for existing in existing_names]

    is_unique = normalized_name not in normalized_existing

    # Publish validation event if name is not unique
    if not is_unique:
        publish_event(
            EventType.VALIDATION_FAILED,
            model_name="Client",
            data={
                "field": "name",
                "value": name,
                "error": "Client name must be unique",
                "existing_names": existing_names,
            },
        )

    return is_unique


def get_client_statistics(clients: list[Client]) -> dict[str, any]:
    """Get statistics about client data."""
    if not clients:
        return {"total": 0, "with_nice_name": 0, "with_address": 0, "with_contacts": 0}

    stats = {
        "total": len(clients),
        "with_nice_name": sum(1 for c in clients if c.nice_name),
        "with_address": sum(1 for c in clients if c.address),
        "with_tech_contact": sum(1 for c in clients if c.tech_contact),
        "with_bus_contact": sum(1 for c in clients if c.bus_contact),
        "with_both_contacts": sum(1 for c in clients if c.tech_contact and c.bus_contact),
    }

    return stats


# Export all models and utilities
__all__ = [
    "Client",
    "ClientBase",
    "ClientCreate",
    "ClientList",
    "ClientPaginatedResponse",
    "ClientReference",
    "ClientResponse",
    "ClientUpdate",
    "create_client_not_found_error",
    "get_client_statistics",
    "validate_client_name_uniqueness",
]
