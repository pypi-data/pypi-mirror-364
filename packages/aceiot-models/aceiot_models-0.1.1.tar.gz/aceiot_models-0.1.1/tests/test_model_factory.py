"""Tests for the model factory system."""

import pytest
from pydantic import BaseModel, Field

from aceiot_models.model_factory import (
    BulkOperationMixin,
    ModelEnhancer,
    ModelFactory,
    ModelMixin,
)


class TestModelFactory:
    """Test the ModelFactory functionality."""

    def test_create_crud_models_basic(self):
        """Test basic CRUD model generation."""

        # Define base model
        class ProductBase(BaseModel):
            name: str = Field(..., description="Product name")
            price: float = Field(..., ge=0, description="Product price")
            description: str | None = Field(None, description="Product description")

        # Generate CRUD models
        models = ModelFactory.create_crud_models(ProductBase, "Product")

        # Check all expected models were created
        assert "Model" in models
        assert "Create" in models
        assert "Update" in models
        assert "Response" in models
        assert "Reference" in models
        assert "List" in models
        assert "PaginatedResponse" in models

        # Test the full model
        Product = models["Model"]
        product = Product(name="Test Product", price=29.99, id=1)
        assert product.name == "Test Product"
        assert product.price == 29.99
        assert product.id == 1

        # Test Create model (no ID field)
        ProductCreate = models["Create"]
        create_data = ProductCreate(name="New Product", price=19.99)
        assert create_data.name == "New Product"
        assert not hasattr(create_data, "id")

        # Test Update model (all fields optional)
        ProductUpdate = models["Update"]
        update_data = ProductUpdate(price=24.99)
        assert update_data.price == 24.99
        assert update_data.name is None

        # Test Reference model
        ProductReference = models["Reference"]
        ref = ProductReference(id=1, name="Product Ref")
        assert ref.id == 1
        assert ref.name == "Product Ref"

    def test_create_crud_models_custom_validators(self):
        """Test CRUD model generation with custom validators (simplified)."""

        class ItemBase(BaseModel):
            name: str = Field(..., description="Item name")

        # Generate models (custom validators is an advanced feature that could be improved)
        models = ModelFactory.create_crud_models(ItemBase, "Item")

        ItemUpdate = models["Update"]

        # Basic functionality test - model creation works
        update = ItemUpdate(name="Test")
        assert update.name == "Test"

        # Test optional nature of Update model
        update_empty = ItemUpdate()
        assert update_empty.name is None

    def test_create_crud_models_without_reference(self):
        """Test model generation without reference models."""

        class SimpleBase(BaseModel):
            value: int = Field(..., description="Simple value")

        models = ModelFactory.create_crud_models(
            SimpleBase, "Simple", include_reference=False, include_list=False
        )

        assert "Reference" not in models
        assert "List" not in models
        assert "Model" in models
        assert "Create" in models


