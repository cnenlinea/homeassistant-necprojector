"""Number platform for NEC Projector."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import NecProjectorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the NEC Projector number entities."""
    zoom_number = NecProjectorZoomNumber(
        coordinator=hass.data[entry.entry_id], entry=entry
    )
    async_add_entities([zoom_number], update_before_add=True)


class NecProjectorZoomNumber(CoordinatorEntity, NumberEntity):
    """Representation of a NEC Projector zoom."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_native_step = 1
        self._attr_unique_id = f"{entry.unique_id}_zoom"
        self._attr_name = f"{entry.title} Zoom"
        self._attr_mode = NumberMode.BOX

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data and self.coordinator.data.get("zoom_value"):
            try:
                self._attr_native_value = float(self.coordinator.data.get("zoom_value"))
            except ValueError as ex:
                LOGGER.error(
                    "ValueError for zoom_value, %s",
                    ex,
                )
            except TypeError as ex:
                LOGGER.error("TypeError for zoom_value, %s", ex)
        else:
            LOGGER.debug("zoom_value is not available")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if self.coordinator.data and self.coordinator.data.get("zoom_value"):
            try:
                self._attr_native_value = float(self.coordinator.data.get("zoom_value"))
                self._attr_native_max_value = float(
                    self.coordinator.data.get("max_zoom")
                )
                self._attr_native_min_value = float(
                    self.coordinator.data.get("min_zoom")
                )
            except ValueError as ex:
                LOGGER.error(
                    "ValueError for zoom_level, %s",
                    ex,
                )
            except TypeError as ex:
                LOGGER.error("TypeError for zoom_value, %s", ex)
        else:
            LOGGER.debug("zoom_value is not available")

    async def async_set_native_value(self, value: float) -> None:
        """Turn the switch on."""
        if self.coordinator.data.get("power_on"):
            zoom_level = int(value)
            await self.coordinator.api.async_set_zoom(zoom_level)
