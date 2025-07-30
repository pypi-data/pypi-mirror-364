"""Tests for BACnet models."""

import pytest
from pydantic import ValidationError

from aceiot_models.bacnet import (
    DEVICE_ADDRESS_NORMALIZE_MAP,
    BACnetDevice,
    BACnetDeviceBase,
    BACnetDeviceCreate,
    BACnetDeviceReference,
    BACnetDeviceUpdate,
    BACnetPoint,
    BACnetPointBase,
    BACnetPointCreate,
    BACnetPointReference,
    BACnetPointUpdate,
)


@pytest.fixture
def sample_bacnet_device_data(sample_datetime):
    """Sample data for creating a BACnet device."""
    return {
        "client": "test_client",
        "site": "test_site",
        "device_id": 12345,
        "device_address": "192.168.1.100",
        "device_name": "Test Device",
        "device_description": "A test BACnet device",
        "proxy_id": "test.bacnet_proxy",
        "last_seen": sample_datetime,
        "last_scanned": sample_datetime,
    }


@pytest.fixture
def sample_bacnet_device(sample_bacnet_device_data):
    """Sample BACnetDevice instance."""
    return BACnetDevice(**sample_bacnet_device_data)


@pytest.fixture
def sample_bacnet_point_data(sample_bacnet_device, sample_datetime):
    """Sample data for creating a BACnet point."""
    return {
        "name": "test_point",
        "point_type": "bacnet",
        "marker_tags": ["sensor", "temperature"],
        "kv_tags": {"unit": "celsius", "location": "room1"},
        "collect_config": {"interval": 300},
        "object_type": "analogInput",
        "object_index": "1",
        "object_units": "degreesCelsius",
        "object_name": "Temperature Sensor",
        "object_description": "Room temperature sensor",
        "present_value": "23.5",
        "raw_properties": {"reliability": "no-fault-detected"},
        "device": sample_bacnet_device,
        "created": sample_datetime,
        "updated": sample_datetime,
        "collect_enabled": True,
        "collect_interval": 300,
    }


@pytest.fixture
def sample_api_point_data():
    """Sample API response data for a BACnet point."""
    return {
        "name": "test_client/test_site/192.168.1.100-12345/analogInput/1",
        "site": "test_site",
        "client": "test_client",
        "point_type": "bacnet",
        "marker_tags": ["sensor", "temperature"],
        "kv_tags": {"unit": "celsius"},
        "collect_config": {"interval": 300},
        "collect_enabled": True,
        "collect_interval": 300,
        "created": "2024-01-01T00:00:00Z",
        "updated": "2024-01-01T00:00:00Z",
        "bacnet_data": {
            "device_address": "192.168.1.100",
            "device_id": 12345,
            "device_name": "Test Device",
            "device_description": "A test BACnet device",
            "bacnet_proxy": "test.bacnet_proxy",
            "object_type": "analogInput",
            "object_index": 1,
            "object_name": "Temperature Sensor",
            "object_units": "degreesCelsius",
            "object_description": "Room temperature sensor",
            "present_value": "23.5",
            "raw_reliability": "no-fault-detected",
        },
    }


