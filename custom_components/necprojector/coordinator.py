"""DataUpdateCoordinator for the NEC Projector integration."""

from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NecProjectorApi, ProjectorCommandError, ProjectorConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class NecProjectorCoordinator(DataUpdateCoordinator):
    """Manages polling for data from the NEC Projector."""

    def __init__(self, hass, api: NecProjectorApi) -> None:
        """Initialize the data update coordinator."""
        self.api = api
        self.shutter_available = True
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_setup(self):
        try:
            await self.api.async_get_shutter_status()
        except ProjectorCommandError:
            LOGGER.info("Shutter not available, disabling feature")
            self.shutter_available = False

    async def _async_update_data(self):
        """Fetch data from the projector."""
        try:
            power_status = await self.api.async_get_status()
            zoom_status = await self.api.async_get_zoom()
            
            if self.shutter_available:
                shutter_status = await self.api.async_get_shutter_status()
            else:
                shutter_status = {"shutter_status": "disabled"}

            return power_status | shutter_status | zoom_status
        except (ProjectorConnectionError, ProjectorCommandError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
