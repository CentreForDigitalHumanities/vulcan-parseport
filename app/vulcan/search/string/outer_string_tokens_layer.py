from abc import ABC
from typing import List, Any

from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer


class OuterStringTokensLayer(OuterSearchLayer):
    def get_description(self) -> str:
        return "This layer checks if any token in the string matches the given criteria," \
               " and highlights the tokens that do."

    def get_label(self) -> str:
        return "Any token in the string matches:"

    def get_id(self) -> str:
        return "OuterStringTokensLayer"

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], obj: List[str]):
        # print(obj)
        # TODO make different versions of this class for strings and tables
        # for row in obj:
        ret = []
        for i, cell in enumerate(obj):  # in row:
            result = True
            for inner_search_layer, user_args in zip(inner_search_layers, user_arguments):
                if inner_search_layer.apply(cell, user_args):
                    pass
                else:
                    result = False
                    print(cell, inner_search_layer.get_label(), user_args)
            if result:
                ret.append(i)
        if len(ret) > 0:
            return ret
        else:
            return None


class InnerTableCellsLayer(InnerSearchLayer, ABC):

    def apply(self, obj: str, user_arguments: List[str]):
        raise NotImplementedError()
