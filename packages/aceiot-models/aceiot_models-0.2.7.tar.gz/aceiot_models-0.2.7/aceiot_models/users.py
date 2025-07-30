"""User and authentication models for ACE IoT API."""

from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field, field_validator

from .common import BaseEntityModel, BaseModel, PaginatedResponse


class AceRole(str, Enum):
    """Enum for user roles in the ACE system."""

    SUPERUSER = "superuser"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Role(BaseModel):
    """Role model."""

    id: int = Field(..., description="Unique role ID")
    name: AceRole = Field(..., description="Role name")
    description: str | None = Field(None, description="Role description", max_length=512)

    @field_validator("name")
    @classmethod
    def validate_role_name(cls, v: AceRole) -> AceRole:
        """Validate role name is a valid AceRole."""
        if not isinstance(v, AceRole):
            raise ValueError(
                f"Invalid role name. Must be one of: {[role.value for role in AceRole.__members__.values()]}"
            )
        return v


class UserBase(BaseModel):
    """Base user model with common fields."""

    username: str | None = Field(None, description="Username", max_length=256)
    first_name: str | None = Field(None, description="First name", max_length=256)
    last_name: str | None = Field(None, description="Last name", max_length=256)
    contact: str | None = Field(None, description="Contact information", max_length=256)
    email: EmailStr = Field(..., description="Email address")
    active: bool | None = Field(True, description="Whether user is active")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None

            if len(v) < 2:
                raise ValueError("Username must be at least 2 characters long")

            # Username should be alphanumeric with underscores/hyphens
            import re

            if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                raise ValueError(
                    "Username can only contain letters, numbers, underscores, and hyphens"
                )

        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_fields(cls, v: str | None) -> str | None:
        """Validate name fields."""
        if v is not None:
            v = v.strip()
            if not v:
                return None

            if len(v) < 1:
                raise ValueError("Name must not be empty")

        return v

    @field_validator("email")
    @classmethod
    def validate_email_not_empty(cls, v: EmailStr) -> EmailStr:
        """Ensure email is provided."""
        if not v:
            raise ValueError("Email address is required")
        return v


class User(UserBase, BaseEntityModel):
    """Full user model with all fields including ID and timestamps."""

    id: int | None = Field(None, description="Unique user ID")
    confirmed_at: datetime | None = Field(None, description="Email confirmation timestamp")
    fs_uniquifier: str | None = Field(None, description="Flask-Security uniquifier")
    client_ids: list[int] | None = Field(
        default_factory=list, description="List of client IDs user has access to"
    )
    role_id: int | None = Field(None, description="Primary role ID")


class UserCreate(UserBase):
    """User creation model - excludes ID and timestamps."""

    password: str = Field(..., description="User password", min_length=8)
    role_id: int | None = Field(None, description="Primary role ID")
    client_ids: list[int] | None = Field(
        default_factory=list, description="List of client IDs to assign"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, lowercase, and digit
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )

        return v


class UserUpdate(BaseModel):
    """User update model - all fields optional."""

    username: str | None = Field(None, description="Username", max_length=256)
    first_name: str | None = Field(None, description="First name", max_length=256)
    last_name: str | None = Field(None, description="Last name", max_length=256)
    contact: str | None = Field(None, description="Contact information", max_length=256)
    email: EmailStr | None = Field(None, description="Email address")
    active: bool | None = Field(None, description="Whether user is active")
    password: str | None = Field(None, description="New password", min_length=8)
    role_id: int | None = Field(None, description="Primary role ID")
    client_ids: list[int] | None = Field(None, description="List of client IDs to assign")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """Validate password if provided."""
        if v is not None:
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters long")

            has_upper = any(c.isupper() for c in v)
            has_lower = any(c.islower() for c in v)
            has_digit = any(c.isdigit() for c in v)

            if not (has_upper and has_lower and has_digit):
                raise ValueError(
                    "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
                )

        return v


class UserResponse(User):
    """User response model - excludes sensitive fields like password."""


class UserReference(BaseModel):
    """Minimal user reference for use in other models."""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")


