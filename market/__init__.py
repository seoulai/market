"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
from flask import Flask
from flask_compress import Compress
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)
    if test_config is None:
        app.config.from_pyfile("env.cfg")
    app.config["APP_ROOT"] = os.path.abspath(os.path.dirname(__file__))
    app.config["SECRET_KEY"] = "key"
    app.config["DATABASE"] = os.path.join(
        app.config["APP_ROOT"], "market.sqlite")
    # Compress text, css, xml, json responeses
    Compress(app)

    @app.route("/")
    def hello():
        return "Market Environment"

    # register the database commands
    from market import db
    db.init_app(app)

    # route Cross Origin Resource Sharing (CORS)
    # CORS(app, resources={r"/*": {"origins": "*"}})

    # routes
    from market.api import api_route

    # routes api
    app.register_blueprint(api_route)

    return app
