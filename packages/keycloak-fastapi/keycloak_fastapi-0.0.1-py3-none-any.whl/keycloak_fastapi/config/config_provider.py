# external_lib/config_provider.py
_config = None

def set_config(config):
    global _config
    _config = config

def get_config():
    if _config is None:
        raise RuntimeError("Settings not initialized")
    return _config
