# app/validation.py

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import os

def validate_date(month, day):
    """
    Validates that the given month and day form a valid date.
    
    Args:
        month (int): The month of the date.
        day (int): The day of the date.
    
    Returns:
        bool: True if the date is valid, False otherwise.
    """
    try:
        # Using the current year for validation
        datetime(year=datetime.now().year, month=month, day=day)
        return True
    except ValueError:
        return False

def validate_holiday_fields(holiday):
    """
    Validates that all required fields are present in the holiday configuration.
    
    Args:
        holiday (dict): The holiday configuration.
    
    Returns:
        bool: True if all required fields are present, False otherwise.
    """
    required_fields = ['name', 'start_date', 'end_date', 'pre_rolls', 'selection_mode']
    for field in required_fields:
        if field not in holiday:
            logging.error(f"Missing required field '{field}' in holiday configuration.")
            return False
    return True

def check_overlap(new_holiday, existing_holidays, timezone):
    """
    Checks if the new_holiday overlaps with any of the existing_holidays.
    
    Args:
        new_holiday (dict): The holiday to check.
        existing_holidays (list): List of already validated holidays.
        timezone (str): Timezone string.
    
    Returns:
        bool: True if there is an overlap, False otherwise.
    """
    tz = pytz.timezone(timezone)
    new_start_month, new_start_day = map(int, new_holiday['start_date'].split('-'))
    new_end_month, new_end_day = map(int, new_holiday['end_date'].split('-'))
    
    try:
        current_year = datetime.now(tz).year
        new_start_date = datetime(current_year, new_start_month, new_start_day, tzinfo=tz)
        new_end_date = datetime(current_year, new_end_month, new_end_day, tzinfo=tz)
        
        # Adjust for holidays that span over the year-end
        if new_end_date < new_start_date:
            new_end_date += relativedelta(years=1)
    except ValueError:
        logging.error(f"Invalid date range for holiday: {new_holiday['name']}")
        return True  # Treat invalid dates as overlapping to prevent addition
    
    for holiday in existing_holidays:
        other_start_month, other_start_day = map(int, holiday['start_date'].split('-'))
        other_end_month, other_end_day = map(int, holiday['end_date'].split('-'))
        
        try:
            other_start_date = datetime(current_year, other_start_month, other_start_day, tzinfo=tz)
            other_end_date = datetime(current_year, other_end_month, other_end_day, tzinfo=tz)
            
            if other_end_date < other_start_date:
                other_end_date += relativedelta(years=1)
        except ValueError:
            logging.error(f"Invalid date range for holiday: {holiday['name']}")
            continue  # Skip invalid existing holidays
        
        # Check for overlap
        if (new_start_date <= other_end_date) and (new_end_date >= other_start_date):
            logging.error(f"Holiday '{new_holiday['name']}' overlaps with existing holiday '{holiday['name']}'.")
            return True
    
    return False

def validate_pre_roll_files(pre_rolls, base_dir):
    """
    Validates that all pre-roll files exist.
    
    Args:
        pre_rolls (list): List of pre-roll file paths relative to base_dir.
        base_dir (str): The base directory for pre-roll videos.
    
    Returns:
        bool: True if all pre-roll files exist, False otherwise.
    """
    all_exist = True
    for pre_roll in pre_rolls:
        full_path = os.path.join(base_dir, pre_roll)
        if not os.path.isfile(full_path):
            logging.error(f"Pre-roll file does not exist: {full_path}")
            all_exist = False
    return all_exist
