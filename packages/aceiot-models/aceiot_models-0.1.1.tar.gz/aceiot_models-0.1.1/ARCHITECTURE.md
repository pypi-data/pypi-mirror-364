# ACE IoT Models - Architecture Documentation

## Overview

This document outlines the architectural improvements made to the ACE IoT Models library to enhance robustness, modularity, and maintainability.

## 🏗️ New Architectural Components

### 1. Validator System (`validators.py`)

**Purpose**: Centralized, reusable validation functions to eliminate code duplication.

**Key Features**:
- Simple function-based validators (easier than decorators)
- Consistent error messaging
- Configurable validation rules
- Type-safe implementations

**Usage Example**:
```python
from pydantic import field_validator
from aceiot_models.validators import validate_name, validate_email

class UserModel(BaseModel):
    name: str
    email: str
    
    @field_validator("name")
    @classmethod
    def validate_name_field(cls, v: str) -> str:
        return validate_name(v, min_length=2, strip_whitespace=True)
    
    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        return validate_email(v)
```

**Available Validators**:
- `validate_name()` - Name field validation with configurable rules
- `validate_email()` - Email format validation
- `validate_url()` - URL format validation with HTTPS option
- `validate_mac_address()` - MAC address format validation
- `validate_coordinate()` - Geographic coordinate validation
- `validate_string_length()` - String length constraints
- `validate_positive_integer()` - Non-negative integer validation
- `validate_coordinate_pair()` - Lat/lon pair validation
- `validate_unique_in_list()` - List uniqueness validation
- `validate_hierarchy()` - Hierarchical relationship validation

### 2. Model Factory (`model_factory.py`)

**Purpose**: Generate CRUD model variants automatically to reduce boilerplate code.

**Key Features**:
- Automatic generation of Create/Update/Response models
- Consistent patterns across all models
- Built-in mixins for common functionality
- Extensible design

**Usage Example**:
```python
from aceiot_models.model_factory import ModelFactory

# Base model
class ProductBase(BaseModel):
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")

# Generate all CRUD models
models = ModelFactory.create_crud_models(ProductBase, "Product")

# Access generated models
Product = models["Model"]           # Full model with ID
ProductCreate = models["Create"]    # Create model (no ID)
ProductUpdate = models["Update"]    # Update model (all optional)
ProductResponse = models["Response"] # API response model
```

**Model Mixins**:
- `ModelMixin`: Common functionality (display names, change detection)
- `BulkOperationMixin`: Bulk validation and response creation

### 3. Configuration Management (`config.py`)

**Purpose**: Centralized configuration system replacing hardcoded values.

**Key Features**:
- Environment variable integration
- Type-safe configuration classes
- Feature flags
- Hierarchical configuration structure

**Configuration Sections**:
- **ValidationConfig**: Field validation rules and constraints
- **FeatureFlags**: Enable/disable functionality
- **CacheConfig**: Caching behavior settings
- **SecurityConfig**: Security-related settings
- **DatabaseConfig**: Database connection settings
- **NotificationConfig**: Email and webhook settings

**Usage Example**:
```python
from aceiot_models.config import get_config

config = get_config()

# Use configuration values
max_length = config.validation.name_max_length
cache_enabled = config.features.enable_caching
default_ttl = config.cache.default_ttl

# Environment variable override
# ACEIOT_ENABLE_CACHING=false will disable caching
```

### 4. Caching System (`cache.py`)

**Purpose**: Add caching support for expensive operations.

**Key Features**:
- LRU cache implementation
- Model-specific caching
- TTL support
- Cache statistics
- Decorator-based caching

**Usage Example**:
```python
from aceiot_models.cache import cache_model_operation, get_cache_stats

class MyModel(BaseModel):
    name: str
    
    @cache_model_operation("MyModel", "expensive_calc", ttl=600)
    def expensive_calculation(self, param: int) -> float:
        # This result will be cached for 10 minutes
        return complex_calculation(param)

# Get cache statistics
stats = get_cache_stats()
print(f"Cache hit rate: {stats['MyModel']['hit_rate']}")
```

### 5. Event System (`events.py`)

**Purpose**: Decoupled event-driven architecture for notifications and side effects.

**Key Features**:
- Model lifecycle events (created, updated, deleted)
- Asynchronous event handling
- Built-in handlers (logging, cache invalidation, webhooks)
- Event filtering and middleware
- Event history tracking

**Usage Example**:
```python
from aceiot_models.events import publish_event, EventType, EventHandler

# Automatic event publishing
@publishes_events(created=True, updated=True)
class MyModel(BaseModel):
    name: str

# Custom event handler
class CustomHandler(EventHandler):
    def handle_sync(self, event: Event) -> None:
        if event.event_type == EventType.MODEL_CREATED:
            send_notification(event.data)

# Register handler
from aceiot_models.events import get_event_bus
get_event_bus().subscribe(CustomHandler())
```

