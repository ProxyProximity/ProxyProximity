"""Support for ProxyProximity device sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ProxyProximity_ble import ProxyProximityAdvertisement

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ProxyProximity_DEVICE_NEW
from .coordinator import ProxyProximityCoordinator
from .entity import ProxyProximityEntity


@dataclass
class ProxyProximityRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[ProxyProximityAdvertisement], str | int | None]


@dataclass
class ProxyProximitySensorEntityDescription(SensorEntityDescription, ProxyProximityRequiredKeysMixin):
    """Describes ProxyProximity sensor entity."""


SENSOR_DESCRIPTIONS = (
    ProxyProximitySensorEntityDescription(
        key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_registry_enabled_default=False,
        value_fn=lambda ProxyProximity_advertisement: ProxyProximity_advertisement.rssi,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxyProximitySensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_registry_enabled_default=False,
        value_fn=lambda ProxyProximity_advertisement: ProxyProximity_advertisement.power,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ProxyProximitySensorEntityDescription(
        key="estimated_distance",
        translation_key="estimated_distance",
        icon="mdi:signal-distance-variant",
        native_unit_of_measurement=UnitOfLength.METERS,
        value_fn=lambda ProxyProximity_advertisement: ProxyProximity_advertisement.distance,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    ProxyProximitySensorEntityDescription(
        key="vendor",
        translation_key="vendor",
        entity_registry_enabled_default=False,
        value_fn=lambda ProxyProximity_advertisement: ProxyProximity_advertisement.vendor,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for ProxyProximity Tracker component."""
    coordinator: ProxyProximityCoordinator = hass.data[DOMAIN]

    @callback
    def _async_device_new(
        unique_id: str,
        identifier: str,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Signal a new device."""
        async_add_entities(
            ProxyProximitySensorEntity(
                coordinator,
                description,
                identifier,
                unique_id,
                ProxyProximity_advertisement,
            )
            for description in SENSOR_DESCRIPTIONS
        )

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_ProxyProximity_DEVICE_NEW, _async_device_new)
    )


class ProxyProximitySensorEntity(ProxyProximityEntity, SensorEntity):
    """An ProxyProximity sensor entity."""

    entity_description: ProxyProximitySensorEntityDescription

    def __init__(
        self,
        coordinator: ProxyProximityCoordinator,
        description: ProxyProximitySensorEntityDescription,
        identifier: str,
        device_unique_id: str,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Initialize an ProxyProximity sensor entity."""
        super().__init__(
            coordinator, identifier, device_unique_id, ProxyProximity_advertisement
        )
        self._attr_unique_id = f"{device_unique_id}_{description.key}"
        self.entity_description = description

    @callback
    def _async_seen(
        self,
        ProxyProximity_advertisement: ProxyProximityAdvertisement,
    ) -> None:
        """Update state."""
        self._attr_available = True
        self._ProxyProximity_advertisement = ProxyProximity_advertisement
        self.async_write_ha_state()

    @callback
    def _async_unavailable(self) -> None:
        """Update state."""
        self._attr_available = False
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self._ProxyProximity_advertisement)
