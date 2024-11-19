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
WORKDIR /src

# Copy project
COPY . /src/

# Create a directory for server logs (production).
RUN mkdir -p /logs

# Expose port
EXPOSE 5050

ENV FLASK_APP=app.py
ENV FLASK_ENV=1

# Expose the port
EXPOSE 32771

# Run server
CMD ["python", "start_server.py"]
# CMD ["python", "launch_vulcan.py", "little_prince_simple.pickle", "--address=0.0.0.0", "--port=5050"]