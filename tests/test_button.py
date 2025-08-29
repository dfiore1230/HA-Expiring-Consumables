
import sys
import types
from pathlib import Path

def test_button_default_state(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    ha_module = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    button_module = types.ModuleType("homeassistant.components.button")

    class ButtonEntity:
        def __init__(self):
            self._attr_state = None
        def async_write_ha_state(self):
            pass
    button_module.ButtonEntity = ButtonEntity
    components.button = button_module
    ha_module.components = components

    config_entries = types.ModuleType("homeassistant.config_entries")
    class ConfigEntry:
        def __init__(self):
            self.entry_id = "1"
            self.data = {}
            self.options = {}
    config_entries.ConfigEntry = ConfigEntry

    core = types.ModuleType("homeassistant.core")
    class HomeAssistant:
        def __init__(self):
            self.config_entries = types.SimpleNamespace(async_update_entry=lambda *args, **kwargs: None)
    core.HomeAssistant = HomeAssistant

    helpers = types.ModuleType("homeassistant.helpers")
    entity = types.ModuleType("homeassistant.helpers.entity")
    class DeviceInfo:
        def __init__(self, **kwargs):
            pass
    entity.DeviceInfo = DeviceInfo
    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = object
    helpers.entity = entity
    helpers.entity_platform = entity_platform

    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.components", components)
    monkeypatch.setitem(sys.modules, "homeassistant.components.button", button_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)
    monkeypatch.setitem(sys.modules, "homeassistant.core", core)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers", helpers)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity", entity)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity_platform", entity_platform)

    from consumable_expiration.button import MarkReplacedButton, CONF_NAME

    hass = core.HomeAssistant()
    entry = config_entries.ConfigEntry()
    entry.data = {CONF_NAME: "Test"}

    button = MarkReplacedButton(hass, entry)

    assert button.state == "idle"
