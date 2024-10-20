# Pre-Roll Automation v2

Automate Plex pre-roll video updates based on holidays. This application schedules and manages pre-roll videos for your Plex server, ensuring that the correct video is displayed during specified holiday periods.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Holiday-Based Pre-Rolls:** Automatically updates Plex pre-roll videos based on defined holiday periods.
- **Flexible Selection Modes:** Choose between random or sequential selection of pre-roll videos.
- **Manual Triggering:** Provides API endpoints to manually trigger pre-roll updates.
- **Logging:** Comprehensive logging with log rotation for monitoring and troubleshooting.
- **Unit Testing:** Includes unit tests to ensure reliability and correctness.

## Prerequisites

- Python 3.7 or higher
- Plex Media Server
- Access to Plex API Token

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/pre-roll_automation_v2.git
    cd pre-roll_automation_v2
    ```

2. **Create a Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables:**

    - Create a `.env` file in the root directory.
    - Add your Plex token and host:

        ```dotenv
        PLEX_TOKEN=your_plex_token_here
        PLEX_HOST=http://your_plex_host:32400
        LOG_LEVEL=INFO  # Optional: DEBUG, INFO, WARNING, ERROR, CRITICAL
        ```

## Configuration

1. **Edit `config/config.yaml`:**

    ```yaml
    # config/config.yaml

    # Plex Configuration
    plex:
      token: "${PLEX_TOKEN}"  # Your Plex token from .env
      host: "${PLEX_HOST}"    # Your Plex host URL from .env

    # Time Zone Configuration
    timezone: "America/Chicago"  # Time zone for scheduling and date calculations

    # Directories Configuration
    directories:
      base_pre_roll_dir: "/pre-rolls/plex"  # Base directory for pre-roll videos
      pre_roll:
        input: "/pre-rolls/input"
        output: "/pre-rolls/output"
        temp: "/pre-rolls/temp"

    # Schedule Configuration
    schedule:
      tasks:
        - name: "Daily Pre-Roll Update"
          time: "14:30"  # Time to run the update (HH:MM in 24-hour format)

    # Holidays Configuration
    holidays:
      - name: "New Years"
        start_date: "12-26"  # MM-DD format
        end_date: "01-04"    # MM-DD format
        pre_rolls:
          - "christmas/Snow Globe Plex Pre-roll.mp4"
          - "christmas/Another Pre-roll.mp4"
        selection_mode: "random"  # Options: "random", "sequential"
        last_index: 0  # Used for "sequential" mode

      # Add other holidays similarly...
    ```

2. **Define Holidays and Pre-Rolls:**

    - Ensure that all pre-roll video paths are relative to the `base_pre_roll_dir`.
    - Specify the selection mode as either `random` or `sequential`.

## Usage

1. **Run the Application:**

    ```bash
    python main.py
    ```

    - The scheduler will start in a separate thread.
    - The Flask API will run on `http://0.0.0.0:5000/`.

2. **Trigger Pre-Roll Update Manually:**

    - Send a POST request to `/update-pre-roll`.

    ```bash
    curl -X POST http://localhost:5000/update-pre-roll
    ```

## API Endpoints

- **GET `/`**

    - **Description:** Home endpoint providing basic information.
    - **Response:**

        ```json
        {
            "message": "Plex Pre-Roll Automation API",
            "status": "Running"
        }
        ```

- **POST `/update-pre-roll`**

    - **Description:** Manually trigger a pre-roll update.
    - **Response:**

        ```json
        {
            "message": "Pre-roll update triggered successfully."
        }
        ```

- **GET `/status`**

    - **Description:** Check the current status of the scheduler.
    - **Response:**

        ```json
        {
            "status": "Scheduler is running.",
            "next_run": "2024-10-21 14:30:00 CDT"
        }
        ```

## Testing

1. **Run Unit Tests:**

    ```bash
    python -m unittest discover tests
    ```

    - Ensures that all functionalities work as expected.

## Logging

- **Log Files:**
    - Located in the `logs/` directory.
    - `app.log` captures all logs with rotation to prevent excessive file sizes.

- **Console Logs:**
    - Logs are also output to the console for real-time monitoring.

- **Log Levels:**
    - Configurable via the `LOG_LEVEL` environment variable in the `.env` file.

## Contributing

1. **Fork the Repository.**
2. **Create a Feature Branch:**

    ```bash
    git checkout -b feature/YourFeature
    ```

3. **Commit Your Changes:**

    ```bash
    git commit -m "Add your feature"
    ```

4. **Push to the Branch:**

    ```bash
    git push origin feature/YourFeature
    ```

5. **Open a Pull Request.**

## License

This project is licensed under the [MIT License](LICENSE).

