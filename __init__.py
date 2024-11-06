import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration via YAML, if needed."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Ubibot integration from a config entry."""
    _LOGGER.debug("Initializing UbiBot integration for entry ID: %s", entry.entry_id)

    # Initialize the coordinator
    coordinator = UbiBotDataUpdateCoordinator(hass, entry)

    # Attempt first data fetch
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("Successfully fetched initial data for UbiBot")
    except Exception as e:
        _LOGGER.error("Failed to initialize Ubibot API: %s", e)
        raise ConfigEntryNotReady from e

    # Store the coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up platforms
    _LOGGER.debug("Setting up sensor platform for UbiBot")
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Add reload listener
    entry.add_update_listener(async_reload_entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry ID: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the config entry."""
    _LOGGER.debug("Reloading entry ID: %s", entry.entry_id)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

class UbiBotDataUpdateCoordinator(DataUpdateCoordinator):
    """Custom coordinator to manage fetching data from the Ubibot API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),  # Adjust as needed
        )
        self.account_key = entry.data["account_key"]
        self.channel_id = entry.data["channel_id"]
        _LOGGER.debug("UbiBotDataUpdateCoordinator initialized with update interval: %s", self.update_interval)

    async def _async_update_data(self):
        """Fetch data from Ubibot API."""
        _LOGGER.debug("Fetching data from UbiBot API for channel ID: %s", self.channel_id)

        try:
            data = await self._fetch_data()
            _LOGGER.debug("Fetched data: %s", data)
            return data
        except Exception as e:
            _LOGGER.error("Error fetching data from Ubibot: %s", e)
            raise UpdateFailed(f"Error fetching data: {e}")

    async def _fetch_data(self):
        """Perform the API call to fetch data."""
        import aiohttp
        
        url = f"https://api.ubibot.com/channels/{self.channel_id}?account_key={self.account_key}"
        _LOGGER.debug("API request URL: %s", url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()
