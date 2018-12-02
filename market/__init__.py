"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
import logging
from flask import Flask
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

"""Create and configure an instance of the Flask application."""

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

if Path("market/env.cfg").exists():
    app.config.from_pyfile("env.cfg")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = ""

app.config["APP_ROOT"] = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "key"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Compress text, css, xml, json responeses
Compress(app)

# routes
from market.api import api_route

# routes api
app.register_blueprint(api_route)
