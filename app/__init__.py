# app\__init__.py

from flask import Flask # type: ignore
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # Register blueprints
    from .routes.roadmap_routes import roadmap_bp
    from .routes.integration_routes import integration_bp

    app.register_blueprint(roadmap_bp, url_prefix='/api')
    app.register_blueprint(integration_bp, url_prefix='/api')

    return app
