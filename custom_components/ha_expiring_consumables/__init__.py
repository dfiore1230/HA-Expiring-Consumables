"""HA Expiring Consumables integration."""

from .const import DOMAIN

__version__ = "0.1.6"


async def async_setup_entry(hass, entry):
    """Set up HA Expiring Consumables from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


__all__ = ["__version__"]
