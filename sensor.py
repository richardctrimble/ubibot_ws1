import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

SENSOR_TYPES = ["temperature", "humidity", "light", "voltage", "wifi_rssi", "knocks"]

class UbiBotSensor(SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, sensor_type: str, device_id: str):
        self.coordinator = coordinator
        self.sensor_type = sensor_type
        self.device_id = device_id

    @property
    def unique_id(self):
        return f"{self.device_id}_{self.sensor_type}"

    @property
    def state(self):
        return self.coordinator.data[self.sensor_type]

    @property
    def name(self):
        return f"UbiBot {self.sensor_type.capitalize()} Sensor"

    @property
    def unit_of_measurement(self):
        if self.sensor_type == "temperature":
            return "°C"
        elif self.sensor_type == "humidity":
            return "%"
        elif self.sensor_type == "light":
            return "lux"
        elif self.sensor_type == "voltage":
            return "V"
        elif self.sensor_type == "wifi_rssi":
            return "dBm"
        elif self.sensor_type == "knocks":
            return "count"

    async def async_update(self):
        self.coordinator.async_update()

class UbiBotDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.entry = entry
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5))

    async def _async_update_data(self):
        response = requests.get(f"https://api.ubibot.io/v1.0/devices/{self.entry.data['device_id']}/data", headers={"X-Authorization": self.entry.data["api_key"]})
        data = response.json()
        return {
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "light": data["light"],
            "voltage": data["voltage"],
            "wifi_rssi": data["wifi_rssi"],
            "knocks": data["knocks"]
        }
