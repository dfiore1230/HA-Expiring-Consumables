import sys
import types
import datetime as dt
from pathlib import Path


def _setup_modules(monkeypatch):
    package = types.ModuleType("consumable_expiration")
    package.__path__ = [
        str(Path(__file__).resolve().parents[1] / "custom_components" / "consumable_expiration")
    ]
    monkeypatch.setitem(sys.modules, "consumable_expiration", package)
    sys.modules.pop("consumable_expiration.__init__", None)

    vol_module = types.ModuleType("voluptuous")
    class Schema:
        def __init__(self, schema):
            self.schema = schema
        def __call__(self, data):
            return data
    vol_module.Schema = Schema
    vol_module.Required = lambda key, default=None: key
    vol_module.Optional = lambda key, default=None: key
    vol_module.All = lambda *args, **kwargs: (lambda v: v)
    vol_module.Coerce = lambda t: (lambda v: v)
    vol_module.Range = lambda *args, **kwargs: (lambda v: v)
    monkeypatch.setitem(sys.modules, "voluptuous", vol_module)

    cv_module = types.ModuleType("homeassistant.helpers.config_validation")
    cv_module.entity_id = lambda v: v
    cv_module.date = lambda v: v
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.config_validation", cv_module)

    const_module = types.ModuleType("homeassistant.const")
    class Platform:
        SENSOR = "sensor"
        BUTTON = "button"
    const_module.Platform = Platform
    monkeypatch.setitem(sys.modules, "homeassistant.const", const_module)

    ha_module = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    class ConfigEntry:
        pass
    config_entries.ConfigEntry = ConfigEntry

    core = types.ModuleType("homeassistant.core")
    class HomeAssistant:
        def __init__(self):
            self.config_entries = None
    class ServiceCall:
        def __init__(self, data=None):
            self.data = data or {}
    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall

    helpers = types.ModuleType("homeassistant.helpers")
    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    def async_get(hass):
        return types.SimpleNamespace(async_get=lambda entity_id: None)
    entity_registry.async_get = async_get
    helpers.entity_registry = entity_registry

    ha_module.config_entries = config_entries
    ha_module.core = core
    ha_module.helpers = helpers

    monkeypatch.setitem(sys.modules, "homeassistant", ha_module)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)
    monkeypatch.setitem(sys.modules, "homeassistant.core", core)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers", helpers)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity_registry", entity_registry)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.config_validation", cv_module)
    monkeypatch.setitem(sys.modules, "homeassistant.const", const_module)


def test_set_expiry_date_updates_start(monkeypatch):
    _setup_modules(monkeypatch)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))
    import importlib
    init = importlib.import_module("consumable_expiration.__init__")
    const = importlib.import_module("consumable_expiration.const")
    DOMAIN = const.DOMAIN
    CONF_DURATION_DAYS = const.CONF_DURATION_DAYS
    CONF_START_DATE = const.CONF_START_DATE

    class ConfigEntry:
        def __init__(self):
            self.entry_id = "123"
            self.data = {}
            self.options = {CONF_DURATION_DAYS: 30, CONF_START_DATE: "2024-01-01"}

    class ConfigEntries:
        def __init__(self, entry):
            self._entry = entry
        def async_get_entry(self, entry_id):
            return self._entry
        def async_update_entry(self, entry, options=None, data=None):
            entry.options = options

    entry = ConfigEntry()
    hass = types.SimpleNamespace(
        data={DOMAIN: {"entity_map": {"sensor.test": entry.entry_id}}},
        config_entries=ConfigEntries(entry),
    )

    services = {}
    class Services:
        def async_register(self, domain, name, handler, schema=None):
            services[name] = handler
    hass.services = Services()

    init._register_services(hass)

    class Call:
        def __init__(self, data):
            self.data = data

    expiry = dt.date(2024, 2, 10)
    call = Call({"entity_id": "sensor.test", "expiry_date": expiry})

    import asyncio
    asyncio.run(services["set_expiry_date"](call))

    assert entry.options[CONF_START_DATE] == "2024-01-11"
    assert entry.options[CONF_DURATION_DAYS] == 30
