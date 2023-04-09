import logging
from homeassistant.helpers.event import async_track_state_change
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ble_distance"
PLATFORM = "sensor"

CONF_DEVICE = "device"
CONF_RSSI_THRESHOLDS = "rssi_thresholds"

DEFAULT_NAME = "BLE Distance Sensor"
DEFAULT_RSSI_THRESHOLDS = [-70, -80, -90]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(
            CONF_RSSI_THRESHOLDS, default=DEFAULT_RSSI_THRESHOLDS
        ): vol.All(cv.ensure_list, [cv.positive_int]),
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([BleDistanceSensor(hass, config)], True)

class BleDistanceSensor(Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self.device = config[CONF_DEVICE]
        self._name = config[CONF_NAME]
        self._rssi_thresholds = sorted(config[CONF_RSSI_THRESHOLDS])
        self._state = None
        self._unit_of_measurement = "m"
        self._attributes = {}

        async_track_state_change(
            self.hass, f"sensor.{self.device}", self.async_state_changed
        )

    async def async_update(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_class(self):
        return DEVICE_CLASS_SIGNAL_STRENGTH

    @property
    def state_attributes(self):
        return self._attributes

    async def async_state_changed(self, entity_id, old_state, new_state):
        if not new_state:
            return

        if new_state.attributes.get("device_class") != DEVICE_CLASS_SIGNAL_STRENGTH:
            return

        if new_state.attributes.get("unit_of_measurement") != SIGNAL_STRENGTH_DECIBELS_MILLIWATT:
            return

        rssi = new_state.state
        distance = self.calculate_distance(rssi)
        self._state = distance
        self._attributes["rssi"] = rssi

        if distance is not
