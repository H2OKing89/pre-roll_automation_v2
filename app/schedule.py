# app/schedule.py

import schedule
import time
import logging
from app.utils import get_current_holiday, select_pre_roll, update_plex_pre_roll
from app.config import Config  # <-- Added import

def job():
    # Determine if there is a current holiday
    holiday = get_current_holiday()
    
    if holiday:
        # Select the appropriate pre-roll video
        pre_roll_path = select_pre_roll(holiday)
        
        if pre_roll_path:
            # Update the Plex pre-roll with the selected video
            update_plex_pre_roll(pre_roll_path)
        else:
            logging.warning("No pre-roll video selected.")
    else:
        logging.info("No current holiday. Skipping pre-roll update.")

def setup_schedule():
    # Schedule the job based on the config
    for task in Config.SCHEDULE.get('tasks', []):
        time_str = task.get('time')
        if time_str:
            schedule.every().day.at(time_str).do(job)
            logging.info(f"Scheduled task '{task.get('name')}' at {time_str}")

def run_scheduler():
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(1)
