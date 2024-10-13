import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ElectricUsageSensor(coordinator)])

class ElectricUsageSensor(CoordinatorEntity, SensorEntity):
    """Representation of an electric usage sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Electric Usage"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_unique_id = "electric_usage"

    @property
    def native_value(self):
        """Return the current value of the sensor."""
        return self.coordinator.data.get("usage") if self.coordinator.data else None

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self.coordinator.last_update_success
