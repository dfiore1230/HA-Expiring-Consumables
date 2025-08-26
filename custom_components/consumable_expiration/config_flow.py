
from __future__ import annotations

import datetime as dt
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ITEM_TYPE,
    CONF_DURATION_DAYS,
    CONF_START_DATE,
    CONF_EXPIRY_DATE_OVERRIDE,
    CONF_ICON,
    DEFAULT_ICON_MAP,
)

_LOGGER = logging.getLogger(__name__)


class ConsumableConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Normalize values
            name = user_input[CONF_NAME].strip()
            item_type = user_input.get(CONF_ITEM_TYPE)
            icon = user_input.get(CONF_ICON)
            duration = int(user_input[CONF_DURATION_DAYS])
            start_date = user_input.get(CONF_START_DATE)
            expiry_override = user_input.get(CONF_EXPIRY_DATE_OVERRIDE)

            if isinstance(start_date, str):
                start_date = dt.date.fromisoformat(start_date)
            if isinstance(expiry_override, str):
                expiry_override = dt.date.fromisoformat(expiry_override)
            if expiry_override:
                start_date = expiry_override - dt.timedelta(days=duration)

            if duration < 1:
                errors["base"] = "invalid_duration"
            else:
                if not icon:
                    # default from item_type, else try by name
                    if item_type and item_type in DEFAULT_ICON_MAP:
                        icon = DEFAULT_ICON_MAP[item_type]
                    else:
                        icon = DEFAULT_ICON_MAP.get(name.lower())
                data = {
                    CONF_NAME: name,
                    CONF_ITEM_TYPE: item_type,
                    CONF_ICON: icon,
                    # Keep duration/start_date in options so they can be changed later easily
                }
                options = {
                    CONF_DURATION_DAYS: duration,
                    CONF_START_DATE: start_date.isoformat()
                    if hasattr(start_date, "isoformat")
                    else str(start_date),
                }
                return self.async_create_entry(title=name, data=data, options=options)

        today = dt.date.today()

        schema = vol.Schema({
            vol.Required(CONF_NAME): selector.TextSelector(),
            vol.Optional(CONF_ITEM_TYPE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(DEFAULT_ICON_MAP.keys()),
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(CONF_ICON): selector.IconSelector(),
            vol.Required(CONF_DURATION_DAYS, default=90): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=1825, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_START_DATE, default=today): selector.DateSelector(),
            vol.Optional(CONF_EXPIRY_DATE_OVERRIDE): selector.DateSelector(),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class ConsumableOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        data = self.config_entry.data
        options = self.config_entry.options

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            item_type = user_input.get(CONF_ITEM_TYPE)
            icon = user_input.get(CONF_ICON)
            duration = int(user_input[CONF_DURATION_DAYS])
            start_date = user_input.get(CONF_START_DATE)
            expiry_override = user_input.get(CONF_EXPIRY_DATE_OVERRIDE)

            if isinstance(start_date, str):
                start_date = dt.date.fromisoformat(start_date)
            if isinstance(expiry_override, str):
                expiry_override = dt.date.fromisoformat(expiry_override)

            if expiry_override:
                start_date = expiry_override - dt.timedelta(days=duration)

            new_data = data.copy()
            new_data.update({
                CONF_NAME: name,
                CONF_ITEM_TYPE: item_type,
                CONF_ICON: icon,
            })
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)

            new_options = {
                CONF_DURATION_DAYS: duration,
                CONF_START_DATE: start_date.isoformat()
                if hasattr(start_date, "isoformat")
                else str(start_date),
            }
            return self.async_create_entry(title="", data=new_options)

        # Parse existing date
        try:
            current_date = options.get(CONF_START_DATE)
            if isinstance(current_date, str):
                year, month, day = map(int, current_date.split("-"))
                current_date = dt.date(year, month, day)
        except Exception:
            current_date = dt.date.today()

        duration = int(options.get(CONF_DURATION_DAYS, 90))
        due_date = current_date + dt.timedelta(days=duration)

        schema = vol.Schema({
            vol.Required(CONF_NAME, default=data.get(CONF_NAME)): selector.TextSelector(),
            vol.Optional(CONF_ITEM_TYPE, default=data.get(CONF_ITEM_TYPE)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(DEFAULT_ICON_MAP.keys()),
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(CONF_ICON, default=data.get(CONF_ICON)): selector.IconSelector(),
            vol.Required(CONF_DURATION_DAYS, default=duration): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=1825, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_START_DATE, default=current_date): selector.DateSelector(),
            vol.Optional(CONF_EXPIRY_DATE_OVERRIDE, default=due_date): selector.DateSelector(),
        })
        return self.async_show_form(step_id="init", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ConsumableOptionsFlowHandler(config_entry)
