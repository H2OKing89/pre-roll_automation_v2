# app/router.py

"""
Flask Blueprint for the Plex Pre-Roll Automation API.

Defines API endpoints to interact with the pre-roll update system, including
triggering updates and checking scheduler status.
"""

from flask import Blueprint, jsonify, request
import logging
from app.schedule import trigger_pre_roll_update, get_scheduler_next_run_time

# Define a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    """
    Home route that provides basic information about the API.

    Returns:
        JSON response with a message and status.
    """
    return jsonify({
        "message": "Plex Pre-Roll Automation API",
        "status": "Running"
    }), 200

@main_bp.route('/update-pre-roll', methods=['POST'])
def update_pre_roll():
    """
    Endpoint to manually trigger a pre-roll update.

    This route allows external systems or users to initiate a pre-roll update
    by sending a POST request.

    Returns:
        JSON response indicating success or failure.
    """
    try:
        # Trigger the pre-roll update process
        trigger_pre_roll_update()
        logging.info("Manual pre-roll update triggered via API.")
        return jsonify({"message": "Pre-roll update triggered successfully."}), 200
    except Exception as e:
        # Log the error and return an error response
        logging.error(f"Failed to trigger pre-roll update: {e}")
        return jsonify({"error": "Failed to trigger pre-roll update."}), 500

@main_bp.route('/status', methods=['GET'])
def status():
    """
    Endpoint to check the current status of the scheduler.

    Returns:
        JSON response with the scheduler's running status and next scheduled run time.
    """
    try:
        # Retrieve the next scheduled run time from the scheduler
        next_run = get_scheduler_next_run_time()
        logging.info("Status endpoint accessed.")
        
        return jsonify({
            "status": "Scheduler is running.",
            "next_run": next_run
        }), 200
    except Exception as e:
        # Log the error and return an error response
        logging.error(f"Failed to retrieve scheduler status: {e}")
        return jsonify({"error": "Failed to retrieve scheduler status."}), 500
