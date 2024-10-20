# app/schedule.py

import schedule
import time
import logging
from app.utils import get_current_holiday, select_pre_roll, update_plex_pre_roll
from app.config import Config
import threading
from datetime import datetime
from dateutil import tz

# Global variable to store next run time
next_run_time = None
next_run_lock = threading.Lock()

def job():
    """
    Job to determine the current holiday and update the Plex pre-roll accordingly.
    """
    global next_run_time
    try:
        # Update next run time
        with next_run_lock:
            next_run_time = schedule.next_run()

        # Determine if there is a current holiday
        holiday = get_current_holiday()
        
        if holiday:
            logging.info(f"Current holiday: {holiday['name']}")
            # Select the appropriate pre-roll video
            pre_roll_path = select_pre_roll(holiday)
            
            if pre_roll_path:
                # Update the Plex pre-roll with the selected video
                update_plex_pre_roll(pre_roll_path)
            else:
                logging.warning("No pre-roll video selected.")
        else:
            logging.info("No current holiday. Skipping pre-roll update.")
    except Exception as e:
        logging.error(f"Error in scheduled job: {e}")

def setup_schedule():
    """
    Sets up the schedule based on the configuration.
    """
    # Schedule the job based on the config
    for task in Config.SCHEDULE.get('tasks', []):
        time_str = task.get('time')
        task_name = task.get('name', 'Unnamed Task')
        if time_str:
            schedule.every().day.at(time_str).do(job)
            logging.info(f"Scheduled task '{task_name}' at {time_str}")

def run_scheduler():
    """
    Runs the scheduler in a separate thread.
    """
    setup_schedule()
    logging.info("Scheduler is running.")
    while True:
        schedule.run_pending()
        time.sleep(1)

def trigger_pre_roll_update():
    """
    Function to manually trigger the pre-roll update job.
    """
    threading.Thread(target=job).start()

def get_scheduler_next_run_time():
    """
    Retrieves the next scheduled run time in a readable format.

    Returns:
        str: Next run time as a string, or 'N/A' if not scheduled.
    """
    with next_run_lock:
        if next_run_time:
            # Convert to local timezone for readability
            local_timezone = tz.tzlocal()
            localized_time = next_run_time.astimezone(local_timezone)
            return localized_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        else:
            return "N/A"
