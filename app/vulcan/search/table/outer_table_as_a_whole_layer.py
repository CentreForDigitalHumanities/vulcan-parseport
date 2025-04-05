from abc import ABC
from typing import List, Any

from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer


class OuterTableAsAWholeLayer(OuterSearchLayer):
    def get_description(self) -> str:
        return "This layer checks if the sentence (or table) itself matches a given criterion."

    def get_label(self) -> str:
        return "The sentence/table as a whole matches:"

    def get_id(self) -> str:
        return "OuterTableAsAWholeLayer"

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], obj: List[List[str]]):
        for inner_search_layer, user_args in zip(inner_search_layers, user_arguments):
            if not inner_search_layer.apply(obj, user_args):
                return None
        return []


class InnerTableLayer(InnerSearchLayer, ABC):

    def apply(self, obj: List[List[str]], user_arguments: List[str]):
        raise NotImplementedError()
