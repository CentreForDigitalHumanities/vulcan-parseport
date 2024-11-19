import json
from flask import Flask, Response, render_template, request, session
from flask_socketio import SocketIO, emit
from logger import log
from vulcan.file_loader import create_layout_from_filepath


SECRET_KEY = "My secret key"

socketio = SocketIO()

def create_app() -> Flask:
    log.info("Creating app...")

    log.info("Creating standard layout...")
    standard_layout = create_layout_from_filepath(
        # input_path="./little_prince_simple.pickle",
        input_path="./all.pickle",
        is_json_file=False,
        propbank_path=None,
    )
    log.info("Standard layout created.")

    
    app = Flask(__name__, template_folder='vulcan/client', static_folder='vulcan/client/js')
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

        print('Input is None', data['input'] is None)

        if data['input'] is None:
            print('Data input is None, so we use the standard corpus.')
            layout = standard_layout
        else:
            print('Input provided! Now create a layout from it!')
            # layout = create_layout_from_input(...)
            layout = None


        # Process the data as needed
        socketio.emit('start', data)
        return 'SocketIO instance started with data', 200
    
    @socketio.on('connect')
    def handle_connect():
        from vulcan.server.server import make_layout_sendable, create_list_of_possible_search_filters


        print('Connected!')
        sid = request.sid
        # This doesn't work yet, because the layout is not serializable.
        # layout = session.get('layout')

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
            # instance_requested(sid, 0)
        except Exception as e:
            log.exception(e)
            emit("server_error", to=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    
    socketio.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)