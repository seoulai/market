# Reinforcement Learning Market environment

[![Build Status](https://api.travis-ci.com/seoulai/market.svg?branch=master)](https://travis-ci.com/seoulai/market)

## Install

Create a virtualenv and activate it::

    $ virtualenv -p python3.6 [venv name]
    $ source [venv name]/bin/activate

    $ git clone https://github.com/seoulai/market.git [directory name]
    If you are facing an error like that on new MacOS version.
    > xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
    It means that you need to install XCode command line, open a Terminal and run this command:
    $ xcode-select --install

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
