"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
from flask import Flask
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy


# def create_app(test_config=None):
"""Create and configure an instance of the Flask application."""

app = Flask(__name__)
# if test_config is None:
#     app.config.from_pyfile("env.cfg")
app.config["APP_ROOT"] = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "key"
# app.config["DATABASE"] = os.path.join(
#     app.config["APP_ROOT"], "market.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(
    app.config["APP_ROOT"], "market.sqlite")

db = SQLAlchemy(app)

# Compress text, css, xml, json responeses
Compress(app)


# routes
from market.api import api_route

# routes api
app.register_blueprint(api_route)


@app.route("/")
def hello():
    return "Market Environment"
