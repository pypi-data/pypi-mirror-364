"""ACE IoT Models - Pydantic models for ACE IoT API data structures."""

__version__ = "0.1.0"

# Import new architecture components for easy access
from . import cache, config, events, model_factory, validators

# BACnet models
from .bacnet import (
    BACnetDevice,
    BACnetDeviceBase,
    BACnetDeviceCreate,
    BACnetDeviceReference,
    BACnetDeviceResponse,
    BACnetDeviceUpdate,
    BACnetPoint,
    BACnetPointBase,
    BACnetPointCreate,
    BACnetPointReference,
    BACnetPointResponse,
    BACnetPointUpdate,
)

# Common models
# Client models
from .clients import (
    Client,
    ClientCreate,
    ClientList,
    ClientPaginatedResponse,
    ClientReference,
    ClientResponse,
    ClientUpdate,
)
from .common import (
    AuthToken,
    BaseEntityModel,
    BaseModel,
    BaseUUIDEntityModel,
    ErrorResponse,
    FileMetadata,
    IPAddressModel,
    MessageResponse,
    PaginatedResponse,
)

# DER Event models
from .der_events import (
    DerEvent,
    DerEventCreate,
    DerEventList,
    DerEventPaginatedResponse,
    DerEventResponse,
    DerEventUpdate,
)

# Gateway models
from .gateways import (
    Gateway,
    GatewayCreate,
    GatewayIdentity,
    GatewayList,
    GatewayPaginatedResponse,
    GatewayReference,
    GatewayResponse,
    GatewayUpdate,
)

# Hawke models
from .hawke import (
    HawkeConfig,
    HawkeConfigCreate,
    HawkeConfigResponse,
)

# Point models
from .points import (
    BACnetData,
    Point,
    PointCreate,
    PointList,
    PointPaginatedResponse,
    PointReference,
    PointResponse,
    PointUpdate,
)

# Sample models
from .sample import (
    Sample,
    SampleBase,
    SampleCreate,
    SampleList,
    SampleResponse,
    SampleUpdate,
)

# Site models
from .sites import (
    Site,
    SiteCreate,
    SiteList,
    SitePaginatedResponse,
    SiteReference,
    SiteResponse,
    SiteUpdate,
)

# Timeseries models
from .timeseries import (
    PointSample,
    TimeseriesData,
    WeatherData,
)

# User models
from .users import (
    AceRole,
    ClientUser,
    Role,
    User,
    UserCreate,
    UserResponse,
    UserUpdate,
)

# Volttron models
from .volttron import (
    AgentConfig,
    AgentConfigCreate,
    VolttronAgent,
    VolttronAgentCreate,
    VolttronAgentPackage,
    VolttronAgentResponse,
    VolttronAgentUpdate,
)


__all__ = [
    "AceRole",
    "AgentConfig",
    "AgentConfigCreate",
    "AuthToken",
    "BACnetData",
    "BACnetDevice",
    "BACnetDeviceBase",
    "BACnetDeviceCreate",
    "BACnetDeviceReference",
    "BACnetDeviceResponse",
    "BACnetDeviceUpdate",
    "BACnetPoint",
    "BACnetPointBase",
    "BACnetPointCreate",
    "BACnetPointReference",
    "BACnetPointResponse",
    "BACnetPointUpdate",
    "BaseEntityModel",
    "BaseModel",
    "BaseUUIDEntityModel",
    "Client",
    "ClientCreate",
    "ClientList",
    "ClientPaginatedResponse",
    "ClientReference",
    "ClientResponse",
    "ClientUpdate",
    "ClientUser",
    "DerEvent",
    "DerEventCreate",
    "DerEventList",
    "DerEventPaginatedResponse",
    "DerEventResponse",
    "DerEventUpdate",
    "ErrorResponse",
    "FileMetadata",
    "Gateway",
    "GatewayCreate",
    "GatewayIdentity",
    "GatewayList",
    "GatewayPaginatedResponse",
    "GatewayReference",
    "GatewayResponse",
    "GatewayUpdate",
    "HawkeConfig",
    "HawkeConfigCreate",
    "HawkeConfigResponse",
    "IPAddressModel",
    "MessageResponse",
    "PaginatedResponse",
    "Point",
    "PointCreate",
    "PointList",
    "PointPaginatedResponse",
    "PointReference",
    "PointResponse",
    "PointSample",
    "PointUpdate",
    "Role",
    "Sample",
    "SampleBase",
    "SampleCreate",
    "SampleList",
    "SampleResponse",
    "SampleUpdate",
    "Site",
    "SiteCreate",
    "SiteList",
    "SitePaginatedResponse",
    "SiteReference",
    "SiteResponse",
    "SiteUpdate",
    "TimeseriesData",
    "User",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "VolttronAgent",
    "VolttronAgentCreate",
    "VolttronAgentPackage",
    "VolttronAgentResponse",
    "VolttronAgentUpdate",
    "WeatherData",
]
