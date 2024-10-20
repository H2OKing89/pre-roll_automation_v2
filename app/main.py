# main.py

from app.config import Config
from app.schedule import run_scheduler
import threading
import logging
import time  # <-- Added import

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    logging.info("Scheduler started. Application is running.")

    # Keep the main thread alive
    while True:
        time.sleep(1)
