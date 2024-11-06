import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_SCAN_INTERVAL
import aiohttp  # Import for API calls

from .const import DOMAIN, VERSION

class UbiBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # Call a function to validate the API key and device ID
                await self._validate_credentials(user_input["account_key"], user_input["channel_id"])
                return self.async_create_entry(title="UbiBot WS-1", data=user_input)
            except aiohttp.ClientError:
                errors["base"] = f"Authentication Connection Failed - v{VERSION}"
            except Exception as ex:
                errors["base"] = f"Authentication Test Failed: {str(ex)} - v{VERSION}"

        data_schema = vol.Schema({
            vol.Required("account_key"): str,
            vol.Required("channel_id"): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=2): int,  # Default to 2 minutes
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _validate_credentials(self, account_key, channel_id):
        """Validates the API key and channel ID by making a test request to the Ubibot API."""
        # Use aiohttp to send a request to the Ubibot API
        url = f"https://api.ubibot.com/channels/{channel_id}?account_key={account_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()  # or handle as needed
                elif response.status == 404:
                    raise Exception("Channel not found. Please check the channel ID.")
                elif response.status == 401:
                    raise Exception("Unauthorized access. Please check your account key.")
                else:
                    raise Exception("Unexpected error occurred.")

    async def async_step_options(self, user_input=None):
      """Manage the options."""
      if user_input is not None:
          return self.async_create_entry(title="", data=user_input)

      current_interval = self.options.get(CONF_SCAN_INTERVAL, 2)

      return self.async_show_form(
          step_id="options",
          data_schema=vol.Schema({
              vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): int,
          })
    )