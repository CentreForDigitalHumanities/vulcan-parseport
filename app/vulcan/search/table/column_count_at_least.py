from typing import List

from vulcan.search.table.outer_table_as_a_whole_layer import InnerTableLayer
from vulcan.search.table_cells.outer_table_cells_layer import InnerTableCellsLayer


class ColumnCountAtLeast(InnerTableLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """

    def apply(self, obj: List[List[str]], user_arguments: List[str]):
        # read first argument as integer
        try:
            min_column_count = int(user_arguments[0])
        except ValueError:
            # TODO error handling: send some feedback to client
            return False
        return obj is not None and len(obj[0]) >= min_column_count

    def get_description(self) -> str:
        return "Checks minimum sentence length / table width."

    def get_label(self) -> List[str]:
        return ["The sentence has at least length", " (or the table has at least this many columns)"]
