from typing import List, Dict, Tuple

from vulcan.search.graph_nodes.outer_graph_node_layer import InnerGraphNodeLayer
from vulcan.search.table_cells.outer_table_cells_layer import InnerTableCellsLayer


class NodeContentEquals(InnerGraphNodeLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """

    def apply(self, obj: Tuple[Dict, Dict], user_arguments: List[str]):
        if obj is None:
            return False
        if obj[0] is None:
            print("Warning: null node in search")
            print(obj)
        if obj[0]["node_label"] is None:
            # then we have an unlabeled node, or a reentrancy. either way, we don't want to match it
            return False
        if user_arguments[0] is None:
            print("Warning: user argument")
            print(user_arguments)
        return obj[0]["node_label"].strip().lower() == user_arguments[0].strip().lower()

    def get_description(self) -> str:
        return "This checks if a node is labeled with the given string (modulo casing and outer whitespace)."

    def get_label(self) -> List[str]:
        return ["Node has label", ""]
