
from __future__ import annotations

DOMAIN = "consumable_expiration"

CONF_NAME = "name"
CONF_ITEM_TYPE = "item_type"
CONF_DURATION_DAYS = "duration_days"
CONF_START_DATE = "start_date"
CONF_EXPIRY_DATE_OVERRIDE = "expiry_date_override"
CONF_ICON = "icon"

# Default icon mapping for common items (Material Design Icons names)
DEFAULT_ICON_MAP = {
    "water filter": "mdi:water-outline",
    "ac filter": "mdi:hvac",
    "vacuum brush": "mdi:robot-vacuum",
    "fan filter": "mdi:fan",
    "uv light": "mdi:weather-sunny-alert"
}
