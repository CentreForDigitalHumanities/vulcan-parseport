from flask_socketio import emit

from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.file_loader import BasicLayout
from vulcan.search.search import create_list_of_possible_search_filters

from .server_methods import instance_requested
from logger import log


def send_layout_to_client(sid: str, layout: BasicLayout) -> None:
    try:
        emit("set_layout", make_layout_sendable(layout), to=sid)
        emit("set_corpus_length", layout.corpus_size, to=sid)
        emit("set_show_node_names", {"show_node_names": False}, to=sid)
        emit(
            "set_search_filters",
            create_list_of_possible_search_filters(layout),
            to=sid,
        )
        instance_requested(sid, layout, 0)
    except Exception as e:
        log.exception(e)
        emit("server_error", to=sid)


# The following two methods are copied from vulcan.server.server, but
# if we import that file, the server will crash.
def make_slice_sendable(corpus_slice: CorpusSlice):
    ret = {
        "name": corpus_slice.name,
        "visualization_type": corpus_slice.visualization_type,
    }
    return ret


def make_layout_sendable(layout):
    ret = []
    for row in layout.layout:
        ret.append([make_slice_sendable(s) for s in row])
    return ret
