"""The ProxyProximity tracker integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry, async_get

from .const import DOMAIN, PLATFORMS
from .coordinator import ProxyProximityCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetooth LE Tracker from a config entry."""
    coordinator = hass.data[DOMAIN] = ProxyProximityCoordinator(hass, entry, async_get(hass))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await coordinator.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.pop(DOMAIN)
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove ProxyProximity config entry from a device."""
    coordinator: ProxyProximityCoordinator = hass.data[DOMAIN]
    return not any(
        identifier
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN and coordinator.async_device_id_seen(identifier[1])
    )
