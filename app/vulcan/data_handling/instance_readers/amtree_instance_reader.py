from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.data_handling.linguistic_objects.trees.am_tree_as_dict import from_string, from_amtree


class AMTreeInstanceReader(InstanceReader):
    """
    InstanceReader for string data. Assumes each instance is a string, and splits it along spaces to obtain a string
    list internally.
    """

    def convert_single_instance(self, instance):
        return from_amtree(instance)

    def get_visualization_type(self):
        return VisualizationType.TREE


class AMTreeStringInstanceReader(InstanceReader):
    """
    InstanceReader for string data. Assumes each instance is a string, and splits it along spaces to obtain a string
    list internally.
    """

    def convert_single_instance(self, instance):
        return from_string(instance)

    def get_visualization_type(self):
        return VisualizationType.TREE
