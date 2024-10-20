# app/utils.py

"""
Utility functions for the Plex Pre-Roll Automation application.

Includes functions to determine current holidays, select appropriate pre-rolls,
and interact with the Plex API to update pre-roll settings.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from app.config import Config
import random
import os
import logging
import requests
import xml.etree.ElementTree as ET  # Import ElementTree for XML parsing

def get_current_holiday():
    """
    Determines the current holiday based on the configuration and current date.

    Returns:
        dict or None: The current holiday dictionary if within a holiday period, else None.
    """
    try:
        # Get the current time in the configured timezone
        now = datetime.now(pytz.timezone(Config.TIMEZONE))
        current_year = now.year

        for holiday in Config.HOLIDAYS:
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

        # Send the PUT request to update the pre-roll
        response = requests.put(plex_url, params=params)

        # Check if the response was successful
        if response.status_code == 200:
            logging.info(f"Pre-roll update request sent successfully for: {normalized_pre_roll_path}")
            
            # Verification step: Check if the pre-roll was updated correctly
            verify_plex_pre_roll(normalized_pre_roll_path)
        else:
            logging.error(f"Failed to update Plex pre-roll. Status Code: {response.status_code}. Response: {response.text}")

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

        # Send a GET request to retrieve Plex preferences
        response = requests.get(plex_url, params=params)

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
    except Exception as e:
        logging.error(f"Exception occurred while verifying Plex pre-roll: {e}")

def trigger_pre_roll_update():
    """
    Triggers the pre-roll update process.

    This function is called by the scheduler or API endpoint to initiate the pre-roll update.
    """
    try:
        logging.info("Triggering pre-roll update...")
        # Determine the current holiday
        holiday = get_current_holiday()
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
