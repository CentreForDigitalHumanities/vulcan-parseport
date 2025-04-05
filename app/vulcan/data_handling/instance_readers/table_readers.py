from vulcan.data_handling.format_names import FORMAT_NAME_STRING, FORMAT_NAME_TOKEN, FORMAT_NAME_TOKENIZED_STRING, \
    FORMAT_NAME_NLTK_TREE, FORMAT_NAME_NLTK_TREE_STRING, FORMAT_NAME_GRAPH, FORMAT_NAME_GRAPH_STRING, \
    FORMAT_NAME_AMTREE, FORMAT_NAME_AMTREE_STRING, FORMAT_NAME_STRING_TABLE, FORMAT_NAME_OBJECT_TABLE

from vulcan.data_handling.instance_readers.amr_graph_instance_reader import AMRGraphInstanceReader, \
    AMRGraphStringInstanceReader
from vulcan.data_handling.instance_readers.amtree_instance_reader import AMTreeInstanceReader, \
    AMTreeStringInstanceReader
from vulcan.data_handling.instance_readers.instance_reader import InstanceReader
from vulcan.data_handling.instance_readers.nltk_instance_reader import NLTKTreeInstanceReader, \
    NLTKTreeStringInstanceReader
from vulcan.data_handling.instance_readers.string_instance_reader import StringInstanceReader, TokenInstanceReader, \
    TokenizedStringInstanceReader
from vulcan.data_handling.visualization_type import VisualizationType


class StringTableInstanceReader(InstanceReader):
    """
    InstanceReader for tables in string form. Assumes each instance is a table of strings (i.e. List[List[str]]).
    """

    def convert_single_instance(self, instance):
        return instance

    def get_visualization_type(self):
        return VisualizationType.TABLE


class ObjectTableInstanceReader(InstanceReader):
    """
    InstanceReader for tables in object form. Assumes each instance is a table of objects (i.e. List[List[Tuple[str, Any]]]),
    where in the tuple, the first entry is a string from format_names.py, and the second entry is an object of that format.
    """

    def convert_single_instance(self, instance):
        return [[_convert_object(format_name, obj) for format_name, obj in row] for row in instance]

    def get_visualization_type(self):
        return VisualizationType.TABLE


def _convert_object(format_name, obj):
    instance_reader = get_instance_reader_by_name(format_name)
    return instance_reader.get_visualization_type(), instance_reader.convert_single_instance(obj)


def get_instance_reader_by_name(reader_name):
    """

    :param reader_name:
    :return:
    """
    # TODO this is a duplicate of the function in  data_corpus to avoid circular imports.
    #  There should be a better solution!
    if reader_name == FORMAT_NAME_STRING:
        return StringInstanceReader()
    elif reader_name == FORMAT_NAME_TOKEN:
        return TokenInstanceReader()
    elif reader_name == FORMAT_NAME_TOKENIZED_STRING:
        return TokenizedStringInstanceReader()
    elif reader_name == FORMAT_NAME_NLTK_TREE:
        return NLTKTreeInstanceReader()
    elif reader_name == FORMAT_NAME_NLTK_TREE_STRING:
        return NLTKTreeStringInstanceReader()
    elif reader_name == FORMAT_NAME_GRAPH:
        return AMRGraphInstanceReader()
    elif reader_name == FORMAT_NAME_GRAPH_STRING:
        return AMRGraphStringInstanceReader()
    elif reader_name == FORMAT_NAME_AMTREE:
        return AMTreeInstanceReader()
    elif reader_name == FORMAT_NAME_AMTREE_STRING:
        return AMTreeStringInstanceReader()
    elif reader_name == FORMAT_NAME_STRING_TABLE:
        return StringTableInstanceReader()
    elif reader_name == FORMAT_NAME_OBJECT_TABLE:
        return ObjectTableInstanceReader()