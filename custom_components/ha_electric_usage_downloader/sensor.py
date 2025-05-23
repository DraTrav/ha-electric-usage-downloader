import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform from a config entry."""
    try:
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
        async_add_entities([ElectricUsageSensor(coordinator)])
    except KeyError as e:
        _LOGGER.error(f"Error setting up sensor entry: {e}")

class ElectricUsageSensor(CoordinatorEntity, SensorEntity):
    """Representation of an electric usage sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Electric Usage"
        self._attr_unit_of_measurement = UnitOfEnergy
        self._attr_unique_id = "electric_usage"

    @property
    def native_value(self):
        """Return the current value of the sensor."""
        return self.coordinator.data.get("usage") if self.coordinator.data else None

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self.coordinator.last_update_success
