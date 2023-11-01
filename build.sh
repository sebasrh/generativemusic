#!/usr/bin/env bash
# exit on error
set -o errexit

#poetry install
pip install --upgrade pip
pip install tensorflow
pip install tensorflow[and-cuda]
pip install keras
pip install music21
pip install -r requirements.txt 

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate