import asyncio
import importlib
import sys
import types
from pathlib import Path

def test_config_flow_creates_entry(monkeypatch):
    """Ensure the config flow creates an entry without showing a form."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    ha_module = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")

    class DummyConfigFlow:
        def __init_subclass__(cls, **kwargs):
            pass

        def async_create_entry(self, title, data):
            return {"type": "create_entry", "title": title, "data": data}

    config_entries.ConfigFlow = DummyConfigFlow
    ha_module.config_entries = config_entries
    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)

    cf_module = importlib.import_module("ha_expiring_consumables.config_flow")
    flow = cf_module.HAExpiringConsumablesConfigFlow()
    result = asyncio.run(flow.async_step_user())
    assert result["type"] == "create_entry"
    assert result["title"] == cf_module.NAME
