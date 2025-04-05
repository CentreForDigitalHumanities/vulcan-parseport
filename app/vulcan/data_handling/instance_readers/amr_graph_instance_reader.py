from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
from penman import decode


class AMRGraphInstanceReader(InstanceReader):
    """
    InstanceReader for AMR graphs. Specifically, expects the instances to be in the graph format of the penman library.
    """

    def convert_single_instance(self, instance):
        return from_penman_graph(instance)

    def get_visualization_type(self):
        return VisualizationType.GRAPH


class AMRGraphStringInstanceReader(InstanceReader):
    """
    InstanceReader for AMR graphs. Specifically, expects the instances to be string linearizations of the AMRs, as they
    would occur in the AMR corpus.
    """

    def convert_single_instance(self, instance):
        return from_penman_graph(decode(instance))

    def get_visualization_type(self):
        return VisualizationType.TREE
