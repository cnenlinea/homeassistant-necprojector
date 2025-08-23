"""Switch platform for NEC Projector."""

import asyncio

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
    switches = [
        NecProjectorPowerSwitch(
            coordinator=hass.data[entry.entry_id], entry=entry
        )
    ]
    if hass.data[entry.entry_id].data.get("shutter_status") != "disabled":
        shutter_switch = NecProjectorShutterSwitch(
            coordinator=hass.data[entry.entry_id], entry=entry
        )
        switches.append(shutter_switch)
    async_add_entities(switches, update_before_add=True)


class NecProjectorPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a NEC Projector power switch."""

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

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self.coordinator.data:
            self._attr_is_on = self.coordinator.data.get("power_on", False)
    
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data:
            self._attr_is_on = self.coordinator.data.get("power_on", False)
    
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.api.async_power_on()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.api.async_power_off()
        self._attr_is_on = False
        self.async_write_ha_state()

class NecProjectorShutterSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a NEC Projector shutter switch."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_shutter"
        self._attr_name = f"{entry.title} Shutter"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self.coordinator.data:
            self._attr_is_on = self.coordinator.data.get("shutter_status", False) == "open"
    
        self.async_write_ha_state()
    
    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data:
            self._attr_is_on = self.coordinator.data.get("shutter_status", False) == "open"
    
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.async_open_shutter()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.async_close_shutter()
        self._attr_is_on = False
        self.async_write_ha_state()
