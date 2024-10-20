# app/config.py

import os
import yaml
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Load YAML configuration
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    # Load settings
    PLEX_TOKEN = os.getenv('PLEX_TOKEN')
    PLEX_HOST = os.getenv('PLEX_HOST')
    TIMEZONE = yaml_config.get('timezone', 'UTC')
    DIRECTORIES = yaml_config.get('directories', {})
    BASE_PRE_ROLL_DIR = DIRECTORIES.get('base_pre_roll_dir', '')
    SCHEDULE = yaml_config.get('schedule', {})
    HOLIDAYS = yaml_config.get('holidays', [])

    @staticmethod
    def save_config():
        with open(Config.config_path, 'w') as f:
            yaml.safe_dump(Config.yaml_config, f)
