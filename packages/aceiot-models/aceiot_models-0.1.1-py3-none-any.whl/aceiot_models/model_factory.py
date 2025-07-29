"""Model factory for generating CRUD models with reduced duplication."""

from typing import Any, TypeVar, get_origin

from pydantic import Field, create_model

from .common import BaseEntityModel, BaseModel, PaginatedResponse


T = TypeVar("T", bound=BaseModel)


class ModelFactory:
    """Factory for generating CRUD models following consistent patterns."""

    @staticmethod
    def create_crud_models(
        base_model: type[BaseModel],
        name: str,
        include_reference: bool = True,
        include_list: bool = True,
        custom_validators: dict[str, Any] | None = None,
    ) -> dict[str, type[BaseModel]]:
        """Generate all CRUD models for a given base model.

        Args:
            base_model: The base model class with common fields
            name: The name prefix for generated models (e.g., "Client")
            include_reference: Whether to create a Reference model
            include_list: Whether to create a List model
            custom_validators: Custom validators to apply to generated models

        Returns:
            Dictionary of generated model classes
        """
        models = {}

        # Create the full model (with ID and timestamps)
        full_model_fields = {}
        for field_name, field_info in base_model.model_fields.items():
            full_model_fields[field_name] = (field_info.annotation, field_info)

        # Add entity fields
        full_model_fields["id"] = (
            int | None,
            Field(None, description=f"Unique ID for {name.lower()}"),
        )

        FullModel = create_model(
            name,
            __base__=(base_model, BaseEntityModel),
            **full_model_fields,
        )
        models["Model"] = FullModel

        # Create the Create model (exclude ID and timestamps)
        CreateModel = create_model(f"{name}Create", __base__=base_model)
        models["Create"] = CreateModel

        # Create the Update model (all fields optional)
        update_fields = {}
        for field_name, field_info in base_model.model_fields.items():
            # Make field optional
            annotation = field_info.annotation
            if get_origin(annotation) is not type(None):
                # Field is not already optional
                annotation = annotation | None

            # Create new field with same attributes but optional
            new_field = Field(
                None,
                description=field_info.description,
                # Copy important field constraints safely
                max_length=getattr(field_info, "max_length", None),
                min_length=getattr(field_info, "min_length", None),
                ge=getattr(field_info, "ge", None),
                le=getattr(field_info, "le", None),
                gt=getattr(field_info, "gt", None),
                lt=getattr(field_info, "lt", None),
            )
            update_fields[field_name] = (annotation, new_field)

        # Create the Update model with custom validators
        update_model_dict = {"__base__": BaseModel, **update_fields}

        # Apply custom validators if provided
        if custom_validators:
            for validator_name, validator_func in custom_validators.items():
                update_model_dict[validator_name] = validator_func

        UpdateModel = create_model(f"{name}Update", **update_model_dict)

        models["Update"] = UpdateModel

        # Create the Response model (same as full model)
        ResponseModel = create_model(f"{name}Response", __base__=FullModel)
        models["Response"] = ResponseModel

        # Create Reference model if requested
        if include_reference:
            ref_fields = {
                "id": (int, Field(..., description=f"{name} ID")),
                "name": (str, Field(..., description=f"{name} name")),
            }
            ReferenceModel = create_model(f"{name}Reference", __base__=BaseModel, **ref_fields)
            models["Reference"] = ReferenceModel

        # Create List model if requested
        if include_list:
            list_fields = {
                f"{name.lower()}s": (
                    list[FullModel],
                    Field(..., description=f"List of {name.lower()}s"),
                )
            }
            ListModel = create_model(f"{name}List", __base__=BaseModel, **list_fields)
            models["List"] = ListModel

        # Create Paginated Response
        PaginatedModel = type(
            f"{name}PaginatedResponse",
            (PaginatedResponse[FullModel],),
            {"__doc__": f"Paginated response for {name.lower()}s"},
        )
        models["PaginatedResponse"] = PaginatedModel

        return models


class ModelEnhancer:
    """Enhance existing models with additional functionality."""

    @staticmethod
    def add_computed_fields(model_class: type[T], computed_fields: dict[str, Any]) -> type[T]:
        """Add computed fields to a model class."""
        for field_name, field_func in computed_fields.items():
            setattr(model_class, field_name, property(field_func))
        return model_class

    @staticmethod
    def add_validators(model_class: type[T], validators: dict[str, Any]) -> type[T]:
        """Add validators to a model class."""
        for validator_name, validator_func in validators.items():
            setattr(model_class, validator_name, validator_func)
        return model_class

    @staticmethod
    def add_methods(model_class: type[T], methods: dict[str, Any]) -> type[T]:
        """Add methods to a model class."""
        for method_name, method_func in methods.items():
            setattr(model_class, method_name, method_func)
        return model_class


class ModelMixin:
    """Base mixin class for adding common functionality to models."""

    def to_reference(self) -> dict[str, Any]:
        """Convert model to reference format."""
        if hasattr(self, "id") and hasattr(self, "name"):
            return {"id": self.id, "name": self.name}
        raise NotImplementedError("Model must have 'id' and 'name' fields")

    def has_changed(self, other: Any) -> bool:
        """Check if model has changed compared to another instance."""
        if not isinstance(other, self.__class__):
            return True

        for field_name in self.__class__.model_fields:
            if getattr(self, field_name) != getattr(other, field_name, None):
                return True

        return False

    def get_display_name(self) -> str:
        """Get display name for the model."""
        if hasattr(self, "nice_name") and self.nice_name:
            return self.nice_name
        elif hasattr(self, "name"):
            return self.name
        elif hasattr(self, "id"):
            return f"{self.__class__.__name__} #{self.id}"
        return str(self)


class BulkOperationMixin:
    """Mixin for models that support bulk operations."""

    @classmethod
    def validate_bulk(cls, items: list[dict[str, Any]]) -> list["BulkOperationMixin"]:
        """Validate a list of items for bulk operation."""
        validated_items = []
        errors = []

        for i, item in enumerate(items):
            try:
                validated_item = cls(**item)
                validated_items.append(validated_item)
            except Exception as e:
                errors.append({"index": i, "error": str(e), "data": item})

        if errors:
            from .exceptions import ValidationError

            raise ValidationError(
                f"Bulk validation failed for {len(errors)} items",
                details={"errors": errors, "total": len(items)},
            )

        return validated_items

    @classmethod
    def create_bulk_response(
        cls, successful: list[Any], failed: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create a standardized bulk operation response."""
        return {
            "successful": len(successful),
            "failed": len(failed),
            "total": len(successful) + len(failed),
            "results": successful,
            "errors": failed,
        }


# Export all classes
__all__ = [
    "BulkOperationMixin",
    "ModelEnhancer",
    "ModelFactory",
    "ModelMixin",
]
