"""Constants for the NEC Projector integration."""

import logging

DOMAIN = "necprojector"
LOGGER = logging.getLogger(__package__)

# Platforms to be set up
PLATFORMS = ["switch"]

# Default values
DEFAULT_NAME = "NEC Projector"
DEFAULT_PORT = 7142
DEFAULT_TIMEOUT = 5
DEFAULT_SCAN_INTERVAL = 30

# Service names
SERVICE_SEND_COMMAND = "send_command"
