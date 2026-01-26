"""
Configuration loader for semantic visualization paradigm.

Loads configuration from experiment_config.py with proper path handling.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load experiment configuration.
    
    Parameters
    ----------
    config_file : str, optional
        Path to config file (default: config/experiment_config.py)
    
    Returns
    -------
    dict
        Configuration dictionary
    """
    if config_file is None:
        # Default to config/experiment_config.py relative to this file
        config_dir = Path(__file__).parent
        config_file = config_dir / 'experiment_config.py'
    else:
        config_file = Path(config_file)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    # Add config directory to path temporarily
    config_dir = config_file.parent
    sys.path.insert(0, str(config_dir))
    
    try:
        # Import config module
        import experiment_config as config_module
        
        # Extract all configuration variables
        config = {}
        for attr in dir(config_module):
            if not attr.startswith('_'):
                value = getattr(config_module, attr)
                if not callable(value):
                    config[attr] = value
        
        return config
    finally:
        # Remove from path
        if str(config_dir) in sys.path:
            sys.path.remove(str(config_dir))


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get configuration value with optional default.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary
    key : str
        Configuration key
    default : any
        Default value if key not found
    
    Returns
    -------
    any
        Configuration value or default
    """
    return config.get(key, default)
