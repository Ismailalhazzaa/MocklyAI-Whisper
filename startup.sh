#!/bin/bash
apt-get update -qq && apt-get install -y ffmpeg
gunicorn --bind=0.0.0.0:8000 --timeout=1800 --workers=1 app:app
