from pathlib import Path
import importlib
import sys


def test_import_version():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    pkg = importlib.import_module("ha_expiring_consumables")
    assert pkg.__version__
