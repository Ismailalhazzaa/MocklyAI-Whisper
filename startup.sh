apt-get update && apt-get install -y ffmpeg
gunicorn --bind=0.0.0.0:8000 --timeout=180 --workers=1 app:app
