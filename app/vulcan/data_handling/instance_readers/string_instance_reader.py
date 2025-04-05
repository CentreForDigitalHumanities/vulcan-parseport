from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.visualization_type import VisualizationType


class StringInstanceReader(InstanceReader):
    """
    InstanceReader for string data. Assumes each instance is a string, and splits it along spaces to obtain a string
    list internally.
    """

    def convert_single_instance(self, instance):
        return instance.split(" ")

    def get_visualization_type(self):
        return VisualizationType.STRING


class TokenizedStringInstanceReader(InstanceReader):
    """
    Expects as input a list of strings, i.e. an already tokenized sentence
    """

    def convert_single_instance(self, instance):
        return instance

    def get_visualization_type(self):
        return VisualizationType.STRING


class TokenInstanceReader(InstanceReader):
    """
    InstanceReader that treats its input as a single token (as opposed to a sequence of tokens, as in the
    StringInstanceReader). Specifically, simply returns the instance as is.
    """
    def convert_single_instance(self, instance):
        return instance

    def get_visualization_type(self) -> VisualizationType:
        return VisualizationType.STRING
