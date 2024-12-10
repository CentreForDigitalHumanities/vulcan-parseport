import os
from flask import Flask, request, session
from flask_socketio import SocketIO, emit

from vulcan.file_loader import create_layout_from_filepath
from vulcan.search.search import create_list_of_possible_search_filters

from logger import log
from server_methods import instance_requested
from process_parse_data import process_parse_data
from db.models import db
from get_user_layout import get_user_layout
from send_layout_to_client import send_layout_to_client

# TODO: Handle CORS properly.
socketio = SocketIO(cors_allowed_origins="*")

# Used if no input is provided.
STANDARD_LAYOUT_INPUT_PATH = "./standard.pickle"
# For dev purposes.
# STANDARD_LAYOUT_INPUT_PATH = "./little_prince_simple.pickle"

def create_app() -> Flask:
    log.info("Creating app...")

    log.info("Creating standard layout...")
    standard_layout = create_layout_from_filepath(
        input_path=STANDARD_LAYOUT_INPUT_PATH,
        is_json_file=False,
        propbank_path=None,
    )

    log.info("Standard layout created.")

    app = Flask(__name__)
    # TODO: handle secret key/env correctly.
    app.config["SECRET_KEY"] = os.environ.get("VULCAN_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

    @app.route("/status/", methods=["GET"])
    def status():
        if standard_layout is not None:
            return {"ok": True}, 200
        return {"ok": False}, 500

    @app.route("/", methods=["POST"])
    def handle_parse_request():
        """
        Extract parse data from the request and proceeds to create a layout
        from it.

        After validating the input, the input is stored in a SQLite database
        along with the UUID and a timestamp.
        """
        log.debug("Handling parse request!")
        try:
            process_parse_data(request, db)
        except Exception as e:
            log.exception(f"An exception occurred while parsing the data: {e}")
            return {"ok": False}, 500

        log.debug("Data processed!")

        return {"ok": True}, 200

    @socketio.on("connect")
    def handle_connect():
        log.debug("Connected!")

        layout = get_user_layout(request, db)
        if layout is None:
            log.info("No layout found for user. Using standard layout.")
            layout = standard_layout

        sid = request.sid

        send_layout_to_client(sid, layout)

    @socketio.on("disconnect")
    def handle_disconnect():
        log.debug("Client disconnected")

    @socketio.on("instance_requested")
    def handle_instance_requested(index):
        instance_requested(request.sid, standard_layout, index)

    socketio.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    log.info("Vulcan initialised. Waiting for connections...")

    return app
