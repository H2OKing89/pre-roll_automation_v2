# app/utils.py

"""
Utility functions for the Plex Pre-Roll Automation application.

Includes functions to determine current holidays, select appropriate pre-rolls,
and interact with the Plex API to update pre-roll settings.
"""

import random
import os
import logging
import requests
import xml.etree.ElementTree as ET  # Import ElementTree for XML parsing
from app.config import Config
from app.validation import validate_holiday_fields, validate_date, check_overlap, validate_pre_roll_files
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_validated_holidays():
    """
    Returns the list of validated holidays from the configuration.
    """
    return Config.HOLIDAYS

def get_current_holiday(valid_holidays):
    """
    Determines the current holiday based on the validated holidays and current date.

    Args:
        valid_holidays (list): List of validated holiday dictionaries.

    Returns:
        dict or None: The current holiday dictionary if within a holiday period, else None.
    """
    try:
        now = datetime.now(pytz.timezone(Config.TIMEZONE))
        current_year = now.year

        for holiday in valid_holidays:
            # Parse start and end dates from the configuration
            start_month, start_day = map(int, holiday['start_date'].split('-'))
            end_month, end_day = map(int, holiday['end_date'].split('-'))

            # Create datetime objects for start and end dates
            start_date = datetime(current_year, start_month, start_day, tzinfo=pytz.timezone(Config.TIMEZONE))
            end_date = datetime(current_year, end_month, end_day, tzinfo=pytz.timezone(Config.TIMEZONE))

            # Adjust for holidays that span over the year-end
            if end_date < start_date:
                end_date += relativedelta(years=1)

            # Check if current time falls within the holiday period
            if start_date <= now <= end_date:
                logging.info(f"Current holiday detected: {holiday['name']}")
                return holiday

        logging.info("No active holiday detected.")
        return None
    except Exception as e:
        logging.error(f"Error determining current holiday: {e}")
        return None

def select_pre_roll(holiday):
    """
    Selects pre-roll videos based on the holiday's selection mode.

    Args:
        holiday (dict): The holiday configuration.

    Returns:
        str or None: The formatted pre-roll path(s) for Plex, separated by commas or semi-colons.
    """
    try:
        pre_rolls = holiday.get('pre_rolls', [])
        if not pre_rolls:
            logging.warning(f"No pre-rolls available for holiday: {holiday['name']}")
            return None

        selection_mode = holiday.get('selection_mode', 'random')

        if selection_mode == 'random':
            # Format paths with semi-colons for random selection
            formatted_pre_rolls = ';'.join([
                os.path.join(Config.BASE_PRE_ROLL_DIR, pre_roll).replace("\\", "/") for pre_roll in pre_rolls
            ])
            logging.info(f"Random selection mode: {formatted_pre_rolls}")
            return formatted_pre_rolls
        elif selection_mode == 'sequential':
            # Format paths with commas for sequential play
            formatted_pre_rolls = ','.join([
                os.path.join(Config.BASE_PRE_ROLL_DIR, pre_roll).replace("\\", "/") for pre_roll in pre_rolls
            ])
            logging.info(f"Sequential selection mode: {formatted_pre_rolls}")
            return formatted_pre_rolls
        else:
            # Default to random selection if mode is unrecognized
            formatted_pre_rolls = ';'.join([
                os.path.join(Config.BASE_PRE_ROLL_DIR, pre_roll).replace("\\", "/") for pre_roll in pre_rolls
            ])
            logging.warning(f"Unrecognized selection mode '{selection_mode}'. Defaulting to random selection: {formatted_pre_rolls}")
            return formatted_pre_rolls

    except Exception as e:
        logging.error(f"Error selecting pre-roll for holiday {holiday['name']}: {e}")
        return None