class TestBACnetDeviceBase:
    """Tests for BACnetDeviceBase model."""

    def test_device_base_creation_valid(self, sample_bacnet_device_data):
        """Test creating a valid BACnetDeviceBase."""
        # Remove fields not in base model
        base_data = {
            k: v
            for k, v in sample_bacnet_device_data.items()
            if k not in ["last_seen", "last_scanned", "id", "created", "updated"]
        }

        device = BACnetDeviceBase(**base_data)
        assert device.client == "test_client"
        assert device.site == "test_site"
        assert device.device_id == 12345
        assert device.device_address == "192.168.1.100"
        assert device.device_name == "Test Device"
        assert device.device_description == "A test BACnet device"
        assert device.proxy_id == "test.bacnet_proxy"

    def test_device_base_defaults(self):
        """Test default values in BACnetDeviceBase."""
        device = BACnetDeviceBase(
            client="client",
            site="site",
            device_id=100,
            device_address="10.0.0.1",
            device_name="Device",
        )
        assert device.device_description == ""
        assert device.proxy_id == "platform.bacnet_proxy"

    def test_client_validation(self):
        """Test client field validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="",
                site="site",
                device_id=100,
                device_address="10.0.0.1",
                device_name="Device",
            )

        errors = exc_info.value.errors()
        assert any("client cannot be empty" in error["msg"] for error in errors)

    def test_site_validation(self):
        """Test site field validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="client",
                site="   ",
                device_id=100,
                device_address="10.0.0.1",
                device_name="Device",
            )

        errors = exc_info.value.errors()
        assert any("site cannot be empty" in error["msg"] for error in errors)

    def test_device_id_validation(self):
        """Test device_id range validation."""
        # Valid range: 0-4194303
        # Test minimum
        device = BACnetDeviceBase(
            client="client",
            site="site",
            device_id=0,
            device_address="10.0.0.1",
            device_name="Device",
        )
        assert device.device_id == 0

        # Test maximum
        device = BACnetDeviceBase(
            client="client",
            site="site",
            device_id=4194303,
            device_address="10.0.0.1",
            device_name="Device",
        )
        assert device.device_id == 4194303

        # Test out of range - too low
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="client",
                site="site",
                device_id=-1,
                device_address="10.0.0.1",
                device_name="Device",
            )

        errors = exc_info.value.errors()
        assert any("device_id must be between 0 and 4194303" in error["msg"] for error in errors)

        # Test out of range - too high
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="client",
                site="site",
                device_id=4194304,
                device_address="10.0.0.1",
                device_name="Device",
            )

        errors = exc_info.value.errors()
        assert any("device_id must be between 0 and 4194303" in error["msg"] for error in errors)

    def test_device_address_validation(self):
        """Test device_address validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="client", site="site", device_id=100, device_address="", device_name="Device"
            )

        errors = exc_info.value.errors()
        assert any("device_address cannot be empty" in error["msg"] for error in errors)

    def test_device_name_validation(self):
        """Test device_name validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceBase(
                client="client",
                site="site",
                device_id=100,
                device_address="10.0.0.1",
                device_name="   ",
            )

        errors = exc_info.value.errors()
        assert any("device_name cannot be empty" in error["msg"] for error in errors)


class TestBACnetDevice:
    """Tests for BACnetDevice model."""

    def test_device_creation_valid(self, sample_bacnet_device_data):
        """Test creating a valid BACnetDevice."""
        device = BACnetDevice(**sample_bacnet_device_data)
        assert device.client == "test_client"
        assert device.site == "test_site"
        assert device.device_id == 12345
        assert device.last_seen == sample_bacnet_device_data["last_seen"]
        assert device.last_scanned == sample_bacnet_device_data["last_scanned"]

    def test_device_optional_fields(self):
        """Test BACnetDevice with optional fields."""
        device = BACnetDevice(
            client="client",
            site="site",
            device_id=100,
            device_address="10.0.0.1",
            device_name="Device",
        )
        assert device.last_seen is None
        assert device.last_scanned is None

    def test_normalize_address(self):
        """Test address normalization."""
        # Test underscore replacement
        device = BACnetDevice(
            client="client",
            site="site",
            device_id=100,
            device_address="10_0_0_1",
            device_name="Device",
        )
        assert device.normalize_address() == "10.0.0.1-100"

        # Test comma removal
        device.device_address = "10,0,0,1"
        assert device.normalize_address() == "10001-100"

        # Test space replacement
        device.device_address = "10 0 0 1"
        assert device.normalize_address() == "10.0.0.1-100"

        # Test combined
        device.device_address = "10_0,0 1"
        assert device.normalize_address() == "10.00.1-100"

    def test_serialize_device_path(self, sample_bacnet_device):
        """Test device path serialization."""
        path = sample_bacnet_device.serialize_device_path()
        assert path == "test_client/test_site/192.168.1.100-12345"

    def test_from_api_point(self, sample_api_point_data):
        """Test creating BACnetDevice from API point data."""
        device = BACnetDevice.from_api_point(sample_api_point_data)
        assert device.client == "test_client"
        assert device.site == "test_site"
        assert device.device_id == 12345
        assert device.device_address == "192.168.1.100"
        assert device.device_name == "Test Device"
        assert device.proxy_id == "test.bacnet_proxy"
        assert device.last_seen is None
        assert device.last_scanned is None

    def test_to_dict(self, sample_bacnet_device):
        """Test converting BACnetDevice to dictionary."""
        data = sample_bacnet_device.to_dict()

        assert data["client"] == "test_client"
        assert data["site"] == "test_site"
        assert data["device_id"] == 12345
        assert data["device_address"] == "192.168.1.100"
        assert data["device_name"] == "Test Device"
        assert data["device_description"] == "A test BACnet device"
        assert data["proxy_id"] == "test.bacnet_proxy"
        assert data["last_seen"].endswith("Z")
        assert data["last_scanned"].endswith("Z")

    def test_to_dict_none_timestamps(self):
        """Test to_dict with None timestamps."""
        device = BACnetDevice(
            client="client",
            site="site",
            device_id=100,
            device_address="10.0.0.1",
            device_name="Device",
        )
        data = device.to_dict()
        assert data["last_seen"] is None
        assert data["last_scanned"] is None


