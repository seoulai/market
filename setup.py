import io

from setuptools import find_packages, setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="market",
    version="0.0.1",
    url="http://github.com/seoulai/market",
    license="BSD",
    maintainer="Cinyoung Hur",
    maintainer_email="cinyoung.hur@gmail.com",
    description="Market environment",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "Flask-Compress",
        "Flask-Cors",
        "Flask-SQLAlchemy",
        "PyMySQL",
        "SQLAlchemy",
        "flake8",
        "flake8-quotes"
    ],
    extras_require={
        "test": [
            "pytest",
            "coverage",
        ],
    },
)
