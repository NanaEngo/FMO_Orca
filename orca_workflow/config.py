import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    'method': 'wB97X-3c',
    'solvent': 'Toluene',
    'nprocs': 4,
    'nroots': 3,
    'triplets': True,
    'force_field': 'MMFF94',
    'maxcore': 7000,
    'auto_memory': True,
    'max_mem_limit': 8000
}

def load_config(config_path=None):
    """
    Load configuration from YAML file or use defaults.
    """
    config = DEFAULT_CONFIG.copy()
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                config.update(user_config)
    return config
