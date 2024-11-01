import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

class UbiBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # Validate the API key and device ID here
                return self.async_create_entry(title="UbiBot WS-1", data=user_input)
            except Exception:
                errors["base"] = "auth_failed"

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("device_id"): str
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
