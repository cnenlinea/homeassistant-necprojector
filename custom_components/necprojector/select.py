"""Select platform for NEC Projector."""

from homeassistant.components.select import SelectEntity
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
    """Set up the NEC Projector select entities."""
    select_input = NecProjectorSelectInput(
        coordinator=hass.data[entry.entry_id], entry=entry
    )
    
    async_add_entities([select_input], update_before_add=True)


class NecProjectorSelectInput(CoordinatorEntity, SelectEntity):
    """Representation of a NEC Projector video input."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_input"
        self._attr_name = f"{entry.title} Input"
        self._attr_has_entity_name = True
        self._attr_available = True
        self._attr_option = coordinator.data.get("input_options", [])

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
       
        if self.coordinator.data and self.coordinator.data.get("input_value"):
            self._attr_current_option = self.coordinator.data.get("input_value")
        
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data and self.coordinator.data.get("input_value"):
            self._attr_current_option = self.coordinator.data.get("input_value")
        
        self.async_write_ha_state()
    
    async def async_select_option(self, option: str) -> None:
        if self.coordinator.data.get("power_on"):
            await self.coordinator.api.async_set_input_option(option)
            self._attr_current_option = option
            self.async_write_ha_state()
