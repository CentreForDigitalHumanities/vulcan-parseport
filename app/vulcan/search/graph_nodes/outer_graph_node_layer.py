from abc import ABC
from typing import List, Any, Dict, Tuple

from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer
from vulcan.data_handling.linguistic_objects.graphs.graph_as_dict import for_each_node_top_down


class OuterGraphNodeLayer(OuterSearchLayer):
    def get_description(self) -> str:
        return "This layer checks if any node in a graph matches the given criteria, and highlights the nodes that do."

    def get_label(self) -> str:
        return "Any node in the graph matches:"

    def get_id(self) -> str:
        return "OuterGraphNodeLayer"

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], obj: Dict):
        matching_node_names = []
        for_each_node_top_down(obj, lambda node: self._apply_to_node(node, obj, inner_search_layers,
                                                                     user_arguments, matching_node_names))
        if len(matching_node_names) > 0:
            return matching_node_names
        else:
            return None

    def _apply_to_node(self, node, graph, inner_search_layers, user_arguments, matching_node_names: List[str]):
        if all(inner_search_layer.apply((node, graph), user_args)
               for inner_search_layer, user_args in zip(inner_search_layers, user_arguments)):
            matching_node_names.append(node["node_name"])


class InnerGraphNodeLayer(InnerSearchLayer, ABC):

    def apply(self, obj: Tuple[Dict, Dict], user_arguments: List[str]):
        """
        obj is a pair of (node, graph), both of the "graph_as_dict" dictionary format.
        """
        raise NotImplementedError()
