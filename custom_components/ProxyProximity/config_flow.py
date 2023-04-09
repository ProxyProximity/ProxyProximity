import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, KNOWN_DEVICES, DEVICE_TRACKERS, CONF_DEVICES, CONF_PROXIES, DEFAULT_NAME

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [cv.string]),
        vol.Required(CONF_PROXIES): vol.All(cv.ensure_list, [cv.string]),
    }
)

async def validate_devices(hass, devices):
    known_devices = {}
    device_registry = await hass.helpers.device_registry.async_get_registry()
    for device in devices:
        known_device = KNOWN_DEVICES.get(device)
        if known_device:
            known_devices[device] = known_device
            continue
        if len(device) != 17:
            return None
        if device in KNOWN_DEVICES.values():
            return None
        if device_registry.async_get_device({("mac", device)}, set()) is None:
            return None
        known_devices[device] = None
    return known_devices

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ProxyProximity."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            devices = user_input[CONF_DEVICES]
            proxies = user_input[CONF_PROXIES]

            known_devices = await validate_devices(self.hass, devices)
            if known_devices is None:
                errors["base"] = "invalid_devices"
            else:
                self.context["data"] = {
                    CONF_DEVICES: known_devices,
                    CONF_PROXIES: proxies,
                }
                return self.async_create_entry(title=DEFAULT_NAME, data=self.context["data"])

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_config):
        """Handle import from config file."""
        if not import_config:
            return await self.async_step_user()

        devices = import_config.get(CONF_DEVICES, [])
        proxies = import_config.get(CONF_PROXIES, [])

        known_devices = await validate_devices(self.hass, devices)
        if known_devices is None:
            return self.async_abort(reason="invalid_devices")

        return self.async_create_entry(
            title=DEFAULT_NAME,
            data={
                CONF_DEVICES: known_devices,
                CONF_PROXIES: proxies,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option flow for ProxyProximity."""

    def __init__(self, config_entry):
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        known_devices = self.config_entry.data.get(CONF_DEVICES, {})
        device_trackers = self.hass.data.get(DEVICE_TRACKERS, {})
        devices = []
        for mac_address, device in known_devices.items():
            if mac_address in device_trackers:
                devices.append(
                    {
                        "mac": mac_address,
                        "name": device.get("name") if device else "",
                        "