## 🔄 Improved Architecture Patterns

### 1. Enhanced Error Handling

The existing comprehensive error handling system in `exceptions.py` has been integrated with the new components:

```python
from aceiot_models.exceptions import ValidationError, ModelNotFoundError

# Enhanced error creation with events
def create_user(user_data: dict) -> User:
    try:
        user = User(**user_data)
        publish_event(EventType.MODEL_CREATED, "User", user.id)
        return user
    except ValidationError as e:
        publish_event(EventType.VALIDATION_FAILED, "User", data=e.details)
        raise
```

### 2. Backward Compatibility

All improvements maintain backward compatibility:
- Existing models continue to work unchanged
- New features are opt-in
- Configuration defaults preserve current behavior
- Gradual migration path available

### 3. Type Safety Enhancements

Improved type safety throughout:
- Generic type support in factory patterns
- Proper type hints for all validators
- Configuration classes with full type checking
- Event system with typed event data

## 📊 Performance Improvements

### 1. Caching Strategy

- **Model Operations**: Cache expensive database queries and calculations
- **Validation Results**: Cache validation outcomes for repeated data
- **Configuration**: Cache configuration loading

### 2. Async Support

- **Event Handling**: Non-blocking event processing
- **Webhook Delivery**: Asynchronous webhook calls
- **Background Tasks**: Support for async operations

### 3. Memory Management

- **LRU Cache**: Automatic memory management with size limits
- **Event History**: Configurable history size limits
- **Lazy Loading**: Configuration loaded on first access

## 🔒 Security Enhancements

### 1. Configuration Security

- **Environment Variables**: Secure configuration via environment
- **Feature Flags**: Runtime security feature toggles
- **HTTPS Enforcement**: Configurable HTTPS requirements

### 2. Validation Security

- **Input Sanitization**: Enhanced input validation
- **Length Limits**: Configurable field length restrictions
- **Pattern Matching**: Robust regex-based validation

## 📈 Monitoring and Observability

### 1. Cache Metrics

```python
from aceiot_models.cache import get_cache_stats

# Monitor cache performance
stats = get_cache_stats()
for model_name, model_stats in stats.items():
    print(f"{model_name}: {model_stats['hit_rate']:.2%} hit rate")
```

### 2. Event Tracking

```python
from aceiot_models.events import get_event_bus

# Monitor system events
bus = get_event_bus()
recent_events = bus.get_history(limit=100)
```

### 3. Configuration Monitoring

```python
from aceiot_models.config import get_config

config = get_config()
if config.debug:
    print(f"Running in debug mode: {config.environment}")
```

## 🚀 Migration Guide

### Phase 1: Basic Integration

1. **Update imports** to include new components:
   ```python
   from aceiot_models import cache, config, events, validators
   ```

2. **Replace hardcoded values** with configuration:
   ```python
   # Before
   MAX_NAME_LENGTH = 512
   
   # After
   max_length = get_config().validation.name_max_length
   ```

### Phase 2: Enhanced Functionality

1. **Add caching** to expensive operations:
   ```python
   @cache_model_operation("Model", "operation", ttl=300)
   def expensive_function(self): ...
   ```

2. **Enable event handling**:
   ```python
   @publishes_events(created=True, updated=True)
   class MyModel(BaseModel): ...
   ```

### Phase 3: Full Migration

1. **Use model factory** for new models:
   ```python
   models = ModelFactory.create_crud_models(BaseModel, "Entity")
   ```

2. **Replace custom validators** with reusable ones:
   ```python
   # Use validate_name, validate_email, etc.
   ```

## 📋 Best Practices

### 1. Validator Usage

- **Reuse validators** instead of writing custom ones
- **Chain validators** for complex validation rules
- **Use consistent error messages** via validator functions

### 2. Caching Strategy

- **Cache read-heavy operations** with appropriate TTL
- **Monitor cache hit rates** and adjust strategies
- **Use model-specific cache keys** for better organization

### 3. Event Handling

- **Keep handlers lightweight** for better performance
- **Use async handlers** for I/O operations
- **Filter events** to reduce unnecessary processing

### 4. Configuration Management

- **Use environment variables** for deployment-specific values
- **Group related settings** in configuration sections
- **Validate configuration** on application startup

## 🔧 Development Workflow

### 1. Adding New Models

1. Create base model with common fields
2. Use validator functions for field validation
3. Generate CRUD models with ModelFactory
4. Add caching to expensive operations
5. Enable event publishing if needed

### 2. Testing Strategy

1. Test individual validators with edge cases
2. Test model factory-generated models
3. Test cache behavior and invalidation
4. Test event publishing and handling
5. Test configuration loading and validation

### 3. Performance Monitoring

1. Monitor cache hit rates regularly
2. Track event processing times
3. Monitor memory usage of caches
4. Profile validation performance

This architecture provides a robust, scalable foundation for the ACE IoT Models library while maintaining backward compatibility and enabling future enhancements.