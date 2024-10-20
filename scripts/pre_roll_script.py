# scripts/pre_roll_script.py

import os
import shutil
import logging
from app.config import Config

def execute_pre_roll():
    input_dir = Config.DIRECTORIES['pre_roll']['input']
    output_dir = Config.DIRECTORIES['pre_roll']['output']
    temp_dir = Config.DIRECTORIES['pre_roll']['temp']

    logging.info(f"Pre-roll started. Input: {input_dir}, Output: {output_dir}, Temp: {temp_dir}")

    # Example operation: Move files from input to temp
    try:
        for filename in os.listdir(input_dir):
            src = os.path.join(input_dir, filename)
            dest = os.path.join(temp_dir, filename)
            shutil.move(src, dest)
            logging.info(f"Moved {src} to {dest}")
    except Exception as e:
        logging.error(f"Error during pre-roll: {e}")

    # Further pre-roll operations...
    logging.info("Pre-roll completed successfully.")
