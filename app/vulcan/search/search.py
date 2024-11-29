from typing import List, Optional, Any, Dict, Tuple, Union

from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.search.graph_nodes.node_content_equals import NodeContentEquals
from vulcan.search.graph_nodes.outer_graph_node_layer import OuterGraphNodeLayer
from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer
from vulcan.search.search_registry import OUTER_SEARCH_LAYERS, INNER_SEARCH_LAYERS, VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS, \
    OUTER_TO_INNER_SEARCH_LAYERS
from vulcan.search.table.column_count_at_least import ColumnCountAtLeast
from vulcan.search.table.outer_table_as_a_whole_layer import OuterTableAsAWholeLayer
from vulcan.search.table_cells.cell_content_equals import CellContentEquals
from vulcan.search.table_cells.cell_content_matches import CellContentMatches
from vulcan.search.table_cells.outer_table_cells_layer import OuterTableCellsLayer
from vulcan.server.basic_layout import BasicLayout


class SearchFilter:
    def __init__(self, corpus_slice_name: str,
                 outer_search_layer_name: str, inner_search_layer_names: List[str],
                 inner_search_layer_arguments: List[List[str]],
                 color: str):
        self.corpus_slice_name = corpus_slice_name
        self.outer_search_layer_name = outer_search_layer_name
        self.inner_search_layer_names = inner_search_layer_names
        self.inner_search_layer_arguments = inner_search_layer_arguments
        self.color = color


def perform_search_on_layout(layout: BasicLayout,
                             filters: List[SearchFilter]) -> 'BasicLayout':
    lists_to_search: List[List[any]] = [_get_list_to_search(layout, f.corpus_slice_name) for f in filters]
    matching_indices, highlight_dicts = _search_lists(lists_to_search, filters)
    slices = _get_sub_slices_from_indices(layout, matching_indices, highlight_dicts)
    linkers = _get_sub_linkers_from_indices(layout, matching_indices)
    return BasicLayout(slices, linkers, len(matching_indices))


def _get_list_to_search(layout: BasicLayout, corpus_slice_name: str) -> List[any]:
    for row in layout.layout:
        for corpus_slice in row:
            if corpus_slice.name == corpus_slice_name:
                return corpus_slice.instances
    for linker_index, linker in enumerate(layout.linkers):
        if _get_linker_name(linker, linker_index) == corpus_slice_name:
            return linker["scores"]
    raise Exception("Corpus slice not found: " + corpus_slice_name)


def _get_sub_slices_from_indices(layout: BasicLayout, matching_indices: List[int],
                                 highlight_dicts: List[Dict[Tuple, Any]]) -> List[CorpusSlice]:
    sub_slices = []
    for row in layout.layout:
        for corpus_slice in row:
            new_instances = _filter_part_of_slice(corpus_slice.instances, matching_indices)
            new_label_alternatives = _filter_part_of_slice(corpus_slice.label_alternatives, matching_indices)
            new_highlights = _filter_part_of_slice(corpus_slice.highlights, matching_indices)
            new_highlights = _update_highlights(new_highlights, highlight_dicts, corpus_slice.name)
            new_mouseover_texts = _filter_part_of_slice(corpus_slice.mouseover_texts, matching_indices)
            new_dependency_trees = _filter_part_of_slice(corpus_slice.dependency_trees, matching_indices)

            new_slice = CorpusSlice(corpus_slice.name, new_instances,
                                    corpus_slice.visualization_type,
                                    label_alternatives=new_label_alternatives,
                                    highlights=new_highlights,
                                    mouseover_texts=new_mouseover_texts,
                                    dependency_trees=new_dependency_trees)
            sub_slices.append(new_slice)
    return sub_slices


def _update_highlights(old_highlights: Optional[List[Dict[Any, Union[str, List[str]]]]],
                       search_highlight_dicts: List[Dict[Tuple[str, Any], Union[str, List[str]]]],
                       slice_name: str):
    # update the search highlights with the old (base) highlights
    if old_highlights is not None:
        for old_highlight, search_highlight_dict in zip(old_highlights, search_highlight_dicts):  # iterate over corpus
            for key, value in old_highlight.items():  # iterate over all highlights for this corpus entry
                _add_highlight_color(search_highlight_dict, key, slice_name, value)

    # now turn the updated search highlights into the standard highlights format for this corpus slice
    ret = []
    for search_highlight_dict in search_highlight_dicts:  # iterate over corpus
        dict_here = {}
        for key, value in search_highlight_dict.items():  # iterate over all highlights for this corpus entry
            # print(key, value, slice_name)
            if key[0] == slice_name:  # only keep the ones that apply to this corpus slice
                dict_here[key[1]] = value
        ret.append(dict_here)
    return ret


