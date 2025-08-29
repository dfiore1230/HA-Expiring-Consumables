import sys
from pathlib import Path
import types


def test_merge_entry_options_preserves_fields(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))
    from consumable_expiration.util import merge_entry_options
    from consumable_expiration.const import CONF_DURATION_DAYS, CONF_START_DATE

    class ConfigEntry:
        def __init__(self):
            self.data = {}
            self.options = {CONF_DURATION_DAYS: 30, CONF_START_DATE: "2024-01-01"}

    entry = ConfigEntry()
    new_options = merge_entry_options(entry, **{CONF_START_DATE: "2024-02-01"})
    assert new_options[CONF_DURATION_DAYS] == 30
    assert new_options[CONF_START_DATE] == "2024-02-01"


def test_merge_entry_options_uses_data(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))
    from consumable_expiration.util import merge_entry_options
    from consumable_expiration.const import CONF_DURATION_DAYS, CONF_START_DATE

    class ConfigEntry:
        def __init__(self):
            self.data = {CONF_DURATION_DAYS: 45, CONF_START_DATE: "2024-03-01"}
            self.options = {}

    entry = ConfigEntry()
    new_options = merge_entry_options(entry, **{CONF_START_DATE: "2024-04-01"})
    assert new_options[CONF_DURATION_DAYS] == 45
    assert new_options[CONF_START_DATE] == "2024-04-01"
