from __future__ import annotations

from typing import Any, TYPE_CHECKING, Dict

from .const import CONF_DURATION_DAYS, CONF_START_DATE

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


def merge_entry_options(entry: "ConfigEntry", **updates: Any) -> Dict[str, Any]:
    """Return updated options preserving existing values.

    Ensures that required option fields like duration and start date are
    retained when only a subset of options are provided during an update.
    """
    options: Dict[str, Any] = dict(getattr(entry, "options", {}))
    data = getattr(entry, "data", {})

    if CONF_DURATION_DAYS not in options and CONF_DURATION_DAYS in data:
        options[CONF_DURATION_DAYS] = data[CONF_DURATION_DAYS]
    if CONF_START_DATE not in options and CONF_START_DATE in data:
        options[CONF_START_DATE] = data[CONF_START_DATE]

    options.update(updates)
    return options
