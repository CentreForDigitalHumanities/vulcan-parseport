from typing import Any, List

from vulcan.search.inner_search_layer import InnerSearchLayer


class OuterSearchLayer:
    """
    Interface for the outer search layer. An outer search layer e.g. iterates over all nodes in a graph, applying
    an inner search layer to each node.
    """

    def get_description(self) -> str:
        """
        :return: A description of this search layer. This provides more in-depth description, in a mouse-over tooltip.
        """
        raise NotImplementedError()

    def get_label(self) -> str:
        """
        :return: A short label for this search layer. This is used in the search bar.
        """
        raise NotImplementedError()

    def apply(self, inner_search_layers: List[InnerSearchLayer], user_arguments: List[List[str]], obj: Any):
        """
        :param inner_search_layers: All the inner search layers that must match here.
        :param user_arguments: The arguments that the user put into the search bar. These arguments correspond
        to the gaps in the label returned by each InnerSearchLayer's get_label().
        :param obj: The object to check.
        :return: A (possibly empty) set of highlighted node names if the object matches the search criteria,
         None otherwise.
        """
        raise NotImplementedError()
