"""API for NEC Projector Control."""

import asyncio

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, LOGGER

# NEC Projector Commands (Hex Bytes)
CMD_POWER_ON = b"\x02\x00\x00\x00\x00\x02"
CMD_POWER_OFF = b"\x02\x01\x00\x00\x00\x03"
CMD_STATUS_QUERY = b"\x00\x85\x00\x00\x01\x01\x87"


class ProjectorConnectionError(Exception):
    """Exception to indicate a connection error."""


class ProjectorCommandError(Exception):
    """Exception to indicate a command error."""


class NecProjectorApi:
    """API to control an NEC projector."""

    def __init__(
        self, host: str, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        """Initialize the API."""
        self._host = host
        self._port = port
        self._timeout = timeout

    async def _send_command(self, command: bytes) -> bytes:
        """Send a command to the projector and return the response."""
        try:
            async with asyncio.timeout(self._timeout):
                reader, writer = await asyncio.open_connection(self._host, self._port)
                writer.write(command)
                await writer.drain()
                response = await reader.read(4096)
                writer.close()
                await writer.wait_closed()
                return response
        except TimeoutError as exc:
            raise ProjectorConnectionError(
                f"Timeout connecting to {self._host}:{self._port}"
            ) from exc
        except (ConnectionRefusedError, OSError) as exc:
            raise ProjectorConnectionError(
                f"Error connecting to {self._host}:{self._port}"
            ) from exc

    async def async_power_on(self) -> None:
        """Turn the projector on."""
        await self._send_command(CMD_POWER_ON)

    async def async_power_off(self) -> None:
        """Turn the projector off."""
        await self._send_command(CMD_POWER_OFF)

    async def async_get_status(self) -> dict[str, bool]:
        """Get the power status of the projector."""
        response = await self._send_command(CMD_STATUS_QUERY)

        if not response or response[0] != 0x20 or response[1] != 0x85:
            raise ProjectorCommandError("Invalid status response from projector")

        # DATA03 indicates power status: 0x01 is Power On
        power_on = response[2] == 0x01

        return {"power_on": power_on}

    async def async_test_connection(self) -> bool:
        """Test the connection to the projector."""
        try:
            await self.async_get_status()
        except (ProjectorConnectionError, ProjectorCommandError) as exc:
            LOGGER.error("Failed to connect or get status from projector: %s", exc)
            return False

        return True

    async def async_send_custom_command(self, command: bytes) -> str:
        """Send a custom command to the projector."""
        response = await self._send_command(command)
        return response.hex()

    async def async_send_custom_ascii_command(self, command_str: str) -> str:
        """Send a custom ASCII command to the projector."""
        if not command_str.endswith("\r"):
            command_str += "\r"
        command_bytes = command_str.encode("ascii")
        response = await self._send_command(command_bytes)
        return response.decode()
