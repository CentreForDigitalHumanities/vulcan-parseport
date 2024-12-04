import os
from flask import Flask, request, session
from flask_socketio import SocketIO, emit
from logger import log
from vulcan.file_loader import create_layout_from_filepath
from server_methods import instance_requested
from process_parse_data import process_parse_data
from db.models import db


# TODO: Handle CORS properly.
socketio = SocketIO(cors_allowed_origins="*")

def create_app() -> Flask:
    log.info("Creating app...")

    log.info("Creating standard layout...")
    standard_layout = create_layout_from_filepath(
        # Petit Prince
        input_path="./little_prince_simple.pickle",
        # Test pickle from Meaghan, should be used if no input is provided.
        # input_path="./all.pickle",
        is_json_file=False,
        propbank_path=None,
    )
    log.info("Standard layout created.")

    app = Flask(
        __name__, template_folder="vulcan/client", static_folder="vulcan/client/static"
    )
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
        try:
            process_parse_data(request, db)
        except Exception as e:
            log.exception(f"An exception occurred while parsing the data: {e}")
            return {"ok": False}, 500
        
        return {"ok": True}, 200

    @socketio.on("connect")
    def handle_connect():
        from vulcan.server.server import (
            make_layout_sendable,
            create_list_of_possible_search_filters,
        )

        print("Connected!")
        sid = request.sid

        if sid in session:
            layout = session[sid]
        else:
            layout = standard_layout

        show_node_names = session.get("show_node_names")
        print("Layout for session:", layout)
        print("Client connected with SID", sid)

        try:
            print(sid, "connected")
            emit("set_layout", make_layout_sendable(layout), to=sid)
            emit("set_corpus_length", layout.corpus_size, to=sid)
            emit("set_show_node_names", {"show_node_names": show_node_names}, to=sid)
            emit(
                "set_search_filters",
                create_list_of_possible_search_filters(layout),
                to=sid,
            )
            instance_requested(sid, layout, 0)
        except Exception as e:
            log.exception(e)
            emit("server_error", to=sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Client disconnected")

    @socketio.on("instance_requested")
    def handle_instance_requested(index):
        instance_requested(request.sid, standard_layout, index)

    socketio.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
