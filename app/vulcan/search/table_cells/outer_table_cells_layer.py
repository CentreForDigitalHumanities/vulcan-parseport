from abc import ABC
from typing import List, Any, Tuple

from vulcan.data_handling.linguistic_objects.table import cell_coordinates_to_cell_name
from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer


class OuterTableCellsLayer(OuterSearchLayer):
    def get_description(self) -> str:
        return "This layer checks if any cell in a table matches the given criteria, and highlights the cells that do."

    def get_label(self) -> str:
        return "Any cell in the table matches:"

    def get_id(self) -> str:
        return "OuterTableCellsLayer"

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], obj: List[List[Tuple]]):
        # print(obj)
        # TODO make different versions of this class for strings and tables
        ret = []
        for j, column in enumerate(obj):
            for i, cell in enumerate(column):  # in row:
                result = True
                for inner_search_layer, user_args in zip(inner_search_layers, user_arguments):
                    if inner_search_layer.apply(cell, user_args):
                        pass
                    else:
                        result = False
                        break
                        # print(cell, inner_search_layer.get_label(), user_args)
                if result:
                    print("len obj", len(obj))
                    print("len row", len(column))
                    print(f"i: {i}, j: {j}, cell: {str(cell)}")
                    ret.append(cell_coordinates_to_cell_name(i, j))
        if len(ret) > 0:
            return ret
        else:
            return None


class InnerTableCellsLayer(InnerSearchLayer, ABC):

    def apply(self, obj: str, user_arguments: List[str]):
        raise NotImplementedError()
