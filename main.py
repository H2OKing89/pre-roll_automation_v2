# main.py

"""
Main entry point for the Plex Pre-Roll Automation application.

This script initializes logging, validates configurations, starts the scheduler in a separate thread,
sets up the Flask application, and provides a command-line interface to manually trigger pre-roll updates.
"""

from app.config import Config
from app.schedule import run_scheduler, trigger_pre_roll_update_thread
from app.logger import setup_logging
from app.utils import trigger_pre_roll_update, get_validated_holidays, get_current_holiday
from app import create_app
import threading
import logging
import signal
import sys

def main():
    """
    Main function to validate configurations, start the scheduler, and run the Flask application or trigger manual update.

    - Sets up logging.
    - Validates configurations.
    - Starts the scheduler in a separate daemon thread.
    - Initializes and runs the Flask web server.
    """
    # Setup logging configuration
    setup_logging()

    try:
        # Validate configurations and retrieve validated holidays
        valid_holidays = get_validated_holidays()
        if not valid_holidays:
            logging.error("No valid holidays found. Exiting application.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Configuration validation failed: {e}")
        sys.exit(1)

    # Check for command-line arguments to determine operation mode
    if len(sys.argv) > 1 and sys.argv[1] == "manual-update":
        try:
            trigger_pre_roll_update(valid_holidays)
            sys.exit(0)  # Exit after manual update to prevent starting the server
        except Exception as e:
            logging.error(f"Manual update failed: {e}")
            sys.exit(1)

    # Start the scheduler in a separate daemon thread
    scheduler_thread = threading.Thread(target=run_scheduler, args=(valid_holidays,), daemon=True)
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
