from typing import List, Any


class InnerSearchLayer:
    """
    Interface for the inner search layer. An inner search layer e.g. checks if a node or token
     matches a certain criteria.
    """

    def get_description(self) -> str:
        """
        :return: A description of this search layer. This provides more in-depth description, in a mouse-over tooltip.
        """
        raise NotImplementedError()

    def get_label(self) -> List[str]:
        """
        :return: A short label for this search layer. This is used in the search bar. The label is actually a list of
        strings. In between each entry in this list, a variable will be inserted that is filled out in the search bar.
        For example, if this returns ["has label", ""], the search bar will show "has label [__]", where [__] is a
        text field.
        """
        raise NotImplementedError()

    def apply(self, obj: Any, user_arguments: List[str], **kwargs):
        """
        :param obj: the object to check. This can be a macro-object like a graph, or a micro-object like a node,
        depending on the outer search layer.
        :param user_arguments: The arguments that the user put into the search bar. These arguments correspond
        to the gaps in the label returned by get_label().
        :param kwargs: Whatever information this search layer is provided with. Defined by the outer search layer.
        :return: True if the object matches the search criteria, False otherwise.
        """
        raise NotImplementedError()
