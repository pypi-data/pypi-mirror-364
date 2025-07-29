"""Event system for decoupled notifications in ACE IoT models."""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .config import get_config


logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standard event types for model operations."""

    # CRUD events
    MODEL_CREATED = "model.created"
    MODEL_UPDATED = "model.updated"
    MODEL_DELETED = "model.deleted"
    MODEL_RESTORED = "model.restored"

    # Bulk operations
    BULK_CREATED = "bulk.created"
    BULK_UPDATED = "bulk.updated"
    BULK_DELETED = "bulk.deleted"

    # Validation events
    VALIDATION_FAILED = "validation.failed"
    VALIDATION_WARNING = "validation.warning"

    # State changes
    STATE_CHANGED = "state.changed"
    STATUS_CHANGED = "status.changed"

    # Relationship events
    RELATIONSHIP_ADDED = "relationship.added"
    RELATIONSHIP_REMOVED = "relationship.removed"

    # System events
    CACHE_INVALIDATED = "cache.invalidated"
    CONFIG_CHANGED = "config.changed"
    ERROR_OCCURRED = "error.occurred"

    # Custom events
    CUSTOM = "custom"


class Event(BaseModel):
    """Base event model."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    model_name: str | None = Field(None, description="Name of the model involved")
    model_id: Any | None = Field(None, description="ID of the model instance")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = Field(default_factory=dict, description="Event data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Event metadata")
    user_id: str | None = Field(None, description="User who triggered the event")
    correlation_id: str | None = Field(None, description="Correlation ID for tracking")


class EventHandler:
    """Base class for event handlers."""

    def __init__(self, name: str | None = None):
        self.name = name or self.__class__.__name__

    async def handle_async(self, event: Event) -> None:
        """Handle event asynchronously."""

    def handle_sync(self, event: Event) -> None:
        """Handle event synchronously."""

    def should_handle(self, event: Event) -> bool:
        """Determine if this handler should process the event."""
        _ = event  # Mark as intentionally unused
        return True


class EventFilter:
    """Filter events based on criteria."""

    def __init__(
        self,
        event_types: list[EventType] | None = None,
        model_names: list[str] | None = None,
        custom_filter: Callable[[Event], bool] | None = None,
    ):
        self.event_types = set(event_types) if event_types else None
        self.model_names = set(model_names) if model_names else None
        self.custom_filter = custom_filter

    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        if self.event_types and event.event_type not in self.event_types:
            return False

        if self.model_names and event.model_name not in self.model_names:
            return False

        return not (self.custom_filter and not self.custom_filter(event))