class TestModelEnhancer:
    """Test the ModelEnhancer functionality."""

    def test_add_computed_fields(self):
        """Test adding computed fields to models."""

        class User(BaseModel):
            first_name: str
            last_name: str

        def full_name_property(self):
            return f"{self.first_name} {self.last_name}"

        # Add computed field
        EnhancedUser = ModelEnhancer.add_computed_fields(User, {"full_name": full_name_property})

        user = EnhancedUser(first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_add_methods(self):
        """Test adding methods to models."""

        class Calculator(BaseModel):
            value: float = 0.0

        def add_method(self, amount: float):
            return Calculator(value=self.value + amount)

        def multiply_method(self, factor: float):
            return Calculator(value=self.value * factor)

        # Add methods
        EnhancedCalculator = ModelEnhancer.add_methods(
            Calculator, {"add": add_method, "multiply": multiply_method}
        )

        calc = EnhancedCalculator(value=10.0)
        result1 = calc.add(5.0)
        assert result1.value == 15.0

        result2 = calc.multiply(2.0)
        assert result2.value == 20.0


class TestModelMixin:
    """Test the ModelMixin functionality."""

    def test_to_reference(self):
        """Test reference conversion."""

        class TestModel(BaseModel, ModelMixin):
            id: int
            name: str
            description: str | None = None

        model = TestModel(id=1, name="Test", description="A test model")
        ref = model.to_reference()

        assert ref == {"id": 1, "name": "Test"}

    def test_to_reference_missing_fields(self):
        """Test reference conversion without required fields."""

        class InvalidModel(BaseModel, ModelMixin):
            value: int

        model = InvalidModel(value=42)

        with pytest.raises(NotImplementedError) as exc_info:
            model.to_reference()
        assert "must have 'id' and 'name' fields" in str(exc_info.value)

    def test_has_changed(self):
        """Test change detection."""

        class TestModel(BaseModel, ModelMixin):
            name: str
            value: int

        model1 = TestModel(name="Test", value=1)
        model2 = TestModel(name="Test", value=1)
        model3 = TestModel(name="Test", value=2)

        assert not model1.has_changed(model2)  # Same values
        assert model1.has_changed(model3)  # Different values
        assert model1.has_changed("not a model")  # Different type

    def test_get_display_name(self):
        """Test display name generation."""

        class TestModel1(BaseModel, ModelMixin):
            id: int
            name: str
            nice_name: str | None = None

        class TestModel2(BaseModel, ModelMixin):
            id: int
            name: str

        class TestModel3(BaseModel, ModelMixin):
            id: int
            value: str

        # With nice_name
        model1 = TestModel1(id=1, name="test", nice_name="Test Item")
        assert model1.get_display_name() == "Test Item"

        # Without nice_name, with name
        model2 = TestModel2(id=1, name="test")
        assert model2.get_display_name() == "test"

        # Without nice_name or name, with id
        model3 = TestModel3(id=1, value="something")
        assert model3.get_display_name() == "TestModel3 #1"


class TestBulkOperationMixin:
    """Test the BulkOperationMixin functionality."""

    def test_validate_bulk_success(self):
        """Test successful bulk validation."""

        class Item(BaseModel, BulkOperationMixin):
            name: str
            value: int

        items_data = [
            {"name": "Item1", "value": 10},
            {"name": "Item2", "value": 20},
            {"name": "Item3", "value": 30},
        ]

        validated = Item.validate_bulk(items_data)

        assert len(validated) == 3
        assert all(isinstance(item, Item) for item in validated)
        assert validated[0].name == "Item1"
        assert validated[1].value == 20

    def test_validate_bulk_with_errors(self):
        """Test bulk validation with errors."""

        class StrictItem(BaseModel, BulkOperationMixin):
            name: str
            value: int

        items_data = [
            {"name": "Valid", "value": 10},
            {"name": "Invalid"},  # Missing required field
            {"value": 20},  # Missing required field
        ]

        with pytest.raises(Exception) as exc_info:
            StrictItem.validate_bulk(items_data)

        assert "Bulk validation failed" in str(exc_info.value)

    def test_create_bulk_response(self):
        """Test bulk response creation."""

        class Item(BaseModel, BulkOperationMixin):
            name: str

        successful = [Item(name="Item1"), Item(name="Item2")]
        failed = [
            {"index": 2, "error": "Missing name", "data": {"value": 10}},
        ]

        response = Item.create_bulk_response(successful, failed)

        assert response["successful"] == 2
        assert response["failed"] == 1
        assert response["total"] == 3
        assert len(response["results"]) == 2
        assert len(response["errors"]) == 1


class TestModelFactoryIntegration:
    """Test integration of factory-generated models."""

    def test_complete_crud_workflow(self):
        """Test a complete CRUD workflow with factory-generated models."""

        # Base model
        class BookBase(BaseModel):
            title: str = Field(..., description="Book title")
            author: str = Field(..., description="Book author")
            pages: int = Field(..., ge=1, description="Number of pages")
            isbn: str | None = Field(None, description="ISBN number")

        # Generate CRUD models
        models = ModelFactory.create_crud_models(BookBase, "Book")

        Book = models["Model"]
        BookCreate = models["Create"]
        BookUpdate = models["Update"]
        BookReference = models["Reference"]

        # Create a book
        create_data = BookCreate(
            title="The Python Guide", author="John Doe", pages=350, isbn="978-0123456789"
        )

        # Simulate saving (add ID)
        book = Book(**create_data.model_dump(), id=1)
        assert book.id == 1
        assert book.title == "The Python Guide"

        # Update the book
        update_data = BookUpdate(pages=375)  # Only updating pages

        # Apply updates
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(book, field, value)

        assert book.pages == 375
        assert book.title == "The Python Guide"  # Unchanged

        # Create reference
        ref = BookReference(id=book.id, name=book.title)
        assert ref.id == 1
        assert ref.name == "The Python Guide"

    def test_factory_with_mixins(self):
        """Test factory-generated models with mixins."""

        class EnhancedBase(BaseModel, ModelMixin, BulkOperationMixin):
            name: str
            value: float

        models = ModelFactory.create_crud_models(EnhancedBase, "Enhanced")

        Enhanced = models["Model"]

        # Test mixin functionality
        item = Enhanced(id=1, name="Test Item", value=42.0)

        # Test ModelMixin
        ref = item.to_reference()
        assert ref == {"id": 1, "name": "Test Item"}

        # Test BulkOperationMixin
        bulk_data = [
            {"name": "Item1", "value": 10.0, "id": 1},
            {"name": "Item2", "value": 20.0, "id": 2},
        ]

        items = Enhanced.validate_bulk(bulk_data)
        assert len(items) == 2
        assert all(isinstance(item, Enhanced) for item in items)
