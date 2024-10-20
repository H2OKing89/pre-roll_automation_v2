# main.py

"""
Main entry point for the Plex Pre-Roll Automation application.

This script initializes logging, starts the scheduler in a separate thread,
sets up the Flask application, and provides a command-line interface to
manually trigger pre-roll updates.
"""

from app.config import Config
from app.schedule import run_scheduler
from app.logger import setup_logging
from app.utils import update_plex_pre_roll, get_current_holiday, select_pre_roll
from app import create_app
import threading
import logging
import signal
import sys

def manual_pre_roll_update():
    """
    Manually triggers the pre-roll update process.

    This function selects the appropriate pre-roll based on the current holiday
    and updates the Plex server with the selected pre-roll video.
    """
    logging.info("Manual pre-roll update triggered.")

    # Determine the current holiday period
    holiday = get_current_holiday()
    if holiday:
        # Select a pre-roll video based on the holiday's selection mode
        pre_roll = select_pre_roll(holiday)
        if pre_roll:
            # Update Plex with the selected pre-roll video
            update_plex_pre_roll(pre_roll)
            logging.info(f"Pre-roll updated manually to: {pre_roll}")
        else:
            logging.error("No pre-roll selected for the current holiday.")
    else:
        logging.info("No active holiday found. No pre-roll update was performed.")

def main():
    """
    Main function to start the scheduler and the Flask application or trigger manual update.

    - Sets up logging.
    - Checks for command-line arguments to determine operation mode.
    - Starts the scheduler in a separate daemon thread.
    - Initializes and runs the Flask web server.
    """
    # Setup logging configuration
    setup_logging()

    # Check if a manual update is requested via CLI argument
    if len(sys.argv) > 1 and sys.argv[1] == "manual-update":
        manual_pre_roll_update()
        sys.exit(0)  # Exit after manual update to prevent starting the server

    # Start the scheduler in a separate daemon thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    logging.info("Scheduler started. Application is running.")

    # Create and configure the Flask app
    app = create_app()

    # Define signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logging.info('Shutting down gracefully...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)   # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signals

    # Run the Flask web server
    app.run(host='0.0.0.0', port=5000)  # Accessible on all network interfaces

if __name__ == "__main__":
    main()
