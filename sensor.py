import logging
from datetime import timedelta
import aiohttp
import json
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN
from homeassistant.const import CONF_SCAN_INTERVAL

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

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    """Set up the UbiBot sensors from a config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if not coordinator:
        _LOGGER.error("Coordinator not found")
        return
    # Create a sensor entity for each field type defined in SENSOR_TYPES
    sensors = []
    for field in SENSOR_TYPES.keys():
        _LOGGER.debug("Adding sensor for field: %s", field)
        sensors.append(UbiBotSensor(coordinator, field))
    _LOGGER.debug("Sensor Adding Complete")
    # Add the sensors to Home Assistant
    async_add_entities(sensors, True)

class UbiBotSensor(SensorEntity):
    """Representation of a UbiBot sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, field: str):
        """Initialize the UbiBot sensor."""
        self.coordinator = coordinator
        self.field = field

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self.coordinator.channel_id}_{self.field}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"UbiBot {SENSOR_TYPES[self.field]['name'].capitalize()} Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.field)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self.field].get("unit")

    @property
    def device_class(self):
        """Return the device class of this sensor."""
        return SENSOR_TYPES[self.field].get("device_class")

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.channel_id)},  # Use a tuple to define the identifier
            "name": f"UbiBot Device {self.coordinator.channel_id}",  # Device name
            "model": "UbiBot WS-1",  # Replace with actual model name
            "manufacturer": "UbiBot",  # Manufacturer name
        }

    async def async_update(self):
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()

class UbiBotDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the Ubibot API."""
    def __init__(self, hass, entry):
        """Initialize the coordinator."""
        self.account_key = entry.data["account_key"]
        self.channel_id = entry.data["channel_id"]
        # Retrieve custom interval from configuration
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 2)  # Defaults to 2 minutes if not set
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval)
        )
        _LOGGER.debug("Coordinator initialized with channel ID: %s and scan interval: %d minutes", self.channel_id, scan_interval) 

    async def _async_update_data(self):
        _LOGGER.debug("Called Sensor Update Data")
        """Fetch data from the Ubibot API."""
        url = f"https://api.ubibot.com/channels/{self.channel_id}?account_key={self.account_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    _LOGGER.debug("Response status: %s", response.status)
                    response.raise_for_status()  # Raises error for 4xx/5xx status
                    data = await response.json()
                    _LOGGER.debug("Full JSON response: %s", data)

            # Check if 'last_values' is present and is a JSON string
            last_values_str = data.get("channel", {}).get("last_values")
            if not last_values_str:
                _LOGGER.warning("No 'last_values' found in response")
                return {}

            # Attempt to parse the 'last_values' JSON
            try:
                last_values = json.loads(last_values_str)
                _LOGGER.debug("Parsed 'last_values': %s", last_values)
            except json.JSONDecodeError as e:
                _LOGGER.error("JSON decoding error: %s", e)
                return {}

            # Only include values that are defined in SENSOR_TYPES
            parsed_values = {key: value["value"] for key, value in last_values.items() if key in SENSOR_TYPES}
            _LOGGER.debug("Final parsed sensor values: %s", parsed_values)
            return parsed_values

        except aiohttp.ClientError as e:
            _LOGGER.error("Network error while fetching data: %s", e)
            raise UpdateFailed(f"Error communicating with Ubibot API: {e}")
        except Exception as e:
            _LOGGER.error("Unexpected error in data fetch: %s", e)
            raise UpdateFailed(f"Unexpected error: {e}")
