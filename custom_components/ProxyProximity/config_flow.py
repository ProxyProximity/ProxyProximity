import logging

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class BleDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BLE devices."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        if user_input is None:
            # Show the initial form
            return self._show_form()

        # Validate the user input
        errors = self._validate_user_input(user_input)
        if errors:
            return self._show_form(errors=errors)

        # Save the user input as a new config entry
        return self.async_create_entry(
            title=user_input['name'],
            data=user_input
        )

    def _show_form(self, errors=None):
        """Show the config form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                    vol.Required("identity_resolving_key"): cv.string,
                }
            ),
            errors=errors or {},
        )

    def _validate_user_input(self, user_input):
        """Validate the user input."""
        errors = {}

        # TODO: Validate user input here
        if not user_input["identity_resolving_key"]:
            errors["base"] = "identity_resolving_key is required"

        return errors
