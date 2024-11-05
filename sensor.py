import logging
from datetime import timedelta
import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Map field numbers to specific sensor details
SENSOR_TYPES = {
    "field1": {"name": "temperature", "unit": "°C", "device_class": "temperature"},
    "field2": {"name": "humidity", "unit": "%", "device_class": "humidity"},
    "field3": {"name": "light", "unit": "lx", "device_class": "illuminance"},
    "field4": {"name": "voltage", "unit": "V", "device_class": "voltage"},
    "field5": {"name": "wifi_signal", "unit": "dB", "device_class": "signal_strength"},
    "field6": {"name": "vibration", "unit": "count"},
    "field7": {"name": "knocks", "unit": "count"},
    "traffic_out": {"name": "traffic_out", "unit": "kB"},
    "traffic_in": {"name": "traffic_in", "unit": "kB"}
}

class UbiBotSensor(SensorEntity):
    """Representation of a UbiBot sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, sensor_type: str, field: str, device_id: str):
        """Initialize the UbiBot sensor."""
        self.coordinator = coordinator
        self.sensor_type = sensor_type
        self.field = field
        self.device_id = device_id

    @property
    def unique_id(self):
        return f"{self.device_id}_{self.sensor_type}"

    @property
    def state(self):
        # Use field mapping to get the appropriate sensor state
        return self.coordinator.data.get(self.field)

    @property
    def name(self):
        return f"UbiBot {self.sensor_type.capitalize()} Sensor"

    @property
    def unit_of_measurement(self):
        return SENSOR_TYPES[self.field].get("unit")

    @property
    def device_class(self):
        return SENSOR_TYPES[self.field].get("device_class")

    async def async_update(self):
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()


class UbiBotDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the Ubibot API."""

    def __init__(self, hass, entry):
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key = entry.data["api_key"]
        self.device_id = entry.data["device_id"]
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=2))

    async def _async_update_data(self):
        """Fetch data from the Ubibot API."""
        url = f"https://api.ubibot.com/channels/{self.device_id}?account_key={self.api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

            # Access the last values using the correct fields
            last_values = data.get("channel", {}).get("last_values")
            if last_values:
                # Use from_json to parse the embedded JSON
                parsed_values = {key: value["value"] for key, value in last_values.items() if key in SENSOR_TYPES}
                return parsed_values
            else:
                _LOGGER.warning("No data found in 'last_values'")
                return {}

        except aiohttp.ClientError as e:
            _LOGGER.error("Failed to fetch data from Ubibot API: %s", e)
            raise UpdateFailed(f"Error communicating with API: {e}")
