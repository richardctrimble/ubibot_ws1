"""Support for UbiBot WS-1 sensors."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
try:
    from homeassistant.helpers.entity import EntityCategory
except ImportError:
    # Fallback for older HA versions
    EntityCategory = None

from .const import DOMAIN
from .coordinator import UbiBotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor definitions matching your YAML configuration
SENSOR_TYPES: dict[str, dict[str, Any]] = {
    "field1": {
        "name": "Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field2": {
        "name": "Humidity", 
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": "%",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field3": {
        "name": "Light",
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "unit": "lx",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field4": {
        "name": "Voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": "V",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field5": {
        "name": "WiFi Signal Strength",
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "unit": "dBm",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field6": {
        "name": "Vibration Index",
        "unit": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field7": {
        "name": "Knock Count",
        "unit": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "traffic_out": {
        "name": "Data Traffic Out",
        "unit": "kB",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "traffic_in": {
        "name": "Data Traffic In", 
        "unit": "kB",
        "state_class": SensorStateClass.MEASUREMENT,
    },
}

# Diagnostic sensor definitions
DIAGNOSTIC_SENSOR_TYPES: dict[str, dict[str, Any]] = {
    "mac_address": {
        "name": "MAC Address",
        "icon": "mdi:network",
        "entity_category": "diagnostic",
    },
    "last_entry_date": {
        "name": "Last Data Update",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "entity_category": "diagnostic",
    },
    "activated_at": {
        "name": "Activation Date",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "entity_category": "diagnostic",
    },
    "firmware": {
        "name": "Firmware Version",
        "icon": "mdi:chip",
        "entity_category": "diagnostic",
    },
    "device_id": {
        "name": "Device ID",
        "icon": "mdi:identifier",
        "entity_category": "diagnostic",
    },
    "serial": {
        "name": "Serial Number",
        "icon": "mdi:barcode",
        "entity_category": "diagnostic",
    },
    "last_ip": {
        "name": "IP Address",
        "icon": "mdi:ip-network",
        "entity_category": "diagnostic",
    },
    "plan_code": {
        "name": "Service Plan",
        "icon": "mdi:account-box",
        "entity_category": "diagnostic",
    },
    "usage": {
        "name": "Total Data Usage",
        "unit": "kB",
        "icon": "mdi:database",
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "entity_category": "diagnostic",
    },
    "last_entry_id": {
        "name": "Entry ID", 
        "icon": "mdi:counter",
        "entity_category": "diagnostic",
    },
    "wifi_ssid": {
        "name": "WiFi Network",
        "icon": "mdi:wifi",
        "entity_category": "diagnostic", 
    },
    "usb_powered": {
        "name": "USB Power",
        "icon": "mdi:usb",
        "entity_category": "diagnostic",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UbiBot sensors based on a config entry."""
    coordinator: UbiBotDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    
    # Add regular sensors
    for sensor_key in SENSOR_TYPES:
        entities.append(UbiBotSensor(coordinator, sensor_key, config_entry, False))
    
    # Add diagnostic sensors  
    for sensor_key in DIAGNOSTIC_SENSOR_TYPES:
        entities.append(UbiBotSensor(coordinator, sensor_key, config_entry, True))

    async_add_entities(entities)


class UbiBotSensor(CoordinatorEntity[UbiBotDataUpdateCoordinator], SensorEntity):
    """Representation of a UbiBot sensor."""

    def __init__(
        self,
        coordinator: UbiBotDataUpdateCoordinator,
        sensor_key: str,
        config_entry: ConfigEntry,
        is_diagnostic: bool = False,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config_entry = config_entry
        self._is_diagnostic = is_diagnostic
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}"
        
        sensor_config = DIAGNOSTIC_SENSOR_TYPES[sensor_key] if is_diagnostic else SENSOR_TYPES[sensor_key]
        self._attr_name = sensor_config['name']
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_state_class = sensor_config.get("state_class")
        self._attr_icon = sensor_config.get("icon")
        
        # Set entity category for diagnostic sensors
        if is_diagnostic and EntityCategory:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        elif is_diagnostic:
            # Fallback for older HA versions
            self._attr_entity_category = "diagnostic"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.channel_id)},
            name=f"UbiBot WS-1 ({self.coordinator.channel_id})",
            manufacturer="UbiBot",
            model="WS-1",
        )

    @property
    def native_value(self) -> float | str | bool | datetime | None:
        """Return the native value of the sensor."""
        if self.coordinator.data:
            value = self.coordinator.data.get(self._sensor_key)
            if value is not None:
                # Handle timestamp sensors - return datetime objects directly
                if self._sensor_key in ["last_entry_date", "activated_at"]:
                    # Return datetime object for timestamp sensors, or None if invalid
                    if isinstance(value, datetime):
                        return value
                    else:
                        return None
                # Handle other string sensors
                elif self._sensor_key in ["mac_address", "firmware", "device_id", "serial", 
                                        "last_ip", "plan_code", "last_entry_id", "wifi_ssid"]:
                    return str(value)
                elif self._sensor_key == "usb_powered":
                    return str(value)  # Convert boolean to string for display
                elif self._sensor_key == "usage":
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None
                else:
                    # Regular numeric sensors
                    try:
                        return round(float(value), 2)
                    except (ValueError, TypeError):
                        return None
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._sensor_key in (
            self.coordinator.data or {}
        )