class TestBACnetDeviceCreate:
    """Tests for BACnetDeviceCreate model."""

    def test_device_create_valid(self, sample_bacnet_device_data):
        """Test creating a valid BACnetDeviceCreate."""
        # Remove entity fields
        create_data = {
            k: v
            for k, v in sample_bacnet_device_data.items()
            if k not in ["id", "created", "updated"]
        }

        device = BACnetDeviceCreate(**create_data)
        assert device.client == "test_client"
        assert device.last_seen == sample_bacnet_device_data["last_seen"]


class TestBACnetDeviceUpdate:
    """Tests for BACnetDeviceUpdate model."""

    def test_device_update_all_fields(self, sample_bacnet_device_data):
        """Test updating all fields."""
        update = BACnetDeviceUpdate(**sample_bacnet_device_data)
        assert update.client == "test_client"
        assert update.device_id == 12345

    def test_device_update_optional_fields(self):
        """Test that all fields are optional."""
        update = BACnetDeviceUpdate()
        assert update.client is None
        assert update.site is None
        assert update.device_id is None
        assert update.device_address is None
        assert update.device_name is None
        assert update.device_description is None
        assert update.proxy_id is None
        assert update.last_seen is None
        assert update.last_scanned is None

    def test_device_update_validation(self):
        """Test validation applies to provided fields."""
        # Empty client
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceUpdate(client="")

        errors = exc_info.value.errors()
        assert any("client cannot be empty" in error["msg"] for error in errors)

        # Invalid device_id
        with pytest.raises(ValidationError) as exc_info:
            BACnetDeviceUpdate(device_id=-1)

        errors = exc_info.value.errors()
        assert any("device_id must be between 0 and 4194303" in error["msg"] for error in errors)


class TestBACnetDeviceReference:
    """Tests for BACnetDeviceReference model."""

    def test_device_reference_creation(self):
        """Test creating a BACnetDeviceReference."""
        ref = BACnetDeviceReference(id=1, device_name="Test Device", device_id=12345)
        assert ref.id == 1
        assert ref.device_name == "Test Device"
        assert ref.device_id == 12345


