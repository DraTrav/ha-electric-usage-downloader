import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, SCAN_INTERVAL
from .api import ElectricUsageAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Electric Usage Downloader from a config entry."""
    try:
        username = entry.data["username"]
        password = entry.data["password"]
        login_url = entry.data["login_url"]
        usage_url = entry.data["usage_url"]

        session = async_get_clientsession(hass)
        api = ElectricUsageAPI(session, username, password, login_url, usage_url)

        coordinator = ElectricUsageCoordinator(hass, api)
        await coordinator.async_refresh()  # Fetch initial data

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        return True

    except Exception as e:
        _LOGGER.error(f"Failed to set up entry: {e}")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Electric Usage Downloader."""
    try:
        hass.data[DOMAIN].pop(entry.entry_id)
        return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    except Exception as e:
        _LOGGER.error(f"Error unloading entry: {e}")
        return False

class ElectricUsageCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching electric usage data."""

    def __init__(self, hass: HomeAssistant, api: ElectricUsageAPI):
        """Initialize the coordinator."""
        self.api = api
        super().__init__(hass, _LOGGER, name="Electric Usage Coordinator", update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            await self.api.login()
            return await self.api.get_usage_data()
        except Exception as e:
            _LOGGER.error(f"Error fetching data from API: {e}")
            return None
