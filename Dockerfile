FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir flask==3.0.0 gunicorn==21.2.0 openai-whisper

COPY app.py .

RUN mkdir -p uploads

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "1800", "--workers", "1", "app:app"]
