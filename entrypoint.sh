#!/bin/bash
if [ "$VULCAN_SECRET_KEY" = "insecure-key" ]; then
    echo "ERROR: VULCAN_SECRET_KEY environment variable must be added to .env. Consult the README for more information."
    exit 1
fi

# If we get here, the environment variable is set, so run the application
exec flask run --host=0.0.0.0 --port=${VULCAN_PORT}