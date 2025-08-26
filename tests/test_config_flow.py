import asyncio
import importlib
import sys
import types
from pathlib import Path


def test_config_flow_form_and_entry(monkeypatch):
    """Ensure the config flow shows a form and creates an entry."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    vol_module = types.ModuleType("voluptuous")

    class Schema:
        def __init__(self, schema):
            self.schema = schema

        def __eq__(self, other):
            return isinstance(other, Schema) and self.schema == other.schema

        def __call__(self, data):
            return data

    vol_module.Schema = Schema
    monkeypatch.setitem(sys.modules, "voluptuous", vol_module)
    import voluptuous as vol

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
    assert result["data_schema"] == vol.Schema({})

    result = asyncio.run(flow.async_step_user(user_input={}))
    assert result["type"] == "create_entry"
    assert result["title"] == cf_module.NAME
    assert result["data"] == {}
