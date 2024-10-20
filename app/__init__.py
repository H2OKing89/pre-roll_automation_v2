from flask import Flask
from .config import Config
from .logger import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    setup_logging(app)

    with app.app_context():
        # Import routes
        from . import main
        app.register_blueprint(main.bp)

    return app
