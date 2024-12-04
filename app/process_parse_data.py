import base64
from datetime import datetime

from flask import Request
from flask_sqlalchemy import SQLAlchemy
from db.models import ParseResult
from logger import log


class InvalidInput(Exception):
    """
    Custom exception raised when the input data is invalid.
    """

    pass


def process_parse_data(request: Request, db: SQLAlchemy) -> None:
    """
    Validates the request data and stores the parse results in the database.
    """
    parse_results, uuid = validate_input(request)

    # Store in DB
    new_result = ParseResult(
        uuid=uuid,
        timestamp=datetime.now(),
        data=parse_results,
    )
    db.session.add(new_result)
    db.session.commit()


def validate_input(request) -> tuple[bytes | None, str | None]:
    """
    Validate the input received in the POST request. The input should be a JSON
    object containing two properties:
    - `parse_data`: a base64-encoded string representing the pickle/binary
        parse results;
    - `id`: an ID unique referencing the parse request.

    If the input is invalid, the function will raise an InvalidInput exception.
    """

    # Check if the request contains the necessary data
    if not request.json:
        log.error("No JSON data received.")
        raise InvalidInput("No JSON data received.")

    # Check if the request contains the necessary keys
    if "parse_data" not in request.json or "uuid" not in request.json:
        log.error("Missing keys in JSON data.")
        raise InvalidInput("Missing keys in JSON data.")

    # Extract the parse data and the UUID
    parse_data = request.json.get("parse_data")
    uuid = request.json.get("uuid")

    # Check if the parse data is valid
    if not parse_data or not isinstance(parse_data, str):
        log.error("No valid parse data received.")
        raise InvalidInput("No valid parse data received.")

    # Check if the UUID is valid
    if not uuid or not isinstance(uuid, str):
        log.error("No valid UUID received.")
        raise InvalidInput("No valid UUID received.")

    try:
        base64.b64decode(parse_data)
    except Exception as e:
        log.error("Could not decode base64 data:", e)
        raise InvalidInput("Could not decode base64 data.")

    return parse_data, uuid
