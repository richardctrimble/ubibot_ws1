import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
import aiohttp  # Import for API calls
import asyncio

class UbiBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # Call a function to validate the API key and device ID
                await self._validate_credentials(user_input["api_key"], user_input["device_id"])
                return self.async_create_entry(title="UbiBot WS-1", data=user_input)
            except aiohttp.ClientError:
                errors["base"] = "Authication Connection Failed"
            except Exception:
                errors["base"] = "Authication Test Failed"

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("device_id"): str
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _validate_credentials(self, api_key, device_id):
        """Validates the API key and device ID by making a test request to the Ubibot API."""
        # Use aiohttp to send a request to the Ubibot API
        url = f"https://api.ubibot.com/channels/{device_id}?account_key={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception("Invalid API key or device ID")
