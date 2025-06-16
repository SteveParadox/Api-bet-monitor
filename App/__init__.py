from flask import Flask
from .config import Config
from app.routes.alerts import alerts_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes import alerts
    app.register_blueprint(alerts_bp, url_prefix="/api")

    return app
