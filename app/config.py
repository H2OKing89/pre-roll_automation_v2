# app/config.py

import os
import yaml
from dotenv import load_dotenv
import logging
from pathlib import Path
from app.validation import validate_date, validate_holiday_fields, check_overlap, validate_pre_roll_files
import pytz
from datetime import datetime

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
        Loads and validates the YAML configuration file.

        Returns:
            dict: Validated configuration data.
        """
        try:
            with open(cls.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Validate Plex Configuration
            plex = config.get('plex', {})
            if not plex.get('token') or not plex.get('host'):
                logging.error("Plex configuration is incomplete. 'token' and 'host' are required.")
                raise ValueError("Invalid Plex configuration.")

            # Validate Timezone
            timezone = config.get('timezone')
            try:
                datetime.now(pytz.timezone(timezone))
            except Exception:
                logging.error(f"Invalid timezone specified: {timezone}")
                raise ValueError("Invalid timezone.")

            # Determine Environment
            environment = os.getenv('ENV', 'production').lower()

            # Validate Directories - Skip if developing locally
            directories = config.get('directories', {})
            base_pre_roll_dir = directories.get('base_pre_roll_dir')
            if environment != 'development':
                if not base_pre_roll_dir or not os.path.isdir(base_pre_roll_dir):
                    logging.error(f"Invalid or non-existent base_pre_roll_dir: {base_pre_roll_dir}")
                    raise ValueError("Invalid directories configuration.")
            else:
                logging.info("Running in development mode. Skipping directory validation.")

            # Validate Holidays
            holidays = config.get('holidays', [])
            validated_holidays = []
            for holiday in holidays:
                if not validate_holiday_fields(holiday):
                    logging.error(f"Skipping holiday '{holiday.get('name', 'Unknown')}' due to missing fields.")
                    continue

                # Validate dates
                try:
                    start_month, start_day = map(int, holiday['start_date'].split('-'))
                    end_month, end_day = map(int, holiday['end_date'].split('-'))
                except ValueError:
                    logging.error(f"Invalid date format in holiday '{holiday['name']}'. Expected MM-DD.")
                    continue

                if not validate_date(start_month, start_day):
                    logging.error(f"Invalid start date '{holiday['start_date']}' in holiday '{holiday['name']}'.")
                    continue

                if not validate_date(end_month, end_day):
                    logging.error(f"Invalid end date '{holiday['end_date']}' in holiday '{holiday['name']}'.")
                    continue

                # Check for overlapping holidays
                if check_overlap(holiday, validated_holidays, timezone):
                    logging.error(f"Skipping holiday '{holiday['name']}' due to overlap.")
                    continue

                # Validate pre-roll files - Skip in development
                if environment != 'development':
                    if not validate_pre_roll_files(holiday['pre_rolls'], base_pre_roll_dir):
                        logging.error(f"Skipping holiday '{holiday['name']}' due to missing pre-roll files.")
                        continue
                else:
                    logging.info(f"Running in development mode. Skipping pre-roll file validation for holiday '{holiday['name']}'.")

                validated_holidays.append(holiday)
                logging.info(f"Holiday '{holiday['name']}' validated successfully.")

            config['holidays'] = validated_holidays
            logging.info("Configuration validation completed.")
            return config
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            raise
        except FileNotFoundError:
            logging.error(f"Configuration file not found at path: {cls.config_path}")
            raise
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
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
Config.PLEX_TOKEN = os.getenv('PLEX_TOKEN')
Config.PLEX_HOST = os.getenv('PLEX_HOST')

# Load and validate configuration
Config.yaml_config = Config.load_config()

Config.TIMEZONE = Config.yaml_config.get('timezone', 'UTC')
Config.DIRECTORIES = Config.yaml_config.get('directories', {})
Config.BASE_PRE_ROLL_DIR = Config.DIRECTORIES.get('base_pre_roll_dir', '')
Config.SCHEDULE = Config.yaml_config.get('schedule', {})
Config.HOLIDAYS = Config.yaml_config.get('holidays', [])
