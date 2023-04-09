"""Config flow for Proxy Proximity."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .helpers import check_configuration

_LOGGER = logging.getLogger(__name__)

class ProxyProximityFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Proxy Proximity."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            config_valid, error_msg = await check_configuration(self.hass, user_input)

            if config_valid:
                return self.async_create_entry(
                    title="Proxy Proximity",
                    data=user_input
                )
            else:
                errors["base"] = error_msg

        # Show the configuration form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("url"): str,
                vol.Optional("username"): str,
                vol.Optional("password"): str,
            }),
            errors=errors
        )

    async def async_step_import(self, user_input):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)

    async def async_step_zeroconf(self, discovery_info):
        """Handle zeroconf discovery."""
        return await self.async_step_user({
            "url": f"http://{discovery_info['host']}:{discovery_info['port']}"
        })
