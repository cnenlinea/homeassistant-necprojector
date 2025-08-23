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
    lens_properties = ["zoom", "focus", "h_shift", "v_shift"]

    lens_numbers = [NecProjectorLensNumber(
            coordinator=hass.data[entry.entry_id], entry=entry, lens_property=p
        ) for p in lens_properties
    ]
    async_add_entities(lens_numbers, update_before_add=True)


class NecProjectorLensNumber(CoordinatorEntity, NumberEntity):
    """Representation of a NEC Projector lens property."""

    def __init__(
        self, coordinator: NecProjectorCoordinator, entry: ConfigEntry, lens_property: str
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self.lens_property = lens_property
        self._entry = entry
        self._attr_native_step = 1
        self._attr_unique_id = f"{entry.unique_id}_{lens_property}"
        self._attr_name = f"{entry.title} {lens_property.capitalize()}"
        self._attr_mode = NumberMode.BOX

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)}, name=self._entry.title
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        value_property = f"{self.lens_property}_value"
        if self.coordinator.data and self.coordinator.data.get(value_property):
            try:
                self._attr_native_value = float(self.coordinator.data.get(value_property))
            except ValueError as ex:
                LOGGER.error(
                    "ValueError for %s, %s",
                    value_property,
                    ex
                )
            except TypeError as ex:
                LOGGER.error("TypeError for %s, %s", value_property, ex)
        else:
            LOGGER.debug(f"{value_property} is not available")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        value_property = f"{self.lens_property}_value"
        max_property = f"{self.lens_property}_max"
        min_property = f"{self.lens_property}_min"

        if self.coordinator.data and self.coordinator.data.get(value_property):
            try:
                self._attr_native_value = float(self.coordinator.data.get(value_property))
                self._attr_native_max_value = float(
                    self.coordinator.data.get(max_property)
                )
                self._attr_native_min_value = float(
                    self.coordinator.data.get(min_property)
                )
            except ValueError as ex:
                LOGGER.error(
                    "ValueError for %s, %s",
                    value_property,
                    ex
                )
            except TypeError as ex:
                LOGGER.error("TypeError for %s, %s", value_property, ex)
        else:
            LOGGER.debug(f"{value_property} is not available")

    async def async_set_native_value(self, value: float) -> None:
        """Turn the switch on."""
        if self.coordinator.data.get("power_on"):
            lens_value = int(value)
            await self.coordinator.api.async_set_lens_value(self.lens_property, lens_value)
