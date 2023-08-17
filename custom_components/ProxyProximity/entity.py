"""Support for ProxyProximity device sensors."""
from __future__ import annotations

from abc import abstractmethod

from ProxyProximity_ble import ProxyProximityAdvertisement

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import ATTR_MAJOR, ATTR_MINOR, ATTR_SOURCE, ATTR_UUID, DOMAIN
from .coordinator import ProxyProximityCoordinator, signal_seen, signal_unavailable


class ProxyProximityEntity(Entity):
    """An ProxyProximity entity."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ProxyProximityCoordinator,
        identifier: str,
        device_unique_id: str,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Initialize an ProxyProximity sensor entity."""
        self._device_unique_id = device_unique_id
        self._coordinator = coordinator
        self._ProxyProximity_advertisement = ProxyProximity_advertisement
        self._attr_device_info = DeviceInfo(
            name=identifier,
            identifiers={(DOMAIN, device_unique_id)},
        )

    @property
    def extra_state_attributes(
        self,
    ) -> dict[str, str | int]:
        """Return the device state attributes."""
        ProxyProximity_advertisement = self._ProxyProximity_advertisement
        return {
            ATTR_UUID: str(ProxyProximity_advertisement.uuid),
            ATTR_MAJOR: ProxyProximity_advertisement.major,
            ATTR_MINOR: ProxyProximity_advertisement.minor,
            ATTR_SOURCE: ProxyProximity_advertisement.source,
        }

    @abstractmethod
    @callback
    def _async_seen(
        self,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Update state."""

    @abstractmethod
    @callback
    def _async_unavailable(self) -> None:
        """Set unavailable."""

    async def async_added_to_hass(self) -> None:
        """Register state update callbacks."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_seen(self._device_unique_id),
                self._async_seen,
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_unavailable(self._device_unique_id),
                self._async_unavailable,
            )
        )
