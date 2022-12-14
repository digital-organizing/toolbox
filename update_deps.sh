#!/usr/bin/sh

pip-compile -o requirements.txt pyproject.toml
pip-compile --extra dev -o dev-requirements.txt pyproject.toml

pip install -r requirements.txt
pip install -r dev-requirements.txt
