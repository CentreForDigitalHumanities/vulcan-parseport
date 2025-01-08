from typing import Any

from flask_socketio import emit

from logger import log

from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.server.basic_layout import BasicLayout
from vulcan.search.search import SearchFilter

# These methods are copied from vulcan.server.server. 
# We cannot import that file directly, since it crashes the app.

def cell_coordinates_to_cell_name(row: int, column: int) -> str:
    return f"({row}, {column})"


def transform_string_maps_to_table_maps(
    highlights: dict[int, str | list[str]],
    label_alternatives_by_node_name: dict[int, dict[str, Any]],
):
    if label_alternatives_by_node_name:
        label_alternatives_by_node_name = {
            cell_coordinates_to_cell_name(0, k): v
            for k, v in label_alternatives_by_node_name.items()
        }
    if highlights:
        highlights = {
            cell_coordinates_to_cell_name(0, k): v for k, v in highlights.items()
        }
    return highlights, label_alternatives_by_node_name


def send_string_table(
    slice_name: str,
    table: list[list[str]],
    label_alternatives_by_node_name: dict[tuple[int, int], Any] | None = None,
    highlights: dict[tuple[int, int], str | list[str]] | None = None,
    dependency_tree: list[tuple[int, int, str]] | None = None,
) -> dict:
    dict_to_send = {"canvas_name": slice_name, "table": table}
    if label_alternatives_by_node_name is not None:
        dict_to_send["label_alternatives_by_node_name"] = (
            label_alternatives_by_node_name
        )
    if highlights is not None:
        dict_to_send["highlights"] = highlights
    if dependency_tree is not None:
        dict_to_send["dependency_tree"] = dependency_tree
    return dict_to_send


def send_string(
    slice_name: str,
    tokens: list[str],
    label_alternatives_by_node_name: dict | None = None,
    highlights: dict[int, str | list[str]] | None = None,
    dependency_tree: list[tuple[int, int, str]] | None = None,
) -> dict:
    highlights, label_alternatives_by_node_name = transform_string_maps_to_table_maps(
        highlights, label_alternatives_by_node_name
    )
    return send_string_table(
        slice_name,
        [[t] for t in tokens],
        label_alternatives_by_node_name,
        highlights,
        dependency_tree,
    )


def send_graph(
    slice_name: str,
    graph: dict,
    label_alternatives_by_node_name: dict | None = None,
    highlights: dict[str, str | list[str]] = None,
    mouseover_texts: dict[str, str] = None,
) -> dict:
    #  graph must be of the graph_as_dict type.
    dict_to_send = {"canvas_name": slice_name, "graph": graph}
    if label_alternatives_by_node_name is not None:
        dict_to_send["label_alternatives_by_node_name"] = (
            label_alternatives_by_node_name
        )
    if highlights is not None:
        dict_to_send["highlights"] = highlights
    if mouseover_texts is not None:
        dict_to_send["mouseover_texts"] = mouseover_texts
    return dict_to_send


def send_linker(
    name1: str, name2: str, layout: BasicLayout, scores: dict[str, dict[str, float]]
) -> dict:
    if layout.get_visualization_type_for_slice_name(name1) == VisualizationType.STRING:
        scores = {str((0, k)).replace("'", ""): v for k, v in scores.items()}
    if layout.get_visualization_type_for_slice_name(name2) == VisualizationType.STRING:
        scores = {
            k: {str((0, k2)).replace("'", ""): v for k2, v in d.items()}
            for k, d in scores.items()
        }
    return {"name1": name1, "name2": name2, "scores": scores}


def instance_requested(sid: str, layout: BasicLayout, data: Any):
    try:
        if layout.corpus_size > 0:
            instance_id = data
            for row in layout.layout:
                for corpus_slice in row:
                    if corpus_slice.label_alternatives is not None:
                        label_alternatives_by_node_name = (
                            corpus_slice.label_alternatives[instance_id]
                        )
                    else:
                        label_alternatives_by_node_name = None

                    if corpus_slice.highlights is not None:
                        highlights = corpus_slice.highlights[instance_id]
                    else:
                        highlights = None

                    if corpus_slice.mouseover_texts is not None:
                        mouseover_texts = corpus_slice.mouseover_texts[instance_id]
                    else:
                        mouseover_texts = None

                    if corpus_slice.dependency_trees is not None:
                        dependency_tree = corpus_slice.dependency_trees[instance_id]
                    else:
                        dependency_tree = None

                    if corpus_slice.visualization_type == VisualizationType.STRING:
                        send_data = send_string(
                            corpus_slice.name,
                            corpus_slice.instances[instance_id],
                            label_alternatives_by_node_name,
                            highlights,
                            dependency_tree,
                        )
                        emit('set_table', send_data, to=sid)
                    elif corpus_slice.visualization_type == VisualizationType.TABLE:
                        send_data = send_string_table(
                            corpus_slice.name,
                            corpus_slice.instances[instance_id],
                            label_alternatives_by_node_name,
                            highlights,
                            dependency_tree,
                        )
                        emit('set_table', send_data, to=sid)
                    elif corpus_slice.visualization_type == VisualizationType.TREE:
                        # trees are just graphs without reentrancies
                        send_data = send_graph(
                            corpus_slice.name,
                            corpus_slice.instances[instance_id],
                            label_alternatives_by_node_name,
                            highlights,
                        )
                        emit('set_graph', send_data, to=sid)
                    elif corpus_slice.visualization_type == VisualizationType.GRAPH:
                        send_data = send_graph(
                            corpus_slice.name,
                            corpus_slice.instances[instance_id],
                            label_alternatives_by_node_name,
                            highlights,
                            mouseover_texts,
                        )
                        emit('set_graph', send_data, to=sid)
            for linker in layout.linkers:
                sent_data = send_linker(
                    linker["name1"],
                    linker["name2"],
                    layout,
                    linker["scores"][instance_id],
                )
                emit("set_linker", sent_data, to=sid)
        else:
            print("No instances in corpus")
    except Exception as e:
        log.exception(e)
        emit("server_error", to=sid)


def get_search_filters_from_data(data) -> list[SearchFilter]:
    search_filters = []
    for search_filter_data in data:
        search_filters.append(
            SearchFilter(
                search_filter_data["slice_name"],
                search_filter_data["outer_layer_id"],
                search_filter_data["inner_layer_ids"],
                search_filter_data["inner_layer_inputs"],
                search_filter_data["color"],
            )
        )
    return search_filters