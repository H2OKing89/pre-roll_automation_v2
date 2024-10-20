# app/config.py

import os
import yaml
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class that loads settings from a YAML file and environment variables.
    """

    # Path to config.yaml
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'

    @classmethod
    def load_config(cls):
        """
        Loads the YAML configuration file.

        Returns:
            dict: Configuration data.
        """
        try:
            with open(cls.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logging.error(f"Failed to load config.yaml: {e}")
            raise

    @classmethod
    def save_config(cls, config_data):
        """
        Saves the configuration data back to the YAML file.

        Args:
            config_data (dict): Configuration data to save.
        """
        try:
            with open(cls.config_path, 'w') as f:
                yaml.safe_dump(config_data, f)
            logging.info("Configuration saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save config.yaml: {e}")
            raise

# === Initialization outside the class ===

# Load configurations at runtime
yaml_config = Config.load_config()
Config.PLEX_TOKEN = os.getenv('PLEX_TOKEN')
Config.PLEX_HOST = os.getenv('PLEX_HOST')
Config.TIMEZONE = yaml_config.get('timezone', 'UTC')
Config.DIRECTORIES = yaml_config.get('directories', {})
Config.BASE_PRE_ROLL_DIR = Config.DIRECTORIES.get('base_pre_roll_dir', '')
Config.SCHEDULE = yaml_config.get('schedule', {})
Config.HOLIDAYS = yaml_config.get('holidays', [])

