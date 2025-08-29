
from __future__ import annotations

import datetime as dt

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NAME, CONF_START_DATE


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([MarkReplacedButton(hass, entry)])


class MarkReplacedButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "mark_replaced"
    _attr_state = "idle"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_mark_replaced"

    @property
    def device_info(self) -> DeviceInfo | None:
        name = self.entry.data.get(CONF_NAME, "Consumable")
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=name,
            manufacturer="dfiore1230",
            model="HA Expiring Consumables",
        )

    @property
    def icon(self) -> str | None:
        return "mdi:backup-restore"

    async def async_added_to_hass(self) -> None:
        """Reset state when the entity is added to Home Assistant."""
        await super().async_added_to_hass()
        self._attr_state = "idle"
        self.async_write_ha_state()

    async def async_press(self) -> None:
        today = dt.date.today().isoformat()
        options = {**self.entry.options, CONF_START_DATE: today}
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self._attr_state = dt.datetime.now().isoformat()
        self.async_write_ha_state()
