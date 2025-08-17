"""Switch platform for NEC Projector."""

import asyncio

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
    power_switch = NecProjectorPowerSwitch(
        coordinator=hass.data[entry.entry_id], entry=entry
    )
    shutter_switch = NecProjectorShutterSwitch(
        coordinator=hass.data[entry.entry_id], entry=entry
    )
    async_add_entities([power_switch, shutter_switch], update_before_add=True)


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

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get("power_on", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.api.async_power_on()
        try:
            async with asyncio.timeout(10):
                await self.coordinator.async_request_refresh()
                if self.is_on:
                    return
                await asyncio.sleep(0.5)
        except TimeoutError:
            pass

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.api.async_power_off()
        try:
            async with asyncio.timeout(10):
                await self.coordinator.async_request_refresh()
                if not self.is_on:
                    return
                await asyncio.sleep(0.5)
        except TimeoutError:
            pass


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

    @property
    def is_on(self) -> bool:
        """Return true if the shutter is open."""
        return self.coordinator.data.get("shutter_status", False) == "open"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.async_open_shutter()
        try:
            async with asyncio.timeout(10):
                await self.coordinator.async_request_refresh()
                if self.is_on:
                    return
                await asyncio.sleep(0.5)
        except TimeoutError:
            pass

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.async_close_shutter()
        try:
            async with asyncio.timeout(10):
                await self.coordinator.async_request_refresh()
                if not self.is_on:
                    return
                await asyncio.sleep(0.5)
        except TimeoutError:
            pass
