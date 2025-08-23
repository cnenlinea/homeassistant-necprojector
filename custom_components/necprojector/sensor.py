"""Sensor platform for NEC Projector."""

from homeassistant.components.sensor import SensorEntity
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
    """Set up the NEC Projector sensor entities."""
    status_sensor = NecProjectorStatusSensor(
        coordinator=hass.data[entry.entry_id], entry=entry
    )
    
    async_add_entities(lens_numbers, update_before_add=True)


class NecProjectorStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NEC Projector current status."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_status"
        self._attr_name = f"{entry.title} Status"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data and self.coordinator.data.get("status"):
            self._attr_native_value = float(self.coordinator.data.get("status"))
        
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self.coordinator.data and self.coordinator.data.get("status"):
            self._attr_native_value = float(self.coordinator.data.get("status"))
        
        self.async_write_ha_state()
