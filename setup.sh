#!/usr/bin/env bash

# Install python
sudo apt-get install software-properties-common
sudo apt update -y
sudo apt install python3

# install venv and create local venv
python3 -m pip install --user virtualenv
python3 -m venv venv

# install dependencies in local venv
source "venv/bin/activate"
pip install -r requirements.txt