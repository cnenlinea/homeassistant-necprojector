from homeassistant.config_entries import ConfigFlow

from .const import (
    CONF_MODEL,
    DOMAIN,
)

class NECProjectorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NEC Projector."""
    pass