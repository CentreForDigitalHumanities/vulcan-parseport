import os
from flask import Flask, request
from flask_socketio import SocketIO, emit

from vulcan.file_loader import create_layout_from_filepath

from logger import log
from services.server_methods import instance_requested
from services.process_parse_data import process_parse_data
from db.models import db
from services.get_user_layout import (
    get_stored_layout,
    get_and_unpack_layout,
    unpack_layout,
)
from services.send_layout_to_client import send_layout_to_client
from services.search import handle_search
from utils.timestamps import remove_old_layouts

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

    # HTTP route handlers
    @app.route("/status/", methods=["GET"])
    def status():
        if standard_layout is not None:
            return {"ok": True}, 200
        return {"ok": False}, 500

    @app.route("/", methods=["POST"])
    def handle_parse_request():
        log.debug("Handling parse request!")
        try:
            process_parse_data(request, db)
        except Exception as e:
            log.exception(f"An exception occurred while parsing the data: {e}")
            return {"ok": False}, 500

        log.debug("Data processed!")

        return {"ok": True}, 200

    # Websocket event handlers
    @socketio.on("connect")
    def handle_connect():
        log.debug("Client connected")

        # TODO: this should be done in a cronjob.
        remove_old_layouts(db)

        layout = get_and_unpack_layout(request, db)
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
        layout = get_and_unpack_layout(request, db)
        if layout is None:
            log.info(
                f"No layout found for user on requesting instance. Using standard layout."
            )
            layout = standard_layout
        instance_requested(request.sid, layout, index)

    @socketio.on("perform_search")
    def perform_search(data):
        """
        Perform a search on the current layout and reroute to it.
        """
        log.debug("Search requested")
        result_identifier = handle_search(request, db, data, standard_layout)
        log.debug("Search successful. Rerouting to result.")
        emit("route_to_layout", result_identifier, to=request.sid)

    @socketio.on("clear_search")
    def clear_search():
        """Return the base layout on which the current layout is based."""
        log.debug("Clearing search.")
        layout = get_stored_layout(request, db)
        if layout is None:
            log.info(
                f"No layout found for user on clearing search."
            )
            emit("route_to_layout", "", to=request.sid)
            return
        
        if layout.based_on is None:
            log.info(
                f"No base layout found for user on clearing search."
            )
            return

        layout_data = unpack_layout(layout.based_on)
        identifier = layout.based_on.parse_id

        emit("set_corpus_length", layout_data.corpus_size, to=request.sid)
        log.debug("Clearing search successful. Rerouting to base layout.")
        emit("route_to_layout", identifier, to=request.sid)

    socketio.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    log.info("Vulcan initialised. Waiting for connections...")

    return app
