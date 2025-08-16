"""Switch platform for NEC Projector."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NecProjectorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the NEC Projector switch."""
    switch = NecProjectorSwitch(coordinator=hass.data[entry.entry_id], entry=entry)
    async_add_entities([switch], update_before_add=True)


class NecProjectorSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a NEC Projector switch."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_power"
        self._attr_name = f"{entry.title} Power"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get("power_on", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.api.async_power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.api.async_power_off()
        await self.coordinator.async_request_refresh()
