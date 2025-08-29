import asyncio
import importlib
import sys
import types
import datetime as dt
from pathlib import Path


def test_config_flow_form_and_entry(monkeypatch):
    """Ensure the config flow shows a form and creates an entry."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

    vol_module = types.ModuleType("voluptuous")

    class Schema:
        def __init__(self, schema):
            self.schema = schema

        def __call__(self, data):
            return data

    vol_module.Schema = Schema
    def _identity(key, default=None):
        return key

    vol_module.Required = _identity
    vol_module.Optional = _identity
    monkeypatch.setitem(sys.modules, "voluptuous", vol_module)
    import voluptuous as vol  # noqa: F401

    ha_module = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    core = types.ModuleType("homeassistant.core")
    data_entry_flow = types.ModuleType("homeassistant.data_entry_flow")
    helpers = types.ModuleType("homeassistant.helpers")
    selector = types.ModuleType("homeassistant.helpers.selector")
    const_module = types.ModuleType("homeassistant.const")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    config_validation = types.ModuleType("homeassistant.helpers.config_validation")
    def _cv_identity(value):
        return value
    config_validation.entity_id = _cv_identity
    config_validation.date = _cv_identity

    class ConfigEntry:
        pass

    config_entries.ConfigEntry = ConfigEntry

    class BaseFlow:
        def async_create_entry(self, title, data, options=None):
            return {"type": "create_entry", "title": title, "data": data, "options": options}

        def async_show_form(self, step_id, data_schema, errors=None):
            return {"type": "form", "step_id": step_id, "data_schema": data_schema, "errors": errors}

    class OptionsFlow(BaseFlow):
        pass

    config_entries.OptionsFlow = OptionsFlow

    class DummyConfigFlow(BaseFlow):
        def __init_subclass__(cls, **kwargs):
            pass

    config_entries.ConfigFlow = DummyConfigFlow
    ha_module.config_entries = config_entries

    class FlowResult(dict):
        pass

    data_entry_flow.FlowResult = FlowResult

    class HomeAssistant:
        pass

    def callback(func):
        return func

    class ServiceCall:
        pass

    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall
    core.callback = callback
    ha_module.core = core

    class TextSelector:
        pass

    class SelectSelectorConfig:
        def __init__(self, options=None, mode=None):
            self.options = options
            self.mode = mode

    class SelectSelectorMode:
        DROPDOWN = "dropdown"

    class SelectSelector:
        def __init__(self, config):
            self.config = config

    class IconSelector:
        def __init__(self, *args, **kwargs):
            pass

    class NumberSelectorConfig:
        def __init__(self, min=None, max=None, step=None, mode=None):
            self.min = min
            self.max = max
            self.step = step
            self.mode = mode

    class NumberSelectorMode:
        BOX = "box"

    class NumberSelector:
        def __init__(self, config):
            self.config = config

    class DateSelector:
        def __init__(self, *args, **kwargs):
            pass

    selector.TextSelector = TextSelector
    selector.SelectSelector = SelectSelector
    selector.SelectSelectorConfig = SelectSelectorConfig
    selector.SelectSelectorMode = SelectSelectorMode
    selector.IconSelector = IconSelector
    selector.NumberSelector = NumberSelector
    selector.NumberSelectorConfig = NumberSelectorConfig
    selector.NumberSelectorMode = NumberSelectorMode
    selector.DateSelector = DateSelector

    class Platform:
        SENSOR = "sensor"
        BUTTON = "button"

    const_module.Platform = Platform

    def async_get(hass):
        return object()

    entity_registry.async_get = async_get
    helpers.selector = selector
    helpers.entity_registry = entity_registry
    helpers.config_validation = config_validation
    ha_module.helpers = helpers

    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)
    monkeypatch.setitem(sys.modules, "homeassistant.core", core)
    monkeypatch.setitem(sys.modules, "homeassistant.data_entry_flow", data_entry_flow)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers", helpers)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.selector", selector)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity_registry", entity_registry)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.config_validation", config_validation)
    monkeypatch.setitem(sys.modules, "homeassistant.const", const_module)

    cf_module = importlib.import_module("consumable_expiration.config_flow")
    flow = cf_module.ConsumableConfigFlow()

    # Initial call should show the form
    result = asyncio.run(flow.async_step_user())
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    user_input = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: dt.date(2024, 1, 1),
    }
    result = asyncio.run(flow.async_step_user(user_input=user_input))
    assert result["type"] == "create_entry"
    assert result["title"] == "Filter"
    assert result["data"][cf_module.CONF_NAME] == "Filter"
    assert result["options"][cf_module.CONF_DURATION_DAYS] == 30
    assert result["options"][cf_module.CONF_START_DATE] == "2024-01-01"

    flow2 = cf_module.ConsumableConfigFlow()
    asyncio.run(flow2.async_step_user())
    user_input2 = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
        cf_module.CONF_EXPIRY_DATE_OVERRIDE: "2024-02-01",
    }
    result2 = asyncio.run(flow2.async_step_user(user_input=user_input2))
    assert result2["options"][cf_module.CONF_START_DATE] == "2024-01-02"

    # Test options flow handles expiry override strings
    config_entry = cf_module.config_entries.ConfigEntry()
    config_entry.data = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_ITEM_TYPE: None,
        cf_module.CONF_ICON: None,
    }
    config_entry.options = {
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
    }

    options_flow = cf_module.ConsumableConfigFlow.async_get_options_flow(config_entry)

    class DummyConfigEntries:
        def async_update_entry(self, entry, data=None):
            entry.data = data or entry.data

    hass = core.HomeAssistant()
    hass.config_entries = DummyConfigEntries()
    options_flow.hass = hass

    asyncio.run(options_flow.async_step_init())
    user_input3 = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
        cf_module.CONF_EXPIRY_DATE_OVERRIDE: "2024-02-01",
    }
    result3 = asyncio.run(options_flow.async_step_init(user_input=user_input3))
    assert result3["data"][cf_module.CONF_START_DATE] == "2024-01-02"

    # Changing start date should ignore default expiry override
    config_entry_change = cf_module.config_entries.ConfigEntry()
    config_entry_change.data = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_ITEM_TYPE: None,
        cf_module.CONF_ICON: None,
    }
    config_entry_change.options = {
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
    }
    options_flow_change = cf_module.ConsumableConfigFlow.async_get_options_flow(
        config_entry_change
    )
    options_flow_change.hass = hass
    asyncio.run(options_flow_change.async_step_init())
    user_input_change = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-15",
        cf_module.CONF_EXPIRY_DATE_OVERRIDE: "2024-01-31",
    }
    result_change = asyncio.run(
        options_flow_change.async_step_init(user_input=user_input_change)
    )
    assert result_change["data"][cf_module.CONF_START_DATE] == "2024-01-15"

    # Partial update should not require all fields
    config_entry_partial = cf_module.config_entries.ConfigEntry()
    config_entry_partial.data = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_ITEM_TYPE: None,
        cf_module.CONF_ICON: None,
    }
    config_entry_partial.options = {
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
    }
    options_flow_partial = cf_module.ConsumableConfigFlow.async_get_options_flow(config_entry_partial)
    options_flow_partial.hass = hass
    asyncio.run(options_flow_partial.async_step_init())
    user_partial = {
        cf_module.CONF_NAME: "Updated",
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
    }
    result_partial = asyncio.run(options_flow_partial.async_step_init(user_input=user_partial))
    assert result_partial["data"][cf_module.CONF_START_DATE] == "2024-01-01"
    assert config_entry_partial.data[cf_module.CONF_NAME] == "Updated"

    # None values should preserve existing fields
    config_entry_none = cf_module.config_entries.ConfigEntry()
    config_entry_none.data = {
        cf_module.CONF_NAME: "Filter",
        cf_module.CONF_ITEM_TYPE: "typeA",
        cf_module.CONF_ICON: "mdi:filter",
    }
    config_entry_none.options = {
        cf_module.CONF_DURATION_DAYS: 30,
        cf_module.CONF_START_DATE: "2024-01-01",
    }
    options_flow_none = cf_module.ConsumableConfigFlow.async_get_options_flow(config_entry_none)
    options_flow_none.hass = hass
    asyncio.run(options_flow_none.async_step_init())
    user_none = {
        cf_module.CONF_NAME: "Updated",
        cf_module.CONF_ITEM_TYPE: None,
        cf_module.CONF_ICON: None,
        cf_module.CONF_DURATION_DAYS: None,
        cf_module.CONF_START_DATE: None,
    }
    result_none = asyncio.run(options_flow_none.async_step_init(user_input=user_none))
    assert config_entry_none.data[cf_module.CONF_ITEM_TYPE] == "typeA"
    assert config_entry_none.data[cf_module.CONF_ICON] == "mdi:filter"
    assert result_none["data"][cf_module.CONF_START_DATE] == "2024-01-01"

    # Test reconfigure flow delegates to options flow
    config_entry2 = cf_module.config_entries.ConfigEntry()
    config_entry2.entry_id = "abc123"
    config_entry2.data = {
        cf_module.CONF_NAME: "Old", 
        cf_module.CONF_ITEM_TYPE: None,
        cf_module.CONF_ICON: None,
    }
    config_entry2.options = {
        cf_module.CONF_DURATION_DAYS: 10,
        cf_module.CONF_START_DATE: "2024-01-01",
    }

    class DummyConfigEntries2:
        def __init__(self, entry):
            self._entry = entry

        def async_get_entry(self, entry_id):
            return self._entry

        def async_update_entry(self, entry, data=None):
            entry.data = data or entry.data

    hass2 = core.HomeAssistant()
    hass2.config_entries = DummyConfigEntries2(config_entry2)

    flow3 = cf_module.ConsumableConfigFlow()
    flow3.hass = hass2
    flow3.context = {"entry_id": "abc123"}

    result4 = asyncio.run(flow3.async_step_reconfigure())
    assert result4["type"] == "form"

    user_input4 = {
        cf_module.CONF_NAME: "New",
        cf_module.CONF_DURATION_DAYS: 20,
        cf_module.CONF_START_DATE: dt.date(2024, 1, 1),
    }
    result5 = asyncio.run(flow3.async_step_reconfigure(user_input=user_input4))
    assert result5["type"] == "create_entry"
    assert config_entry2.data[cf_module.CONF_NAME] == "New"
    assert result5["data"][cf_module.CONF_DURATION_DAYS] == 20
