# Reinforcement Learning Market environment

[![Build Status](https://api.travis-ci.com/seoulai/market.svg?branch=master)](https://travis-ci.com/seoulai/market)

## Install

Create a virtualenv and activate it::

    $ virtualenv -p python3.6 [venv name]
    $ source [venv name]/bin/activate

    $ git clone https://github.com/seoulai/market.git [directory name]

    If you are facing an error like that on new MacOS version.
    >> xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
    It means that you need to install XCode command line, open a Terminal and run this command:
    $ xcode-select --install

Or on Windows cmd::

    $ TODO: fill in
    $ TODO

Install TA-Lib::

    Download {ta-lib-0.4.0-src.tar.gz](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz) and:

    $ tar -xzf ta-lib-0.4.0-src.tar.gz
    $ cd ta-lib/
    $ ./configure --prefix=/usr
    $ make
    $ sudo make install

Install market::

    $ pip install -e .

Update config for database URI::

    $ python
    >> from market import db
    >> db.create_all()

## Run

On Linux::

    $ export FLASK_APP=market
    $ export FLASK_ENV=development
    $ flask run

Or on Windows cmd::

    > set FLASK_APP=market
    > set FLASK_ENV=development
    > flask run

## Test

    $ pip install '.[test]'
    $ pytest -m market -s

## Deploy

Update config for remote host::

    $ cp deploy.default.json deploy.json
