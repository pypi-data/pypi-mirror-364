# eops/utils/config_loader.py
import importlib.util
from pathlib import Path
from typing import Dict, Any

def _deep_merge_dicts(base: dict, new: dict) -> dict:
    """Recursively merges new dict into base dict."""
    for k, v in new.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            base[k] = _deep_merge_dicts(base[k], v)
        else:
            base[k] = v
    return base

def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """
    Dynamically loads a Python configuration file as a module and converts it to a dictionary.
    It only loads uppercase variables.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    spec = importlib.util.spec_from_file_location(name="eops_config", location=str(config_path))
    if spec is None:
        raise ImportError(f"Could not load spec for module at {config_path}")
    
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    config_dict = {
        key: getattr(config_module, key)
        for key in dir(config_module)
        if key.isupper() and not key.startswith("__")
    }
    
    if "MODE" not in config_dict:
        raise AttributeError("Missing required configuration variable 'MODE' in the config file.")
    if "STRATEGY_CLASS" not in config_dict:
        raise AttributeError("Missing required configuration variable 'STRATEGY_CLASS' in the config file.")
        
    return config_dict

def build_final_config(
    base_config_path: Path, 
    overrides: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Loads a base config from a file and merges override parameters into it.
    """
    # First, ensure the root of the project is in the path
    # so the config file can import its own modules
    import sys
    project_root = base_config_path.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    base_config = load_config_from_file(base_config_path)

    # Deep merge overrides into the base config
    # This allows overriding nested dicts like STRATEGY_PARAMS
    final_config = _deep_merge_dicts(base_config, overrides)
    
    # Ensure critical keys are still present
    if "STRATEGY_CLASS" not in final_config:
        raise ValueError("Final config is missing 'STRATEGY_CLASS'.")
    if "MODE" not in final_config:
        raise ValueError("Final config is missing 'MODE'.")

    return final_config