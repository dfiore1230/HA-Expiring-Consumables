
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ITEM_TYPE,
    CONF_DURATION_DAYS,
    CONF_START_DATE,
    CONF_ICON,
)

PARALLEL_UPDATES = 0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entity = ConsumableExpirationSensor(hass, entry)
    async_add_entities([entity])


class ConsumableExpirationSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "days_remaining"
    _attr_native_unit_of_measurement = "days"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_days_remaining"
        # Map entity id to entry for services
        hass.data[DOMAIN]["entity_map"][
            self.entity_id if hasattr(self, "entity_id") else self._attr_unique_id
        ] = entry.entry_id
        self._unsub_midnight = None

    async def async_added_to_hass(self) -> None:
        # After entity_id is assigned
        self.hass.data[DOMAIN]["entity_map"][self.entity_id] = self.entry.entry_id
        # Update at startup and daily shortly after midnight
        @callback
        def _midnight_refresh(now):
            self.async_write_ha_state()

        self._unsub_midnight = async_track_time_change(
            self.hass, _midnight_refresh, hour=0, minute=0, second=30
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_midnight:
            self._unsub_midnight()
            self._unsub_midnight = None

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
        icon = self.entry.data.get(CONF_ICON)
        return icon or "mdi:calendar-clock"

    @property
    def native_value(self) -> int | None:
        duration, start_date = self._get_params()
        if not duration or not start_date:
            return None
        now = dt_util.now().date()
        elapsed = (now - start_date).days
        remaining = max(duration - elapsed, 0)
        return remaining

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        duration, start_date = self._get_params()
        if not duration or not start_date:
            return {}
        due_date = start_date + dt.timedelta(days=duration)
        now = dt_util.now().date()
        elapsed = (now - start_date).days
        percent_used = min(100.0, max(0.0, (elapsed / duration) * 100.0)) if duration else None
        return {
            "start_date": start_date.isoformat(),
            "duration_days": duration,
            "due_date": due_date.isoformat(),
            "days_elapsed": max(elapsed, 0),
            "percent_used": round(percent_used, 1) if percent_used is not None else None,
            "expired": (now >= due_date),
        }

    def _get_params(self) -> tuple[int | None, dt.date | None]:
        duration = self.entry.options.get(CONF_DURATION_DAYS) or self.entry.data.get(CONF_DURATION_DAYS)
        start = self.entry.options.get(CONF_START_DATE) or self.entry.data.get(CONF_START_DATE)
        if isinstance(start, str):
            try:
                y, m, d = map(int, start.split("-"))
                start_date = dt.date(y, m, d)
            except Exception:
                start_date = None
        elif isinstance(start, dt.date):
            start_date = start
        else:
            start_date = None
        try:
            duration = int(duration) if duration is not None else None
        except Exception:
            duration = None
        return duration, start_date
