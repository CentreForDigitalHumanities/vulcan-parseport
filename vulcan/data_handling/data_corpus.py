from typing import List, Dict
import copy

from data_handling.instance_readers.amr_graph_instance_reader import AMRGraphStringInstanceReader, \
    AMRGraphInstanceReader
from data_handling.instance_readers.amtree_instance_reader import AMTreeInstanceReader, AMTreeStringInstanceReader
from data_handling.instance_readers.string_instance_reader import StringInstanceReader, TokenInstanceReader, \
    TokenizedStringInstanceReader
from data_handling.visualization_type import VisualizationType
from collections import OrderedDict
from data_handling.linguistic_objects.graphs.graph_as_dict import for_each_node_top_down
from data_handling.linguistic_objects.graphs.propbank_frame_reader import create_frame_to_definition_dict
import re

FORMAT_NAME_STRING = "string"
FORMAT_NAME_TOKEN = "token"
FORMAT_NAME_TOKENIZED_STRING = "tokenized_string"
FORMAT_NAME_AMTREE = "amtree"
FORMAT_NAME_AMTREE_STRING = "amtree_string"
FORMAT_NAME_GRAPH = "graph"
FORMAT_NAME_GRAPH_STRING = "graph_string"

class DataCorpus:

    def __init__(self):
        self.size = None
        self.slices = OrderedDict()
        self.linkers = []

    def add_slice(self, name, instances, visualization_type, label_alternatives=None, highlights=None,
                  mouseover_texts: Dict[str, str] = None):
        """
        Add a slice of data to the corpus.
        """
        self.slices[name] = CorpusSlice(name, instances, visualization_type, label_alternatives, highlights,
                                        mouseover_texts)

    def add_linker(self, linker):
        self.linkers.append(linker)


def from_dict_list(data: List[Dict], propbank_frames_path: str = None) -> DataCorpus:
    """
    Create a DataCorpus object from a dictionary.
    """
    print(propbank_frames_path)
    if propbank_frames_path:
        propbank_frames_dict = create_frame_to_definition_dict(propbank_frames_path)
    else:
        propbank_frames_dict = None
    data_corpus = DataCorpus()
    for entry in data:
        entry_type = entry.get('type', 'data')  # default to data
        if entry_type == 'data':

            name = entry['name']
            if not name:
                raise ValueError('Error when creating DataCorpus from dict list: "name" entry is required for'
                                 '"data" type dictionaries')
            instances = entry['instances']
            if not instances:
                raise ValueError('Error when creating DataCorpus from dict list: "instances" entry is required for'
                                 '"data" type dictionaries')

            if data_corpus.size:
                if len(entry['instances']) != data_corpus.size:
                    print(f"WARNING: number of instances for {name} ({len(instances)})"
                          f" does not match previously seen data ({data_corpus.size} instances).")
                    if len(entry['instances']) < data_corpus.size:
                        data_corpus.size = len(entry['instances'])
            else:
                data_corpus.size = len(entry['instances'])
                print(f"Retreived DataCorpus size from 'data' entry {name}: {data_corpus.size} instances")

            input_format = entry.get('format', 'string')
            instance_reader = get_instance_reader_by_name(input_format)
            instances = instance_reader.convert_instances(instances)

            label_alternatives = read_label_alternatives(entry)
            # data_corpus.size is now always defined here
            if label_alternatives is not None and data_corpus.size != len(label_alternatives):
                print(f"WARNING: number of label alternative entries for {name} ({len(label_alternatives)})"
                      f" does not match previously seen data ({data_corpus.size} instances).")
                if len(label_alternatives) < data_corpus.size:
                    data_corpus.size = len(label_alternatives)
            highlights = entry.get('highlights', None)
            if highlights is not None:
                check_is_list(highlights)
                if len(highlights) != data_corpus.size:
                    print(f"WARNING: number of highlight entries for {name} ({len(highlights)})"
                          f" does not match previously seen data ({data_corpus.size} instances).")
                    if len(highlights) < data_corpus.size:
                        data_corpus.size = len(highlights)
            mouseover_texts = None
            if input_format in [FORMAT_NAME_GRAPH, FORMAT_NAME_GRAPH_STRING] and propbank_frames_dict is not None:
                mouseover_texts = get_mouseover_texts(instances, propbank_frames_dict)
            data_corpus.add_slice(name, instances, instance_reader.get_visualization_type(), label_alternatives,
                                  highlights, mouseover_texts)
        elif entry_type == 'linker':
            # TODO: some sanity check that the linker refers to only existing names (but we may not have seen them yet, so check later?)
            data_corpus.add_linker(entry)
            if data_corpus.size:
                if data_corpus.size != len(entry['scores']):
                    print(f"WARNING: when creating DataCorpus from dict list: number of instances for"
                          f" linker \"{entry['name1']}\"--\"{entry['name2']}\" ({len(entry['scores'])})"
                          f" does not match previously seen data ({data_corpus.size} instances).")
                    if len(entry['scores']) < data_corpus.size:
                        data_corpus.size = len(entry['scores'])
            else:
                data_corpus.size = len(entry['scores'])
                print(f"Retreived DataCorpus size from 'data' entry \"{entry['name1']}\"--\"{entry['name2']}\":"
                      f" {data_corpus.size} instances")

        else:
            raise ValueError(f"Error when creating DataCorpus from dict list: unknown entry type '{entry_type}'")
    return data_corpus


