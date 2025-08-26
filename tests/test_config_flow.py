import asyncio
import importlib
import sys
import types
from pathlib import Path

def test_config_flow_form_and_entry(monkeypatch):
    """Ensure the config flow shows a form and creates an entry."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    ha_module = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")

    class DummyConfigFlow:
        def __init_subclass__(cls, **kwargs):
            pass

        def async_create_entry(self, title, data):
            return {"type": "create_entry", "title": title, "data": data}

        def async_show_form(self, step_id, data_schema):
            return {"type": "form", "step_id": step_id, "data_schema": data_schema}

    config_entries.ConfigFlow = DummyConfigFlow
    ha_module.config_entries = config_entries
    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)

    cf_module = importlib.import_module("ha_expiring_consumables.config_flow")
    flow = cf_module.HAExpiringConsumablesConfigFlow()

    # Initial call should show the form
    result = asyncio.run(flow.async_step_user())
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    user_input = {"type": "filter", "duration": 30, "start_date": "2024-01-01"}
    result = asyncio.run(flow.async_step_user(user_input=user_input))
    assert result["type"] == "create_entry"
    assert result["title"] == user_input["type"]
    assert result["data"] == user_input
