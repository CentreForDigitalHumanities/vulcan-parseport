import json
from flask import Flask, Response, render_template, request, session, g
from flask_socketio import SocketIO, emit
from logger import log
from vulcan.file_loader import create_layout_from_filepath
from server_methods import instance_requested

SECRET_KEY = "My secret key"

socketio = SocketIO()

def create_app() -> Flask:
    log.info("Creating app...")

    log.info("Creating standard layout...")
    standard_layout = create_layout_from_filepath(
        # Petit Prince
        # input_path="./little_prince_simple.pickle",

        # Test pickle from Meaghan, should be used if no input is provided.
        # input_path="./all.pickle",

        # Test data from parser.
        input_path="./output.pickle",

        is_json_file=False,
        propbank_path=None,
    )
    log.info("Standard layout created.")
    
    app = Flask(__name__, template_folder='vulcan/client', static_folder='vulcan/client/static')
    app.config['SECRET_KEY'] = SECRET_KEY

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/start', methods=['POST'])
    def start():
        # Extract parse data from the request.
        data = request.json
        if not 'input' in data:
            return Response(
                status=400,
                response=json.dumps(dict(ok=False))
            )

        # Store request input in session.
        sid = request.sid
        session[sid] = data['input']

        # Process the data as needed
        return {'status': 'SocketIO instance started with data'}, 200
    
    @socketio.on('connect')
    def handle_connect():
        from vulcan.server.server import make_layout_sendable, create_list_of_possible_search_filters

        print('Connected!')
        sid = request.sid

        # TODO: investigate if we can serialize the layout instead.

        if sid in session:
            layout = session[sid]
        else:
            layout = standard_layout
        
        show_node_names = session.get('show_node_names')
        print('Layout for session:', layout)
        print('Client connected with SID', sid)

        try:
            print(sid, 'connected')
            emit('set_layout', make_layout_sendable(layout), to=sid)
            emit('set_corpus_length', layout.corpus_size, to=sid)
            emit('set_show_node_names', {"show_node_names": show_node_names}, to=sid)
            emit('set_search_filters', create_list_of_possible_search_filters(layout), to=sid)
            instance_requested(sid, layout, 0)
        except Exception as e:
            log.exception(e)
            emit("server_error", to=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('instance_requested')
    def handle_instance_requested(index):
        instance_requested(request.sid, standard_layout, index)
    
    socketio.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)