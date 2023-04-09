"""ProxyProximity sensor integration."""

from homeassistant.helpers.entity import Entity

DOMAIN = "proxyproximity"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the ProxyProximity sensor."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    known_devices = hass.data[DOMAIN][config_entry.entry_id]["known_devices"]
    sensors = []
    for irk in known_devices:
        sensors.append(ProxyProximitySensor(coordinator, irk))
    async_add_entities(sensors)


class ProxyProximitySensor(Entity):
    """Representation of a ProxyProximity sensor."""

    def __init__(self, coordinator, irk):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.irk = irk
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DOMAIN}_{self.irk}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "m"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
        distance_data = self.coordinator.data
        if self.irk in distance_data:
            self._state = distance_data[self.irk]["distance"]
            self._attributes = distance_data[self.irk]["proxies"]
