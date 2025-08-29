
from __future__ import annotations

import datetime as dt
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import (
    DOMAIN,
    CONF_DURATION_DAYS,
    CONF_START_DATE,
)
from .util import merge_entry_options

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entity_map", {})  # entity_id -> entry_id
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Ensure options are present
    data = dict(entry.data)
    options = dict(entry.options)
    changed = False

    if CONF_DURATION_DAYS not in options and CONF_DURATION_DAYS in data:
        options[CONF_DURATION_DAYS] = data[CONF_DURATION_DAYS]
        changed = True
    if CONF_START_DATE not in options and CONF_START_DATE in data:
        options[CONF_START_DATE] = data[CONF_START_DATE]
        changed = True

    if changed:
        hass.config_entries.async_update_entry(entry, options=options)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_update_listener))

    # Register services (idempotent)
    _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Clean entity map entries for this config entry
    emap: dict[str, str] = hass.data[DOMAIN].get("entity_map", {})
    to_del = [eid for eid, e in emap.items() if e == entry.entry_id]
    for eid in to_del:
        emap.pop(eid, None)
    return unloaded


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    # Reload entities when options change
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(hass: HomeAssistant) -> None:
    if getattr(hass.data[DOMAIN], "services_registered", False):
        return

    import voluptuous as vol
    import homeassistant.helpers.config_validation as cv

    async def _resolve_entry_from_entity(hass: HomeAssistant, entity_id: str):
        _LOGGER.debug("Resolving config entry for entity %s", entity_id)
        emap: dict[str, str] = hass.data[DOMAIN]["entity_map"]
        entry_id = emap.get(entity_id)
        if entry_id:
            _LOGGER.debug("Found entry %s in entity map for %s", entry_id, entity_id)
        if not entry_id:
            # Fallback: look up via entity registry to get config entry id
            _LOGGER.debug("Entity %s not found in map; checking entity registry", entity_id)
            ent_reg = er.async_get(hass)
            ent = ent_reg.async_get(entity_id)
            if ent:
                entry_id = ent.config_entry_id
                _LOGGER.debug("Resolved entry %s via entity registry for %s", entry_id, entity_id)
        if not entry_id:
            _LOGGER.debug("Could not resolve config entry for %s", entity_id)
            raise vol.Invalid(f"Could not resolve config entry for {entity_id}")
        return hass.config_entries.async_get_entry(entry_id)

    set_start_date_schema = vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("start_date"): cv.date,
        }
    )
    set_expiry_date_schema = vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("expiry_date"): cv.date,
        }
    )
    set_duration_schema = vol.Schema(
        {
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("duration_days"): vol.All(vol.Coerce(int), vol.Range(min=1)),
        }
    )
    mark_replaced_schema = vol.Schema({vol.Required("entity_id"): cv.entity_id})

    async def handle_set_start(call: ServiceCall):
        entity_id = call.data["entity_id"]
        new_date: dt.date = call.data["start_date"]
        _LOGGER.debug("Service set_start_date called for %s with %s", entity_id, new_date)
        entry = await _resolve_entry_from_entity(hass, entity_id)
        if not entry:
            return
        options = merge_entry_options(entry, **{CONF_START_DATE: new_date.isoformat()})
        _LOGGER.debug("Updating entry %s options to %s", entry.entry_id, options)
        hass.config_entries.async_update_entry(entry, options=options)

    async def handle_set_expiry(call: ServiceCall):
        entity_id = call.data["entity_id"]
        new_expiry: dt.date = call.data["expiry_date"]
        _LOGGER.debug("Service set_expiry_date called for %s with %s", entity_id, new_expiry)
        entry = await _resolve_entry_from_entity(hass, entity_id)
        if not entry:
            return
        duration = entry.options.get(CONF_DURATION_DAYS) or entry.data.get(CONF_DURATION_DAYS)
        if not duration:
            _LOGGER.debug("Duration missing for %s", entity_id)
            raise vol.Invalid("Duration not configured")
        start_date = new_expiry - dt.timedelta(days=duration)
        options = merge_entry_options(entry, **{CONF_START_DATE: start_date.isoformat()})
        _LOGGER.debug(
            "Updating entry %s options to %s for expiry", entry.entry_id, options
        )
        hass.config_entries.async_update_entry(entry, options=options)

    async def handle_set_duration(call: ServiceCall):
        entity_id = call.data["entity_id"]
        days: int = call.data["duration_days"]
        _LOGGER.debug("Service set_duration called for %s with %s", entity_id, days)
        entry = await _resolve_entry_from_entity(hass, entity_id)
        if not entry:
            return
        options = merge_entry_options(entry, **{CONF_DURATION_DAYS: days})
        _LOGGER.debug("Updating entry %s options to %s", entry.entry_id, options)
        hass.config_entries.async_update_entry(entry, options=options)

    async def handle_mark_replaced(call: ServiceCall):
        entity_id = call.data["entity_id"]
        _LOGGER.debug("Service mark_replaced called for %s", entity_id)
        entry = await _resolve_entry_from_entity(hass, entity_id)
        if not entry:
            return
        today = dt.date.today().isoformat()
        options = merge_entry_options(entry, **{CONF_START_DATE: today})
        _LOGGER.debug("Updating entry %s options to %s", entry.entry_id, options)
        hass.config_entries.async_update_entry(entry, options=options)

    hass.services.async_register(
        DOMAIN, "set_start_date", handle_set_start, schema=set_start_date_schema
    )
    hass.services.async_register(
        DOMAIN, "set_duration", handle_set_duration, schema=set_duration_schema
    )
    hass.services.async_register(
        DOMAIN, "set_expiry_date", handle_set_expiry, schema=set_expiry_date_schema
    )
    hass.services.async_register(
        DOMAIN, "mark_replaced", handle_mark_replaced, schema=mark_replaced_schema
    )
    hass.data[DOMAIN]["services_registered"] = True
