"""API for NEC Projector Control."""

import asyncio
import re

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, LOGGER

# NEC Projector Commands (Hex Bytes)
CMD_POWER_ON = b"\x02\x00\x00\x00\x00\x02"
CMD_POWER_OFF = b"\x02\x01\x00\x00\x00\x03"
CMD_STATUS_QUERY = b"\x00\x85\x00\x00\x01\x01\x87"
# NEC Projector Commands (ASCII)
CMD_SHUTTER = "shutter {shutter_arg}\r"
CMD_LENS = "lens {lens_subcmd} {lens_arg}\r"
CMD_INPUT = "input {input_arg}"


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

    async def async_open_shutter(self) -> None:
        """Turn the projector on."""
        command = CMD_SHUTTER.format(shutter_arg="open").encode("ascii")
        await self._send_command(command)

    async def async_close_shutter(self) -> None:
        """Turn the projector off."""
        command = CMD_SHUTTER.format(shutter_arg="close").encode("ascii")
        await self._send_command(command)

    async def async_get_shutter_status(self) -> dict[str, bool]:
        """Turn the projector off."""
        command = CMD_SHUTTER.format(shutter_arg="?").encode("ascii")
        response = await self._send_command(command)
        shutter_value = re.search("(?<=cur\\=)\\w+", response.decode())
        if not shutter_value:
            raise ProjectorCommandError(
                "Invalid shutter status response from projector"
            )
        return {"shutter_status": shutter_value.group()}

    async def async_get_status(self) -> dict[str, bool]:
        """Get the power status of the projector."""
        response = await self._send_command(CMD_STATUS_QUERY)

        if not response or response[0] != 0x20 or response[1] != 0x85:
            raise ProjectorCommandError("Invalid status response from projector")

        # DATA03 indicates power status: 0x01 is Power On
        power_on = response[7] == 0x01

        status = {
            0x00: "Standby (Sleep)",
            0x04: "Power on",
            0x05: "Cooling",
            0x06: "Standby (error)",
            0x0f: "Standby (Power saving)",
            0x10: "Network standby",
            0xff: "Not supported"
        }.get(response[10], "Invalid status")

        return {"power_on": power_on, "status": status}

    async def async_get_lens_value(self, lens_subcommand: str) -> dict[str, str]:
        command = CMD_LENS.format(lens_subcmd=lens_subcommand, lens_arg="?").encode("ascii")
        response = await self._send_command(command)
        decoded_response = response.decode()
        lens_value = re.search("(?<=cur\\=)\\d+", decoded_response)
        max_value = re.search("(?<=max\\=)\\d+", decoded_response)
        min_value = re.search("(?<=min\\=)\\d+", decoded_response)
        if not lens_value or not max_value or not min_value:
            raise ProjectorCommandError(
                f"Invalid lens response for {lens_subcommand} from projector: {decoded_response}"
            )
        return {
            f"{lens_subcommand}_value": lens_value.group(),
            f"{lens_subcommand}_max": max_value.group(),
            f"{lens_subcommand}_min": min_value.group(),
        }

    async def async_set_lens_value(self, lens_subcommand: str, lens_value: int) -> None:
        command = CMD_LENS.format(lens_subcmd=lens_subcommand, lens_arg=lens_value).encode("ascii")
        await self._send_command(command)

    async def async_get_input_options(self) -> dict[str, str | list[str]]:
        command = CMD_INPUT.format(input_arg="?")
        response = await self._send_command(command)
        decoded_response = response.decode()
        input_value = re.search("(?<=cur\\=)\\w+", decoded_response)
        input_options = re.search("(?<=sel\\=)\\w+", decoded_response)

        input_value = input_value.group() if input_value else ""
        input_options = input_options.group() if input_options else ""
        input_options = input_options.split(",")
        
        return {
            "input_value": input_value,
            "input_options": input_options
        }

    async def async_set_input_option(input_value: str) -> None:
        command = CMD_INPUT.format(input_arg=input_value).encode("ascii")
        await self._send_command(command)

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
