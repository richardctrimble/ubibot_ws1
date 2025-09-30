"""Support for UbiBot WS-1 sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfInformation,
    UnitOfSignalStrength,
    UnitOfTemperature,
    UnitOfIlluminance,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UbiBotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor definitions matching your YAML configuration
SENSOR_TYPES: dict[str, dict[str, Any]] = {
    "field1": {
        "name": "Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field2": {
        "name": "Humidity", 
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field3": {
        "name": "Light",
        "device_class": SensorDeviceClass.ILLUMINANCE,
        "unit": UnitOfIlluminance.LUX,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field4": {
        "name": "Voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": UnitOfElectricPotential.VOLT,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field5": {
        "name": "WiFi Signal",
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "unit": UnitOfSignalStrength.DECIBEL,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field6": {
        "name": "Vibration",
        "unit": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "field7": {
        "name": "Knocks",
        "unit": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "traffic_out": {
        "name": "Traffic Out",
        "unit": UnitOfInformation.KILOBYTES,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "traffic_in": {
        "name": "Traffic In", 
        "unit": UnitOfInformation.KILOBYTES,
        "state_class": SensorStateClass.MEASUREMENT,
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
    for sensor_key in SENSOR_TYPES:
        entities.append(UbiBotSensor(coordinator, sensor_key, config_entry))

    async_add_entities(entities)


class UbiBotSensor(CoordinatorEntity[UbiBotDataUpdateCoordinator], SensorEntity):
    """Representation of a UbiBot sensor."""

    def __init__(
        self,
        coordinator: UbiBotDataUpdateCoordinator,
        sensor_key: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}"
        
        sensor_config = SENSOR_TYPES[sensor_key]
        self._attr_name = f"UbiBot {sensor_config['name']}"
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_state_class = sensor_config.get("state_class")

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
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        if self.coordinator.data:
            value = self.coordinator.data.get(self._sensor_key)
            if value is not None:
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
