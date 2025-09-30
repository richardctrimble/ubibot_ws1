"""Data coordinator for UbiBot WS-1."""
from __future__ import annotations

import json
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class UbiBotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the UbiBot API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.account_key = entry.data["account_key"]
        self.channel_id = entry.data["channel_id"]
        
        # Get scan interval from options or data, default to 120 seconds (2 minutes)
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL) or entry.data.get(CONF_SCAN_INTERVAL, 2)
        
        super().__init__(
            hass,
            _LOGGER,
            name="UbiBot WS-1",
            update_interval=timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        url = f"https://api.ubibot.com/channels/{self.channel_id}?account_key={self.account_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
            # Parse the last_values JSON string
            channel_data = data.get("channel", {})
            last_values_str = channel_data.get("last_values", "{}")
            
            try:
                last_values = json.loads(last_values_str)
            except json.JSONDecodeError as err:
                _LOGGER.error("Failed to parse last_values JSON: %s", err)
                last_values = {}
            
            # Create unified data structure
            sensor_data = {}
            
            # Add field sensors
            for field_num in range(1, 8):
                field_key = f"field{field_num}"
                if field_key in last_values:
                    sensor_data[field_key] = float(last_values[field_key].get("value", 0))
            
            # Add traffic data
            sensor_data["traffic_out"] = float(channel_data.get("traffic_out", 0))
            sensor_data["traffic_in"] = float(channel_data.get("traffic_in", 0))
            
            # Add diagnostic data
            sensor_data["mac_address"] = channel_data.get("mac_address", "Unknown")
            sensor_data["last_entry_date"] = channel_data.get("last_entry_date", "Unknown")
            sensor_data["activated_at"] = channel_data.get("activated_at", "Unknown")
            sensor_data["firmware"] = channel_data.get("firmware", "Unknown")
            sensor_data["device_id"] = channel_data.get("device_id", "Unknown")
            sensor_data["serial"] = channel_data.get("full_serial", channel_data.get("serial", "Unknown"))
            sensor_data["last_ip"] = channel_data.get("last_ip", "Unknown")
            sensor_data["plan_code"] = channel_data.get("plan_code", "Unknown")
            sensor_data["usage"] = float(channel_data.get("usage", 0))
            sensor_data["last_entry_id"] = channel_data.get("last_entry_id", "Unknown")
            
            # Parse status for additional info
            try:
                status_data = json.loads(channel_data.get("status", "{}"))
                sensor_data["wifi_ssid"] = status_data.get("ssid", "Unknown")
                sensor_data["usb_powered"] = status_data.get("usb", "Unknown") == "1"
            except (json.JSONDecodeError, TypeError):
                sensor_data["wifi_ssid"] = "Unknown"
                sensor_data["usb_powered"] = False
            
            return sensor_data
            
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err