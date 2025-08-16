"""Config flow for NEC Projector."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT

from .api import NecProjectorApi, ProjectorConnectionError
from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN


class NecProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NEC Projector."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input["host"]
            port = user_input["port"]

            # Use host as a unique ID to prevent duplicates
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            api = NecProjectorApi(host=host, port=port)
            try:
                if await api.async_test_connection():
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )
                errors["base"] = "cannot_connect"
            except ProjectorConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
