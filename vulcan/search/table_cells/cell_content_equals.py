from typing import List

from search.table_cells.outer_table_cells_layer import InnerTableCellsLayer


class CellContentEquals(InnerTableCellsLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """
    
    def apply(self, obj: str, user_arguments: List[str]):
        return obj.strip().lower() == user_arguments[0].strip().lower()

    def get_description(self) -> str:
        return "This checks if the cell content equals the given string (modulo casing and outer whitespace)."

    def get_label(self) -> List[str]:
        return ["Cell content equals", ""]
