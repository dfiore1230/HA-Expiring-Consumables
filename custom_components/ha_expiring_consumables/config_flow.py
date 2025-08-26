"""Config flow for the HA Expiring Consumables integration."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN, NAME


class HAExpiringConsumablesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Expiring Consumables."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step initiated by the user."""
        return self.async_create_entry(title=NAME, data={})
