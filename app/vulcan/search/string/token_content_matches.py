import re
from typing import List

from vulcan.search.table_cells.outer_table_cells_layer import InnerTableCellsLayer


class TokenContentMatches(InnerTableCellsLayer):
    """
    This checks if the cell content equals the given string (modulo casing and outer whitespace).
    """

    def apply(self, obj: str, user_arguments: List[str]):
        return obj is not None and re.compile(user_arguments[0]).match(obj)

    def get_description(self) -> str:
        return "This checks if the token contains a match for the given regular expression."

    def get_label(self) -> List[str]:
        return ["Token contains match for ", "(regular expression)"]
