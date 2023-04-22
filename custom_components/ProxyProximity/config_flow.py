"""Config flow for ProxyProximity integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_DEVICE_TYPE, CONF_DEVICE_NAME, CONF_DEVICE_MAC

DEVICE_TYPES = [
    "Phone",
    "Tablet",
    "Laptop",
    "Smartwatch",
    "Headphones",
]

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_TYPE): vol.In(DEVICE_TYPES),
        vol.Required(CONF_DEVICE_NAME): str,
        vol.Required(CONF_DEVICE_MAC): vol.Match(
            r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
        ),
    }
)


class ProxyProximityFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a ProxyProximity config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if user_input is not None:
            return await self._create_device(user_input)

        return self._show_form()

    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors or {},
        )

    async def _create_device(self, user_input):
        """Create a new device and device entry."""
        device_type = user_input[CONF_DEVICE_TYPE]
        device_name = user_input[CONF_DEVICE_NAME]
        device_mac = user_input[CONF_DEVICE_MAC]

        device_registry = await dr.async_get_registry(self.hass)
        existing_device = device_registry.async_get_device(
            identifiers={(DOMAIN, device_mac)}
        )

        if existing_device:
            return self.async_abort(reason="already_configured")

        # Create the device
        device = {
            "connections": {(dr.CONNECTION_NETWORK_MAC, device_mac)},
            "name": device_name,
            "model": device_type,
            "manufacturer": "Unknown",
        }

        # Create the device in the device registry
        device = device_registry.async_get_or_create(
            config_entry_id=self.context["entry_id"], **device
        )

        # Create the config entry
        entry = self.async_create_entry(
            title=device_name, data=user_input, unique_id=device_mac
        )

        return self.async_abort(reason="success")


async def async_get_or_create_device(hass, device_type, device_name, device_mac):
    """Get or create a device and device entry."""
    device_registry = await dr.async_get_registry(hass)
    existing_device = device_registry.async_get_device(
        identifiers={(DOMAIN, device_mac)}
    )

    if existing_device:
        return existing_device

    # Create the device
    device = {
        "connections": {(dr.CONNECTION_NETWORK_MAC, device_mac)},
        "name": device_name,
        "model": device_type,
        "manufacturer": "Unknown",
    }

    # Create the device in the device registry
    device = device_registry.async_get_or_create(
        config_entry_id=None, **device
    )

    # Return the device
    return device
