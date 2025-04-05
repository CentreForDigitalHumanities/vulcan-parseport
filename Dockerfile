# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt update
RUN apt install -y gettext
RUN pip install gunicorn

# Copy requirements file
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Set working directory
COPY app /app
WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=$VULCAN_DEBUG
ENV VULCAN_PORT=$VULCAN_PORT
ENV VULCAN_SECRET_KEY=$VULCAN_SECRET_KEY

# Expose the port
EXPOSE $VULCAN_PORT

# Run server
CMD ["flask", "run", "--host=0.0.0.0"]