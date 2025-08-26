"""Config flow for the HA Expiring Consumables integration."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN, NAME


class HAExpiringConsumablesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Expiring Consumables."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step initiated by the user."""
        if user_input is None:
            data_schema = {
                "type": str,
                "duration": int,
                "start_date": str,
            }
            return self.async_show_form(step_id="user", data_schema=data_schema)

        title = user_input.get("type", NAME)
        return self.async_create_entry(title=title, data=user_input)