def _get_sub_linkers_from_indices(layout: BasicLayout, matching_indices: List[int]) -> List[dict]:
    sub_linkers = []
    for linker_index, linker in enumerate(layout.linkers):
        new_scores = _filter_part_of_slice(linker["scores"], matching_indices)
        new_linker = {"name1": linker["name1"],
                      "name2": linker["name2"],
                      "scores": new_scores}
        sub_linkers.append(new_linker)
    return sub_linkers


def _filter_part_of_slice(part_of_slice: Optional[List[Any]], matching_indices: List[int]) -> Optional[List[Any]]:
    if part_of_slice is not None:
        return [part_of_slice[i] for i in matching_indices]
    else:
        return None


def _get_linker_name(linker, linker_index):
    return f"linker{linker_index} {linker['name1']} - {linker['name2']}"


def _search_lists(lists_to_search: List[List[any]],
                  filters: List[SearchFilter]) -> Tuple[List[int], List[Dict]]:
    outer_search_layers: List[OuterSearchLayer] = [get_outer_search_layer(f.outer_search_layer_name) for f in filters]
    inner_search_layers_list: List[List[InnerSearchLayer]] = [[get_inner_search_layer(name)
                                                          for name in f.inner_search_layer_names]
                                                            for f in filters]
    matching_indices = []
    highlight_dicts = []
    for index, items in enumerate(zip(*lists_to_search)):
        success = True
        highlighting_here = {}
        for outer_search_layer, inner_search_layers, search_filter, item in \
                zip(outer_search_layers, inner_search_layers_list, filters, items):
            node_names_here = outer_search_layer.apply(inner_search_layers, search_filter.inner_search_layer_arguments,
                                                       item)
            if node_names_here is None:
                # print(f"Search returned false for: {outer_search_layer.get_label()},"
                #       f" {[l.get_label() for l in inner_search_layers]}, {inner_search_layer_arguments}, {item}")
                success = False
                break
            else:
                for nn in node_names_here:
                    _add_highlight_color(highlighting_here, nn, search_filter.corpus_slice_name, search_filter.color)
        if success:
            matching_indices.append(index)
            highlight_dicts.append(highlighting_here)
    # highlight_dicts maps node names (can be ints, tuples of ints or strings, or any other object really) to colors.
    # Colors can be a single string, or a list of strings, or a table (list of lists) of strings.
    return matching_indices, highlight_dicts


def _add_highlight_color(highlight_dict: Dict[Tuple[str, Any], Union[str, List[str]]],
                         node_name: Any,
                         slice_name: str,
                         color: Union[str, List[str]]):
    key = (slice_name, node_name)
    if key in highlight_dict:
        if isinstance(highlight_dict[key], str):
            if isinstance(color, str):
                highlight_dict[key] = [highlight_dict[key], color]
            elif isinstance(color, list):
                if len(color) > 0 and isinstance(color[0], list):
                    print("Warning: Search highlighting is incompatible with highlight colors in table form."
                          "Highlighting will be ignored for this node.")
                else:
                    highlight_dict[key] = [highlight_dict[key]] + color
            else:
                raise Exception("Unknown type when adding highlight color")
        elif isinstance(highlight_dict[key], list):
            if isinstance(color, str):
                highlight_dict[key].append(color)
            elif isinstance(color, list):
                if len(color) > 0 and isinstance(color[0], list):
                    print("Warning: Search highlighting is incompatible with highlight colors in table form."
                          "Highlighting will be ignored for this node.")
                else:
                    highlight_dict[key] += color
            else:
                raise Exception("Unknown type when adding highlight color")
        else:
            raise Exception("Unknown type when adding highlight color")
    else:
        highlight_dict[key] = color


def get_outer_search_layer(name: str) -> OuterSearchLayer:
    return OUTER_SEARCH_LAYERS[name]


def get_inner_search_layer(name: str) -> InnerSearchLayer:
    return INNER_SEARCH_LAYERS[name]


def create_list_of_possible_search_filters(layout: BasicLayout):
    ret = {}
    for row in layout.layout:
        for corpus_slice in row:
            name = corpus_slice.name
            visualization_type = corpus_slice.visualization_type
            slice_dict = {}
            for outer_search_layer_id in VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS[visualization_type]:
                outer_search_layer = OUTER_SEARCH_LAYERS[outer_search_layer_id]
                outer_layer_dict = {"label": outer_search_layer.get_label(),
                                    "description": outer_search_layer.get_description(),
                                    "innerLayers": {}}
                for inner_search_layer_id in OUTER_TO_INNER_SEARCH_LAYERS[outer_search_layer_id]:
                    inner_search_layer = INNER_SEARCH_LAYERS[inner_search_layer_id]
                    inner_layer_dict = {"label": inner_search_layer.get_label(),
                                        "description": inner_search_layer.get_description()}
                    outer_layer_dict["innerLayers"][inner_search_layer_id] = inner_layer_dict

                slice_dict[outer_search_layer_id] = outer_layer_dict

            ret[name] = slice_dict
    return ret

