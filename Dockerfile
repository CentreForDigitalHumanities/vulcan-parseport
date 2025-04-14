# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt update

# Install Gunicorn for production image
RUN pip install gunicorn

# Copy requirements file
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Set working directory
COPY app /app
WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0
ENV VULCAN_PORT=32771
ENV VULCAN_SECRET_KEY="insecure-key"

# Expose the port
EXPOSE $VULCAN_PORT

# Start the application.
CMD flask run --host=0.0.0.0 --port=${VULCAN_PORT}