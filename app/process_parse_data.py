import pickle
import base64
from datetime import datetime

from flask import Request
from flask_sqlalchemy import SQLAlchemy

from db.models import ParseResult
from logger import log
from create_layout_from_input import create_layout_from_input


class InvalidInput(Exception):
    """
    Custom exception raised when the input data is invalid.
    """

    pass


def process_parse_data(request: Request, db: SQLAlchemy) -> None:
    """
    Validates the request data, converts the parse results to a Layout and
    stores it in the database.
    """
    parse_results, input_id = validate_input(request)
    log.debug('Input validated')

    user_layout = create_layout_from_input(parse_results)

    pickled = pickle.dumps(user_layout)

    # Store in DB
    new_result = ParseResult(
        timestamp=datetime.now(),
        input_id=input_id,
        layout=pickled,
    )
    db.session.add(new_result)
    db.session.commit()

    log.debug('Data stored in DB')


def validate_input(request) -> tuple[bytes | None, str | None]:
    """
    Validate the input received in the POST request. The input should be a JSON
    object containing two properties:
    - `parse_data`: a base64-encoded string representing the pickle/binary
        parse results;
    - `id`: an ID uniquely referencing the parse request.

    If the input is invalid, the function will raise an InvalidInput exception.
    """

    # Check if the request contains the necessary data
    if not request.json:
        log.error("No JSON data received.")
        raise InvalidInput("No JSON data received.")

    # Check if the request contains the necessary keys
    if "parse_data" not in request.json or "id" not in request.json:
        log.error("Missing keys in JSON data.")
        raise InvalidInput("Missing keys in JSON data.")

    # Extract the parse data and the ID
    parse_data = request.json.get("parse_data")
    input_id = request.json.get("id")

    # Check if the parse data is valid
    if not parse_data or not isinstance(parse_data, str):
        log.error("No valid parse data received.")
        raise InvalidInput("No valid parse data received.")

    # Check if the ID is valid
    if not input_id or not isinstance(input_id, str):
        log.error("No valid id received.")
        raise InvalidInput("No valid id received.")

    try:
        decoded = base64.b64decode(parse_data)
    except Exception as e:
        log.error("Could not decode base64 data:", e)
        raise InvalidInput("Could not decode base64 data.")

    return decoded, input_id
