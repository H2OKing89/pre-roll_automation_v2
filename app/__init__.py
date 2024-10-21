# app/__init__.py

from flask import Flask
from .config import Config
from .logger import setup_logging
from .router import main_bp

def create_app():
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    setup_logging(app)

    # Register Blueprints
    app.register_blueprint(main_bp)

    return app
