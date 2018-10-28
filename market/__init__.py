"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_compress import Compress


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)
    app.config.from_pyfile('env.cfg')
    app.debug = True
    app.config['APP_ROOT'] = os.path.abspath(os.path.dirname(__file__))

    # Compress text, css, xml, json responeses
    Compress(app)

    @app.route("/")
    def hello():
        return "Market Environment"

    # Database
    # app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app)

    # route Cross Origin Resource Sharing (CORS)
    # CORS(app, resources={r"/*": {"origins": "*"}})

    # routes
    from market.api import api_route

    # routes cluster
    app.register_blueprint(api_route)

    return app
