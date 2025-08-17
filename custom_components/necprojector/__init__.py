"""The NEC Projector integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .api import NecProjectorApi
from .const import DOMAIN, LOGGER, PLATFORMS, SERVICE_SEND_COMMAND
from .coordinator import NecProjectorCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NEC Projector from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    host = entry.data["host"]
    port = entry.data["port"]

    api = NecProjectorApi(host=host, port=port)
    coordinator = NecProjectorCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def send_command_service(call: ServiceCall) -> dict[str, str]:
        """Handle the send_command service call."""
        command_hex = call.data.get("command", "")
        devices = call.data.get("device_id", [])

        try:
            command_bytes = bytes.fromhex(command_hex)
        except ValueError:
            LOGGER.error("Invalid command format. Must be a hex string")
            return {"response": "Invalid command format"}

        device_reg = dr.async_get(hass)
        for device_id in devices:
            device = device_reg.async_get(device_id)
            if device:
                for config_entry_id in device.config_entries:
                    if config_entry_id in hass.data:
                        target_coordinator = hass.data[config_entry_id]
                        response = (
                            await target_coordinator.api.async_send_custom_command(
                                command_bytes
                            )
                        )
                        await target_coordinator.async_request_refresh()
                        return {"response": response}
        return {"response": "No valid device found"}

    async def send_ascii_command_service(call: ServiceCall) -> dict[str, str]:
        """Handle the send_ascii_command service call."""
        command_str = call.data.get("command", "")
        devices = call.data.get("device_id", [])

        device_reg = dr.async_get(hass)
        for device_id in devices:
            device = device_reg.async_get(device_id)
            if device:
                for config_entry_id in device.config_entries:
                    if config_entry_id in hass.data:
                        target_coordinator = hass.data[config_entry_id]
                        response = await target_coordinator.api.async_send_custom_ascii_command(
                            command_str
                        )
                        await target_coordinator.async_request_refresh()
                        return {"response": response}
        return {"response": "No valid device found"}

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        send_command_service,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "send_ascii_command",
        send_ascii_command_service,
        supports_response=SupportsResponse.ONLY,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(entry.entry_id)

    if not hass.data:
        hass.services.async_remove(DOMAIN, SERVICE_SEND_COMMAND)

    return unload_ok