class TestBACnetPointBase:
    """Tests for BACnetPointBase model."""

    def test_point_base_creation_valid(self, sample_bacnet_point_data):
        """Test creating a valid BACnetPointBase."""
        # Remove fields not in base model
        base_data = {
            k: v
            for k, v in sample_bacnet_point_data.items()
            if k not in ["device", "id", "created", "updated"]
        }

        point = BACnetPointBase(**base_data)
        assert point.name == "test_point"
        assert point.point_type == "bacnet"
        assert point.marker_tags == ["sensor", "temperature"]
        assert point.kv_tags == {"unit": "celsius", "location": "room1"}
        assert point.object_type == "analogInput"
        assert point.object_index == "1"
        assert point.collect_enabled is True
        assert point.collect_interval == 300

    def test_point_base_defaults(self):
        """Test default values in BACnetPointBase."""
        point = BACnetPointBase(
            name="point",
            object_type="analogInput",
            object_index="1",
            object_name="Object",
            present_value="0",
        )
        assert point.point_type == "bacnet"
        assert point.marker_tags == []
        assert point.kv_tags == {}
        assert point.collect_config == {}
        assert point.object_units is None
        assert point.object_description == ""
        assert point.raw_properties == {}
        assert point.collect_enabled is False
        assert point.collect_interval == 300

    def test_name_validation(self):
        """Test name field validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointBase(
                name="",
                object_type="analogInput",
                object_index="1",
                object_name="Object",
                present_value="0",
            )

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)

    def test_object_type_validation(self):
        """Test object_type validation."""
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointBase(
                name="point",
                object_type="   ",
                object_index="1",
                object_name="Object",
                present_value="0",
            )

        errors = exc_info.value.errors()
        assert any("object_type cannot be empty" in error["msg"] for error in errors)

    def test_collect_interval_validation(self):
        """Test collect_interval validation."""
        # Valid positive value
        point = BACnetPointBase(
            name="point",
            object_type="analogInput",
            object_index="1",
            object_name="Object",
            present_value="0",
            collect_interval=60,
        )
        assert point.collect_interval == 60

        # Invalid zero value
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointBase(
                name="point",
                object_type="analogInput",
                object_index="1",
                object_name="Object",
                present_value="0",
                collect_interval=0,
            )

        errors = exc_info.value.errors()
        assert any("collect_interval must be positive" in error["msg"] for error in errors)

        # Invalid negative value
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointBase(
                name="point",
                object_type="analogInput",
                object_index="1",
                object_name="Object",
                present_value="0",
                collect_interval=-1,
            )

        errors = exc_info.value.errors()
        assert any("collect_interval must be positive" in error["msg"] for error in errors)


class TestBACnetPoint:
    """Tests for BACnetPoint model."""

    def test_point_creation_valid(self, sample_bacnet_point_data):
        """Test creating a valid BACnetPoint."""
        point = BACnetPoint(**sample_bacnet_point_data)
        assert point.name == "test_point"
        assert point.device.client == "test_client"
        assert point.object_type == "analogInput"
        assert point.present_value == "23.5"

    def test_serialize_point_name(self, sample_bacnet_point_data):
        """Test point name serialization."""
        point = BACnetPoint(**sample_bacnet_point_data)
        name = point.serialize_point_name()
        assert name == "test_client/test_site/192.168.1.100-12345/analogInput/1"

    def test_api_format(self, sample_bacnet_point_data):
        """Test formatting point for API."""
        point = BACnetPoint(**sample_bacnet_point_data)
        api_data = point.api_format()

        assert api_data["name"] == "test_client/test_site/192.168.1.100-12345/analogInput/1"
        assert api_data["site"] == "test_site"
        assert api_data["client"] == "test_client"
        assert api_data["point_type"] == "bacnet"
        assert api_data["collect_enabled"] is True
        assert api_data["collect_interval"] == 300

        # Check bacnet_data
        bacnet_data = api_data["bacnet_data"]
        assert bacnet_data["device_address"] == "192.168.1.100"
        assert bacnet_data["device_id"] == 12345
        assert bacnet_data["object_type"] == "analogInput"
        assert bacnet_data["object_index"] == 1  # Converted to int
        assert bacnet_data["object_name"] == "Temperature Sensor"
        assert bacnet_data["present_value"] == "23.5"

    def test_from_api_model(self, sample_api_point_data):
        """Test creating BACnetPoint from API data."""
        point = BACnetPoint.from_api_model(sample_api_point_data)

        assert point.name == sample_api_point_data["name"]
        assert point.point_type == "bacnet"
        assert point.object_type == "analogInput"
        assert point.object_index == "1"
        assert point.present_value == "23.5"
        assert point.raw_properties == {"reliability": "no-fault-detected"}

        # Check device
        assert point.device.client == "test_client"
        assert point.device.site == "test_site"
        assert point.device.device_id == 12345

    def test_to_dict(self, sample_bacnet_point_data):
        """Test converting BACnetPoint to dictionary."""
        point = BACnetPoint(**sample_bacnet_point_data)
        data = point.to_dict()

        assert data["name"] == "test_point"
        assert data["point_type"] == "bacnet"
        assert data["object_type"] == "analogInput"
        assert data["present_value"] == "23.5"
        assert data["collect_enabled"] is True
        assert data["created"].endswith("Z")
        assert data["updated"].endswith("Z")

        # Check nested device
        assert data["device"]["client"] == "test_client"
        assert data["device"]["device_id"] == 12345


class TestBACnetPointCreate:
    """Tests for BACnetPointCreate model."""

    def test_point_create_valid(self, sample_bacnet_point_data):
        """Test creating a valid BACnetPointCreate."""
        # Use device_id instead of device object
        create_data = {
            k: v
            for k, v in sample_bacnet_point_data.items()
            if k not in ["device", "id", "created", "updated"]
        }
        create_data["device_id"] = 1

        point = BACnetPointCreate(**create_data)
        assert point.name == "test_point"
        assert point.device_id == 1


class TestBACnetPointUpdate:
    """Tests for BACnetPointUpdate model."""

    def test_point_update_all_fields(self):
        """Test updating all fields."""
        update = BACnetPointUpdate(
            name="new_name",
            marker_tags=["new_tag"],
            kv_tags={"new": "tag"},
            collect_config={"new": "config"},
            object_units="newUnits",
            object_description="New description",
            present_value="100",
            raw_properties={"new": "property"},
            collect_enabled=False,
            collect_interval=600,
        )
        assert update.name == "new_name"
        assert update.collect_interval == 600

    def test_point_update_optional_fields(self):
        """Test that all fields are optional."""
        update = BACnetPointUpdate()
        assert update.name is None
        assert update.marker_tags is None
        assert update.kv_tags is None
        assert update.collect_config is None
        assert update.object_units is None
        assert update.object_description is None
        assert update.present_value is None
        assert update.raw_properties is None
        assert update.collect_enabled is None
        assert update.collect_interval is None

    def test_point_update_validation(self):
        """Test validation applies to provided fields."""
        # Empty name
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointUpdate(name="")

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)

        # Invalid collect_interval
        with pytest.raises(ValidationError) as exc_info:
            BACnetPointUpdate(collect_interval=0)

        errors = exc_info.value.errors()
        assert any("collect_interval must be positive" in error["msg"] for error in errors)


class TestBACnetPointReference:
    """Tests for BACnetPointReference model."""

    def test_point_reference_creation(self):
        """Test creating a BACnetPointReference."""
        ref = BACnetPointReference(id=1, name="test_point", object_name="Temperature Sensor")
        assert ref.id == 1
        assert ref.name == "test_point"
        assert ref.object_name == "Temperature Sensor"


class TestUtilityConstants:
    """Tests for utility constants."""

    def test_device_address_normalize_map(self):
        """Test the device address normalization map."""
        # Test underscore to dot
        assert "test_address".translate(DEVICE_ADDRESS_NORMALIZE_MAP) == "test.address"

        # Test comma removal
        assert "test,address".translate(DEVICE_ADDRESS_NORMALIZE_MAP) == "testaddress"

        # Test space to dot
        assert "test address".translate(DEVICE_ADDRESS_NORMALIZE_MAP) == "test.address"

        # Test combined
        assert "test_addr,ess 123".translate(DEVICE_ADDRESS_NORMALIZE_MAP) == "test.address.123"