class ClientUser(BaseEntityModel):
    """Client-User relationship model for RBAC."""

    id: int | None = Field(None, description="Unique relationship ID")
    client_id: int = Field(..., description="Client ID")
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Role ID for this client-user relationship")

    # Optional nested references
    client: dict | None = Field(None, description="Client reference")
    user: dict | None = Field(None, description="User reference")
    role: Role | None = Field(None, description="Role details")


class ClientUserCreate(BaseModel):
    """Client-User relationship creation model."""

    client_id: int = Field(..., description="Client ID")
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Role ID for this client-user relationship")


class ClientUserUpdate(BaseModel):
    """Client-User relationship update model."""

    role_id: int | None = Field(None, description="Role ID for this client-user relationship")


class ClientUserResponse(ClientUser):
    """Client-User response model - same as full ClientUser model."""


# List models
class UserList(BaseModel):
    """List of users wrapper."""

    users: list[User] = Field(..., description="List of users")


class ClientUserList(BaseModel):
    """List of client-user relationships wrapper."""

    client_users: list[ClientUser] = Field(..., description="List of client-user relationships")


class UserPaginatedResponse(PaginatedResponse[User]):
    """Paginated response for users."""


class ClientUserPaginatedResponse(PaginatedResponse[ClientUser]):
    """Paginated response for client-user relationships."""


# Utility functions
def create_user_not_found_error(user_identifier: str):
    """Create a standard user not found error."""
    from .common import create_not_found_error

    return create_not_found_error("User", user_identifier)


def create_client_user_not_found_error(client_user_identifier: str):
    """Create a standard client-user relationship not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Client-User relationship", client_user_identifier)


def validate_email_uniqueness(email: str, existing_emails: list[str]) -> bool:
    """Validate that email is unique."""
    return email.lower().strip() not in [existing.lower().strip() for existing in existing_emails]


def validate_username_uniqueness(username: str, existing_usernames: list[str]) -> bool:
    """Validate that username is unique."""
    if not username:
        return True
    return username.lower().strip() not in [
        existing.lower().strip() for existing in existing_usernames
    ]


def check_user_has_role(
    _user: User, required_role: AceRole, user_role: AceRole | None = None
) -> bool:
    """Check if user has the required role or higher.

    Args:
        _user: The User object
        required_role: The minimum required role
        user_role: The user's actual role (optional). If not provided, the function will return False.
                   In a real application, this would be fetched from the database using user.role_id.

    Returns:
        bool: True if user has the required role or higher, False otherwise
    """
    role_hierarchy = {AceRole.VIEWER: 1, AceRole.EDITOR: 2, AceRole.ADMIN: 3, AceRole.SUPERUSER: 4}

    # If user_role is not provided, we can't determine permissions
    if user_role is None:
        return False

    # Get user's role level
    user_role_level = role_hierarchy.get(user_role, 0)

    # Check if user's role level meets the required level
    required_level = role_hierarchy.get(required_role, 0)
    return user_role_level >= required_level


def generate_password_hash(password: str) -> str:
    """Generate password hash for storage."""
    import hashlib
    import secrets

    # Generate salt
    salt = secrets.token_hex(32)

    # Hash password with salt
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )

    # Return salt + hash
    return salt + password_hash.hex()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash."""
    import hashlib

    try:
        # Extract salt (first 64 chars) and hash
        salt = password_hash[:64]
        stored_hash = password_hash[64:]

        # Hash provided password with stored salt
        provided_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )

        # Compare hashes
        return provided_hash.hex() == stored_hash
    except Exception:
        return False


# Export all models
__all__ = [
    "AceRole",
    "ClientUser",
    "ClientUserCreate",
    "ClientUserList",
    "ClientUserPaginatedResponse",
    "ClientUserResponse",
    "ClientUserUpdate",
    "Role",
    "User",
    "UserBase",
    "UserCreate",
    "UserList",
    "UserPaginatedResponse",
    "UserReference",
    "UserResponse",
    "UserUpdate",
    "check_user_has_role",
    "create_client_user_not_found_error",
    "create_user_not_found_error",
    "generate_password_hash",
    "validate_email_uniqueness",
    "validate_username_uniqueness",
    "verify_password",
]
