#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y libxml2-dev libxslt-dev python3-dev build-essential

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