class EventBus:
    """Central event bus for publishing and subscribing to events."""

    def __init__(self):
        self._sync_handlers: dict[str, list[tuple[EventHandler, EventFilter | None]]] = defaultdict(
            list
        )
        self._async_handlers: dict[str, list[tuple[EventHandler, EventFilter | None]]] = (
            defaultdict(list)
        )
        self._middleware: list[Callable[[Event], Event | None]] = []
        self._event_history: list[Event] = []
        self._max_history_size = 1000

    def subscribe(
        self,
        handler: EventHandler,
        event_types: list[EventType] | None = None,
        event_filter: EventFilter | None = None,
        is_async: bool = False,
    ) -> None:
        """Subscribe a handler to events."""
        if event_filter is None and event_types:
            event_filter = EventFilter(event_types=event_types)

        handler_list = self._async_handlers if is_async else self._sync_handlers

        if event_types:
            for event_type in event_types:
                handler_list[event_type.value].append((handler, event_filter))
        else:
            handler_list["*"].append((handler, event_filter))

    def unsubscribe(self, handler: EventHandler) -> None:
        """Unsubscribe a handler from all events."""
        for handlers in self._sync_handlers.values():
            handlers[:] = [(h, f) for h, f in handlers if h != handler]

        for handlers in self._async_handlers.values():
            handlers[:] = [(h, f) for h, f in handlers if h != handler]

    def add_middleware(self, middleware: Callable[[Event], Event | None]) -> None:
        """Add middleware to process events before handlers."""
        self._middleware.append(middleware)

    def publish(self, event: Event) -> None:
        """Publish an event synchronously."""
        # Apply middleware
        for middleware in self._middleware:
            event = middleware(event)
            if event is None:
                return  # Middleware filtered out the event

        # Store in history
        self._add_to_history(event)

        # Get handlers for this event type
        handlers = list(self._sync_handlers.get(event.event_type.value, []))
        handlers.extend(self._sync_handlers.get("*", []))

        # Execute handlers
        for handler, event_filter in handlers:
            try:
                if (event_filter is None or event_filter.matches(event)) and handler.should_handle(
                    event
                ):
                    handler.handle_sync(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.name}: {e}", exc_info=True)

    async def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously."""
        # Apply middleware
        for middleware in self._middleware:
            event = middleware(event)
            if event is None:
                return

        # Store in history
        self._add_to_history(event)

        # Get all handlers (sync and async)
        sync_handlers = list(self._sync_handlers.get(event.event_type.value, []))
        sync_handlers.extend(self._sync_handlers.get("*", []))

        async_handlers = list(self._async_handlers.get(event.event_type.value, []))
        async_handlers.extend(self._async_handlers.get("*", []))

        # Create tasks for all handlers
        tasks = []

        # Wrap sync handlers in async
        for handler, event_filter in sync_handlers:
            if (event_filter is None or event_filter.matches(event)) and handler.should_handle(
                event
            ):
                tasks.append(self._run_sync_handler(handler, event))

        # Add async handlers
        for handler, event_filter in async_handlers:
            if (event_filter is None or event_filter.matches(event)) and handler.should_handle(
                event
            ):
                tasks.append(handler.handle_async(event))

        # Execute all handlers concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_sync_handler(self, handler: EventHandler, event: Event) -> None:
        """Run sync handler in thread pool."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, handler.handle_sync, event)

    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size limit."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

    def get_history(
        self,
        event_type: EventType | None = None,
        model_name: str | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Get event history with optional filtering."""
        filtered = self._event_history

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if model_name:
            filtered = [e for e in filtered if e.model_name == model_name]

        return filtered[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus


# Convenience functions
def publish_event(
    event_type: EventType,
    model_name: str | None = None,
    model_id: Any | None = None,
    data: dict[str, Any] | None = None,
    **kwargs,
) -> None:
    """Publish an event to the global event bus."""
    import uuid

    event = Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        model_name=model_name,
        model_id=model_id,
        data=data or {},
        **kwargs,
    )

    _event_bus.publish(event)


async def publish_event_async(
    event_type: EventType,
    model_name: str | None = None,
    model_id: Any | None = None,
    data: dict[str, Any] | None = None,
    **kwargs,
) -> None:
    """Publish an event asynchronously to the global event bus."""
    import uuid

    event = Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        model_name=model_name,
        model_id=model_id,
        data=data or {},
        **kwargs,
    )

    await _event_bus.publish_async(event)


# Built-in event handlers
class LoggingEventHandler(EventHandler):
    """Log events to standard logging."""

    def __init__(self, log_level: int = logging.INFO):
        super().__init__("LoggingEventHandler")
        self.log_level = log_level

    def handle_sync(self, event: Event) -> None:
        """Log the event."""
        logger.log(
            self.log_level,
            f"Event {event.event_type}: {event.model_name}#{event.model_id}",
            extra={"event": event.model_dump()},
        )


class CacheInvalidationHandler(EventHandler):
    """Invalidate cache when models are modified."""

    def should_handle(self, event: Event) -> bool:
        """Only handle modification events."""
        return event.event_type in [
            EventType.MODEL_CREATED,
            EventType.MODEL_UPDATED,
            EventType.MODEL_DELETED,
            EventType.BULK_CREATED,
            EventType.BULK_UPDATED,
            EventType.BULK_DELETED,
        ]

    def handle_sync(self, event: Event) -> None:
        """Invalidate relevant cache entries."""
        from .cache import invalidate_cache

        if event.model_name:
            invalidate_cache(event.model_name)


class WebhookEventHandler(EventHandler):
    """Send events to webhooks."""

    def __init__(self, webhook_url: str, headers: dict[str, str] | None = None):
        super().__init__("WebhookEventHandler")
        self.webhook_url = webhook_url
        self.headers = headers or {}

    async def handle_async(self, event: Event) -> None:
        """Send event to webhook."""
        config = get_config()

        if not config.features.enable_webhooks:
            return

        import aiohttp

        timeout = aiohttp.ClientTimeout(total=config.notifications.webhook_timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(config.notifications.webhook_retry_attempts):
                try:
                    async with session.post(
                        self.webhook_url,
                        json=event.model_dump(),
                        headers=self.headers,
                    ) as response:
                        if response.status < 400:
                            return
                        else:
                            logger.warning(
                                f"Webhook returned status {response.status} for event {event.event_id}"
                            )
                except Exception as e:
                    logger.error(f"Webhook request failed: {e}")

                if attempt < config.notifications.webhook_retry_attempts - 1:
                    await asyncio.sleep(config.notifications.webhook_retry_delay)


# Decorators for automatic event publishing
def publishes_events(
    created: bool = True,
    updated: bool = True,
    deleted: bool = True,
) -> Callable[[type], type]:
    """Class decorator to automatically publish events for model operations."""
    _ = deleted  # Mark as intentionally unused

    def decorator(cls: type) -> type:
        original_init = cls.__init__
        original_setattr = cls.__setattr__

        def new_init(self, *args, **kwargs):
            self._is_new = True
            original_init(self, *args, **kwargs)
            if created and hasattr(self, "id") and self.id is not None:
                publish_event(
                    EventType.MODEL_CREATED,
                    model_name=cls.__name__,
                    model_id=self.id,
                    data={"model": self.model_dump() if hasattr(self, "model_dump") else {}},
                )
            self._is_new = False

        def new_setattr(self, name, value):
            old_value = getattr(self, name, None) if hasattr(self, name) else None
            original_setattr(self, name, value)

            if updated and not getattr(self, "_is_new", True) and old_value != value:
                publish_event(
                    EventType.MODEL_UPDATED,
                    model_name=cls.__name__,
                    model_id=getattr(self, "id", None),
                    data={"field": name, "old_value": old_value, "new_value": value},
                )

        cls.__init__ = new_init
        cls.__setattr__ = new_setattr

        return cls

    return decorator


# Initialize default handlers if configured
def _initialize_default_handlers():
    """Initialize default event handlers based on configuration."""
    config = get_config()

    # Add logging handler
    if config.features.enable_audit_logging:
        _event_bus.subscribe(LoggingEventHandler(), is_async=False)

    # Add cache invalidation handler
    if config.features.enable_caching:
        _event_bus.subscribe(CacheInvalidationHandler(), is_async=False)


# Initialize on import
_initialize_default_handlers()


# Export event system
__all__ = [
    "CacheInvalidationHandler",
    "Event",
    "EventBus",
    "EventFilter",
    "EventHandler",
    "EventType",
    "LoggingEventHandler",
    "WebhookEventHandler",
    "get_event_bus",
    "publish_event",
    "publish_event_async",
    "publishes_events",
]
