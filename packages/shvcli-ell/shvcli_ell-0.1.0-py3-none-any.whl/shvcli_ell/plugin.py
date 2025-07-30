"""The top level loaded for the plugin."""

import importlib

importlib.import_module(".timesync", __package__)
importlib.import_module(".timezone", __package__)
