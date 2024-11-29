from vulcan.file_loader import create_layout_from_filepath
from vulcan.server.server import Server


def launch_server_from_file(
    input_path: str,
    port=5050,
    address="localhost",
    is_json_file=False,
    show_node_names=False,
    propbank_path: str | None = None,
    show_wikipedia_articles=False,
):

    layout = create_layout_from_filepath(
        input_path, is_json_file, propbank_path, show_wikipedia_articles
    )

    server = Server(layout, port=port, address=address, show_node_names=show_node_names)

    server.start()  # at this point, the server is running on this thread, and nothing below will be executed
