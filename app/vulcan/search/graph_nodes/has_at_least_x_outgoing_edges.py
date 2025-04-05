from typing import List, Dict, Tuple

from vulcan.data_handling.linguistic_objects.graphs.graph_as_dict import edge_label_has_inverse_direction, \
    CHILD_NODES_KEY, INCOMING_EDGE_KEY
from vulcan.search.graph_nodes.outer_graph_node_layer import InnerGraphNodeLayer
from vulcan.search.table_cells.outer_table_cells_layer import InnerTableCellsLayer


class HasAtLeastXOutgoingEdges(InnerGraphNodeLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """

    def apply(self, obj: Tuple[Dict, Dict], user_arguments: List[str]):
        if obj is None:
            return False
        node = obj[0]
        num_edges_required = int(user_arguments[0].strip())
        num_outgoing_edges_found = 0
        if edge_label_has_inverse_direction(node[INCOMING_EDGE_KEY]):
            num_outgoing_edges_found += 1
        for child in node[CHILD_NODES_KEY]:
            if not edge_label_has_inverse_direction(child[INCOMING_EDGE_KEY]):
                num_outgoing_edges_found += 1
        return num_outgoing_edges_found >= num_edges_required

    def get_description(self) -> str:
        return "This checks if a node has at least X outgoing edges (i.e. edges that have this node as source). "

    def get_label(self) -> List[str]:
        return ["Node has at least", "outgoing edges"]
