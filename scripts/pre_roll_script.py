# scripts/pre_roll_script.py

import os
import shutil
import logging
from app.config import Config
from app.logger import setup_logging
from pathlib import Path

def execute_pre_roll():
    """
    Executes pre-roll operations, such as moving video files from input to temp directories.
    """
    # Initialize logging
    setup_logging()

    input_dir = Path(Config.DIRECTORIES['pre_roll']['input'])
    output_dir = Path(Config.DIRECTORIES['pre_roll']['output'])
    temp_dir = Path(Config.DIRECTORIES['pre_roll']['temp'])

    logging.info(f"Pre-roll started. Input: {input_dir}, Output: {output_dir}, Temp: {temp_dir}")

    # Ensure directories exist
    for directory in [input_dir, output_dir, temp_dir]:
        if not directory.exists():
            logging.error(f"Directory does not exist: {directory}")
            return

    # Example operation: Move files from input to temp
    try:
        files = list(input_dir.iterdir())
        if not files:
            logging.info("No files to process in input directory.")
            return

        for file_path in files:
            if file_path.is_file():
                dest = temp_dir / file_path.name
                try:
                    shutil.move(str(file_path), str(dest))
                    logging.info(f"Moved {file_path} to {dest}")
                except Exception as move_error:
                    logging.error(f"Failed to move {file_path} to {dest}: {move_error}")
    except Exception as e:
        logging.error(f"Error during pre-roll operations: {e}")
        return

    # Further pre-roll operations can be added here
    logging.info("Pre-roll completed successfully.")

if __name__ == "__main__":
    execute_pre_roll()
