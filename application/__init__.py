import flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_mode):
    """Creates and configures the Flask application according to the supplied configuration mode."""

    app = flask.Flask(__name__)
    CORS(app)

    # Import and set configurations from config file
    from config import config
    app.config.from_object(config[config_mode])
    jwt.init_app(app)

    with app.app_context():
        # Import and register blueprint from routes file
        from .routes import routes_bp

        app.register_blueprint(routes_bp)

        # Import models in order to initialize them
        from . import models

        # Initialize the database
        db.init_app(app)
        db.create_all()

        return app
