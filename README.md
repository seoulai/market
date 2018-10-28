# Reinforcement Learning Market environment

[![Build Status](https://api.travis-ci.com/seoulai/market.svg?branch=master)](https://travis-ci.com/seoulai/market)

## Install

Create a virtualenv and activate it::

    $ virtualenv -p python3.6 venv
    $ source venv/bin/activate

Or on Windows cmd::

    $ TODO: fill in
    $ TODO

Install Flaskr::

    $ pip install -e .

## Run

::

    $ export FLASK_APP=market
    $ export FLASK_ENV=development
    $ flask run

Or on Windows cmd::

    > set FLASK_APP=market
    > set FLASK_ENV=development
    > flask run

## Test

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
