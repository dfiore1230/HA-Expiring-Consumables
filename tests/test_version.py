from pathlib import Path
import importlib
import sys
import types


def test_import_version(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    vol_module = types.ModuleType("voluptuous")
    class Invalid(Exception):
        pass
    vol_module.Invalid = Invalid
    monkeypatch.setitem(sys.modules, "voluptuous", vol_module)

    ha_module = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    class ConfigEntry:
        pass
    config_entries.ConfigEntry = ConfigEntry
    ha_module.config_entries = config_entries

    const_module = types.ModuleType("homeassistant.const")
    class Platform:
        SENSOR = "sensor"
        BUTTON = "button"
    const_module.Platform = Platform

    core = types.ModuleType("homeassistant.core")
    class HomeAssistant:
        pass
    class ServiceCall:
        pass
    def callback(func):
        return func
    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall
    core.callback = callback

    helpers = types.ModuleType("homeassistant.helpers")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    def async_get(hass):
        return object()
    entity_registry.async_get = async_get
    helpers.entity_registry = entity_registry

    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)
    monkeypatch.setitem(sys.modules, "homeassistant.const", const_module)
    monkeypatch.setitem(sys.modules, "homeassistant.core", core)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers", helpers)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity_registry", entity_registry)

    pkg = importlib.import_module("consumable_expiration")
    assert pkg is not None
