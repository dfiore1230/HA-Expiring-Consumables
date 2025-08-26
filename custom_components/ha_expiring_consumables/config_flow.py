"""Config flow for the HA Expiring Consumables integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, NAME


class HAExpiringConsumablesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Expiring Consumables."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

        return self.async_create_entry(title=NAME, data={})
