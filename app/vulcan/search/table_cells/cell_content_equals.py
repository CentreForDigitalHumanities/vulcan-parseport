from typing import List

from vulcan.search.table_cells.outer_table_cells_layer import InnerTableCellsLayer
from vulcan.data_handling.visualization_type import VisualizationType


class CellContentEquals(InnerTableCellsLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """

    def apply(self, obj: str, user_arguments: List[str]):
        if isinstance(obj, tuple) and len(obj) == 2 and obj[0] == VisualizationType.STRING:
            obj = obj[1]
        else:
            return False
        return obj is not None and isinstance(obj, str) and obj.strip().lower() == user_arguments[0].strip().lower()

    def get_description(self) -> str:
        return "This checks if the cell content equals the given string (modulo casing and outer whitespace)."

    def get_label(self) -> List[str]:
        return ["Cell content equals", ""]
