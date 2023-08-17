"""Support for tracking ProxyProximity devices."""
from __future__ import annotations

from ProxyProximity_ble import ProxyProximityAdvertisement

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import BaseTrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_HOME, STATE_NOT_HOME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ProxyProximity_DEVICE_NEW
from .coordinator import ProxyProximityCoordinator
from .entity import ProxyProximityEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up device tracker for ProxyProximity Tracker component."""
    coordinator: ProxyProximityCoordinator = hass.data[DOMAIN]

    @callback
    def _async_device_new(
        unique_id: str,
        identifier: str,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Signal a new device."""
        async_add_entities(
            [
                ProxyProximityTrackerEntity(
                    coordinator,
                    identifier,
                    unique_id,
                    ProxyProximity_advertisement,
                )
            ]
        )

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ProxyProximity_DEVICE_NEW, _async_device_new)
    )


class ProxyProximityTrackerEntity(ProxyProximityEntity, BaseTrackerEntity):
    """An ProxyProximity Tracker entity."""

    _attr_name = None

    def __init__(
        self,
        coordinator: ProxyProximityCoordinator,
        identifier: str,
        device_unique_id: str,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Initialize an ProxyProximity tracker entity."""
        super().__init__(
            coordinator, identifier, device_unique_id, ProxyProximity_advertisement
        )
        self._attr_unique_id = device_unique_id
        self._active = True

    @property
    def state(self) -> str:
        """Return the state of the device."""
        return STATE_HOME if self._active else STATE_NOT_HOME

    @property
    def source_type(self) -> SourceType:
        """Return tracker source type."""
        return SourceType.BLUETOOTH_LE

    @property
    def icon(self) -> str:
        """Return device icon."""
        return "mdi:bluetooth-connect" if self._active else "mdi:bluetooth-off"

    @callback
    def _async_seen(
        self,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Update state."""
        self._active = True
        self._ProxyProximity_advertisement = ProxyProximity_advertisement
        self.async_write_ha_state()

    @callback
    def _async_unavailable(self) -> None:
        """Set unavailable."""
        self._active = False
        self.async_write_ha_state()