def get_session_with_retries():
    """
    Creates a requests Session with retry logic for robust API communication.

    Returns:
        requests.Session: Configured session with retries.
    """
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "PUT"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def update_plex_pre_roll(pre_roll_path):
    """
    Updates the Plex server's pre-roll setting with the selected video(s) using the Plex API.

    Args:
        pre_roll_path (str): The formatted path(s) to the selected pre-roll video(s).
    """
    try:
        # Ensure the path uses forward slashes
        normalized_pre_roll_path = pre_roll_path.replace("\\", "/")

        # Construct the API URL based on the Plex settings
        plex_url = f"{Config.PLEX_HOST}/:/prefs"
        params = {
            "CinemaTrailersPrerollID": normalized_pre_roll_path,
            "X-Plex-Token": Config.PLEX_TOKEN
        }

        # Create a session with retries
        session = get_session_with_retries()

        # Send the PUT request to update the pre-roll with a timeout
        response = session.put(plex_url, params=params, timeout=10)  # 10-second timeout

        # Check if the response was successful
        if response.status_code == 200:
            logging.info(f"Pre-roll update request sent successfully for: {normalized_pre_roll_path}")

            # Verification step: Check if the pre-roll was updated correctly
            verify_plex_pre_roll(normalized_pre_roll_path)
        elif response.status_code == 401:
            logging.error("Authentication failed. Check your Plex token.")
        elif response.status_code == 404:
            logging.error("Plex API endpoint not found. Check the host URL.")
        else:
            logging.error(f"Failed to update Plex pre-roll. Status Code: {response.status_code}. Response: {response.text}")

    except requests.exceptions.Timeout:
        logging.error("Request timed out while updating Plex pre-roll.")
    except requests.exceptions.ConnectionError:
        logging.error("Connection error occurred while updating Plex pre-roll.")
    except Exception as e:
        logging.error(f"Exception occurred while updating Plex pre-roll: {e}")

def verify_plex_pre_roll(expected_pre_roll):
    """
    Verifies that the Plex server has successfully updated the pre-roll setting.

    Args:
        expected_pre_roll (str): The expected pre-roll video path(s), formatted with commas or semi-colons.
    """
    try:
        # Construct the API URL to get Plex preferences
        plex_url = f"{Config.PLEX_HOST}/:/prefs"
        params = {
            "X-Plex-Token": Config.PLEX_TOKEN
        }

        # Create a session with retries
        session = get_session_with_retries()

        # Send a GET request to retrieve Plex preferences with a timeout
        response = session.get(plex_url, params=params, timeout=10)

        # Check if the response was successful
        if response.status_code == 200:
            # Parse the XML response
            root = ET.fromstring(response.content)

            # Initialize variable to store the current pre-roll path(s)
            current_pre_roll = None

            # Iterate through all Setting elements to find CinemaTrailersPrerollID
            for setting in root.findall('.//Setting'):
                if setting.get('id') == 'CinemaTrailersPrerollID':
                    current_pre_roll = setting.get('value')
                    break

            if current_pre_roll is not None:
                # Normalize paths for comparison (handle backslashes and forward slashes)
                normalized_expected = expected_pre_roll.replace("\\", "/")
                normalized_current = current_pre_roll.replace("\\", "/")

                # Compare the expected and current pre-roll paths
                if normalized_current == normalized_expected:
                    logging.info(f"Pre-roll update verified successfully: {current_pre_roll}")
                else:
                    logging.error(f"Pre-roll update verification failed. Expected: {normalized_expected}, but got: {normalized_current}")
            else:
                logging.error("CinemaTrailersPrerollID setting not found in Plex response.")
        else:
            logging.error(f"Failed to retrieve Plex preferences. Status Code: {response.status_code}. Response: {response.text}")

    except ET.ParseError as pe:
        logging.error(f"XML parsing error while verifying Plex pre-roll: {pe}")
    except requests.exceptions.Timeout:
        logging.error("Request timed out while verifying Plex pre-roll.")
    except requests.exceptions.ConnectionError:
        logging.error("Connection error occurred while verifying Plex pre-roll.")
    except Exception as e:
        logging.error(f"Exception occurred while verifying Plex pre-roll: {e}")

def trigger_pre_roll_update(valid_holidays):
    """
    Triggers the pre-roll update process.

    Args:
        valid_holidays (list): List of validated holiday dictionaries.
    """
    try:
        logging.info("Triggering pre-roll update...")
        # Determine the current holiday
        holiday = get_current_holiday(valid_holidays)
        if holiday:
            # Select the appropriate pre-roll video(s)
            pre_roll = select_pre_roll(holiday)
            if pre_roll:
                # Update Plex with the selected pre-roll video(s)
                update_plex_pre_roll(pre_roll)
            else:
                logging.error("No pre-roll selected for the current holiday.")
        else:
            logging.info("No active holiday found. No pre-roll update performed.")
    except Exception as e:
        logging.error(f"Exception occurred while triggering pre-roll update: {e}")