def get_instance_reader_by_name(reader_name):
    """

    :param reader_name:
    :return:
    """
    if reader_name == FORMAT_NAME_STRING:
        return StringInstanceReader()
    elif reader_name == FORMAT_NAME_TOKEN:
        return TokenInstanceReader()
    elif reader_name == FORMAT_NAME_TOKENIZED_STRING:
        return TokenizedStringInstanceReader()
    elif reader_name == FORMAT_NAME_AMTREE:
        return AMTreeInstanceReader()
    elif reader_name == FORMAT_NAME_AMTREE_STRING:
        return AMTreeStringInstanceReader()
    elif reader_name == FORMAT_NAME_GRAPH:
        return AMRGraphInstanceReader()
    elif reader_name == FORMAT_NAME_GRAPH_STRING:
        return AMRGraphStringInstanceReader()


def read_label_alternatives(corpus_entry):
    """
    Creates a copy of the 'label_alternatives' entry in corpus_entry, where each label alternative has been
    processed by the appropriate InstanceReader.
    :param corpus_entry: An input corpus entry of type 'data'.
    :return: That created copy
    """
    if 'label_alternatives' in corpus_entry:
        label_alternatives = corpus_entry['label_alternatives']
        check_is_list(label_alternatives)
        ret = []
        for label_alternative_instance in label_alternatives:
            check_is_dict(label_alternative_instance)
            ret_instance = {}
            for node_name, node_label_alternatives in label_alternative_instance.items():
                ret_node = []
                check_is_list(node_label_alternatives)
                for node_label_alternative in node_label_alternatives:
                    check_is_dict(node_label_alternative)

                    ret_alt = copy.deepcopy(node_label_alternative)
                    instance_reader = get_instance_reader_by_name(ret_alt['format'])
                    ret_alt['label'] = instance_reader.convert_single_instance(ret_alt['label'])
                    ret_alt['format'] = instance_reader.get_visualization_type()
                    ret_node.append(ret_alt)
                ret_instance[node_name] = ret_node
            ret.append(ret_instance)
        return ret
    else:
        return None


def check_is_dict(object):
    if not isinstance(object, dict):
        raise ValueError(f"Error: object must be a dict, "
                         f"but was {type(object)}")


def check_is_list(object):
    if not isinstance(object, list):
        raise ValueError(f"Error: object must be a list, "
                         f"but was {type(object)}")

def get_mouseover_texts(graphs: List[Dict], propbank_frames_dict):
    ret = []
    for graph_as_dict in graphs:
        mouseover_texts_here = dict()
        for_each_node_top_down(graph_as_dict,
                               lambda node: add_propbank_frame_to_mouseover_if_applicable(node,
                                                                                          mouseover_texts_here,
                                                                                          propbank_frames_dict))
        ret.append(mouseover_texts_here)
    return ret


def add_propbank_frame_to_mouseover_if_applicable(node: Dict, mouseover_texts_here: Dict, propbank_frames_dict):
    node_label = node["node_label"]
    node_name = node["node_name"]
    if node_label in propbank_frames_dict:
        mouseover_texts_here[node_name] = propbank_frames_dict[node_label]


class CorpusSlice:

    def __init__(self,
                 name: str,
                 instances: List,
                 visualization_type: VisualizationType,
                 label_alternatives=None,
                 highlights=None,
                 mouseover_texts: List[Dict[str, str]] = None):
        self.name = name
        self.instances = instances
        self.visualization_type = visualization_type
        self.label_alternatives = label_alternatives
        self.highlights = highlights
        self.mouseover_texts = mouseover_texts
        if mouseover_texts is not None:
            print("mouseover texts", len(mouseover_texts), mouseover_texts[0])
        else:
            print("no mouseover_texts found in corpus slice ", name)
