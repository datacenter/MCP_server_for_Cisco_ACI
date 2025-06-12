# Dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
CMD ["python", "-u", "main.py"]
