from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.data_handling.linguistic_objects.trees.nltk_tree_as_dict import nltk_tree_to_dict
from nltk import Tree


class NLTKTreeInstanceReader(InstanceReader):
    """
    InstanceReader for NLTK trees. Assumes each instance is an nltk.Tree.
    """

    def convert_single_instance(self, instance):
        return nltk_tree_to_dict(instance)

    def get_visualization_type(self):
        return VisualizationType.TREE


class NLTKTreeStringInstanceReader(InstanceReader):
    """
    InstanceReader for NLTK trees in string form. Assumes each instance is a string representing an nltk.Tree.
    """

    def convert_single_instance(self, instance):
        return nltk_tree_to_dict(Tree.fromstring(instance))

    def get_visualization_type(self):
        return VisualizationType.TREE
