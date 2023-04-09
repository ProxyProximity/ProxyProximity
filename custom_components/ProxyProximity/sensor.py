"""Platform for the ProxyProximity integration."""
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_NAME,
    DEVICE_CLASS_TIMESTAMP,
    STATE_UNKNOWN,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

CONF_KNOWN_DEVICES = "known_devices"
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 60  # seconds

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_DEVICE_CLASS, default=DEVICE_CLASS_TIMESTAMP): cv.string,
        vol.Optional("tx_power", default=None): vol.Any(int, None),
        vol.Optional("mac_address"): cv.string,
        vol.Optional("irk"): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KNOWN_DEVICES): vol.Schema({cv.string: DEVICE_SCHEMA}),
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
    }
)


def estimate_distance(rssi, tx_power):
    """
    Estimate the distance to a BLE device given RSSI and the known TX power.
    """
    if rssi == 0:
        return -1.0
    if tx_power is None:
        return None
    ratio = rssi * 1.0 / tx_power
    if ratio < 1.0:
        return pow(ratio, 10)
    else:
        distance = 0.89976 * pow(ratio, 7.7095) + 0.111
        return distance


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ProxyProximity sensor."""
    known_devices = config[CONF_KNOWN_DEVICES]
    update_interval = config[CONF_UPDATE_INTERVAL]
    async_add_entities(
        [
            ProxyProximitySensor(name=device["name"], device=device, hass=hass)
            for device in known_devices.values()
        ]
    )

    async def update_ble_state(now):
        """Update BLE state and calculate distances."""
        devices = []
        for device in known_devices.values():
            if device["irk"]:
                devices.append(device["irk"])

        if not devices:
            return

        states = await hass.async_add_executor_job(hass.states.all)

        for state in states:
            if not state.entity_id.startswith("proximity."):
                continue

            device_irk = state.attributes.get("irk")
            if device_irk not in devices:
                continue

            rssi = state.attributes.get("rssi")
            tx_power = known_devices[device_irk].get("tx_power")
            distance = estimate_distance(rssi, tx_power)

            if distance is None:
                state.attributes["distance"] = None
            elif distance == -1.0:
                state.attributes["distance"] = STATE_UNKNOWN
            else:
                state.attributes["distance"] = round(distance, 2)

            state.attributes["last_updated"] = str(state.last_updated)

            hass.states.async_set(state.entity_id, state.state, state.attributes)

    async_track_time_interval(hass, update_ble_state, update_interval)


class ProxyProximitySensor(RestoreEntity):
    """Representation of a proximity sensor."""

    def __init__(self, name, device, hass):
        """Initialize the sensor."""
        self._name = name
        self._device = device
        self._hass = hass
        self._state = STATE_UNKNOWN
        self._last_updated = None
        self._distance = None

        if self._device.get("mac_address"):
            self._unique_id = f"{self._device['mac_address']}_proximity"
        else:
            self._unique_id = f"{self._device['irk']}_proximity"

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attrs = {}

        if self._distance is not None:
            attrs["distance"] = self._distance
        if self._last_updated is not None:
            attrs["last_updated"] = self._last_updated

        return attrs

    @property
    def unique_id(self):
        """Return the unique ID of this sensor."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        await super().async_added_to_hass()

        # restore previous state
        state = await self.async_get_last_state()
        if state:
            self._state = state.state
            self._last_updated = state.attributes.get("last_updated")
            self._distance = state.attributes.get("distance")

        # register event listener
        self.async_on_remove(
            self._hass.bus.async_listen(
                "proximity_enter", self._handle_proximity_event
            )
        )

    def _handle_proximity_event(self, event):
        """Handle a proximity event."""
        if event.data.get("irks") is None:
            # no IRK filter - assume all devices match
            self._update_proximity_state(event.data)
        elif self._device.get("irk") in event.data["irks"]:
            # device matches IRK filter
            self._update_proximity_state(event.data)

    def _update_proximity_state(self, data):
        """Update proximity state based on data."""
        rssi = data["rssi"]
        tx_power = self._device.get("tx_power")
        distance = estimate_distance(rssi, tx_power)

        if distance is None:
            self._distance = None
        elif distance == -1.0:
            self._distance = STATE_UNKNOWN
        else:
            self._distance = round(distance, 2)

        self._last_updated = str(data["last_seen"])
        self._state = self._distance

        self.async_schedule_update_ha_state()

    async def async_update(self):
        """No update needed."""    
