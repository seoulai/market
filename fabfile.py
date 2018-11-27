# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import json
import codecs

from fabric.contrib.files import exists
from fabric.api import env, run, sudo, cd, prefix
from contextlib import contextmanager as _contextmanager

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

envs = json.loads(codecs.open(os.path.join(
    PROJECT_DIR, "deploy.json"), "r", "utf-8").read())

apt_requirements = [
    "curl",
    "git",
    "python3-dev",
    "python3-pip",
    "build-essential",
    "python3-setuptools",
    "libssl-dev",
    "libffi-dev",
]


def setup(env="venv"):
    _install_apt_requirements(apt_requirements)
    _get_latest_apt()

    _make_virtualenv()


def prod():
    env.user = envs["REMOTE_USER"]
    env.hosts = [
        envs["REMOTE_HOST_SSH"]
    ]
    env.branch = "master"


def deploy():
    _get_latest_source(env.branch)
    _update_env_api(env.branch)
    _restart_api(env.branch)


@_contextmanager
def _virtualenv(project_dir):
    with cd(project_dir):
        with prefix("source %s/venv/bin/activate" % project_dir):
            yield


@_contextmanager
def _userpathenv():
    with prefix("source ~/.profile"):
        yield


def _get_latest_apt():
    sudo("apt-get update")


def _install_apt_requirements(apt_requirements):
    reqs = ""
    for req in apt_requirements:
        reqs += (" " + req)
    sudo("apt-get -y install {}".format(reqs))


def _make_virtualenv():
    if not exists("~/.virtualenvs"):
        script = """# python virtualenv settings
export WORKON_HOME=~/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON="$(command which python3)"
source /usr/local/bin/virtualenvwrapper.sh
"""
        run("mkdir ~/.virtualenvs")
        sudo("pip3 install virtualenv virtualenvwrapper")
        run("echo {} >> ~/.profile".format(script))


def _set_path(branch):
    api_project_folder = envs["REMOTE_PROJECT_FOLDER"] + \
        envs["API_PROJECT_NAME"]

    return api_project_folder


def _get_latest_source(branch):
    api_project_folder = _set_path(branch)

    if exists(api_project_folder + "/.git"):
        run("cd %s && git pull origin %s" % (api_project_folder, branch))
    else:
        run("git clone -b %s %s %s" %
            (branch, envs["API_REPO_URL"], api_project_folder))


def _update_env_api(branch):
    api_project_folder = _set_path(branch)
    if not exists(api_project_folder + "/venv"):
        run("cd %s && virtualenv venv -p /usr/bin/python3.6" %
            api_project_folder)
    with _virtualenv(api_project_folder):
        run("pip install -r requirements.txt")


def _restart_api(branch):
    api_project_folder = _set_path(branch)
    with _virtualenv(api_project_folder):
        run("python run.py")
