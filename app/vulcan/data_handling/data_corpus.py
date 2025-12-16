# Copyright 2022 Jonas Groschwitz
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file is derived from vulcan/data_handling/data_corpus.py
# Original source: https://github.com/jgroschwitz/vulcan

# MODIFICATIONS:
# - Fixed typo: "Retreived" -> "Retrieved" (2x).

from typing import List, Dict, Tuple, Any
import copy
import textwrap

from vulcan.data_handling.format_names import FORMAT_NAME_GRAPH, FORMAT_NAME_GRAPH_STRING, FORMAT_NAME_STRING, \
    FORMAT_NAME_TOKEN, FORMAT_NAME_TOKENIZED_STRING, FORMAT_NAME_NLTK_TREE, FORMAT_NAME_NLTK_TREE_STRING, \
    FORMAT_NAME_AMTREE, FORMAT_NAME_AMTREE_STRING, FORMAT_NAME_STRING_TABLE, FORMAT_NAME_OBJECT_TABLE
from vulcan.data_handling.instance_readers.amr_graph_instance_reader import AMRGraphInstanceReader, \
    AMRGraphStringInstanceReader
from vulcan.data_handling.instance_readers.amtree_instance_reader import AMTreeInstanceReader, \
    AMTreeStringInstanceReader
from vulcan.data_handling.instance_readers.nltk_instance_reader import NLTKTreeInstanceReader, \
    NLTKTreeStringInstanceReader
from vulcan.data_handling.instance_readers.string_instance_reader import StringInstanceReader, TokenInstanceReader, \
    TokenizedStringInstanceReader
from vulcan.data_handling.instance_readers.table_readers import StringTableInstanceReader, ObjectTableInstanceReader
from vulcan.data_handling.visualization_type import VisualizationType
from collections import OrderedDict
from vulcan.data_handling.linguistic_objects.graphs.graph_as_dict import for_each_node_top_down
from vulcan.data_handling.linguistic_objects.graphs.propbank_frame_reader import create_frame_to_definition_dict
import wikipedia


class DataCorpus:

    def __init__(self):
        self.size = None
        self.slices = OrderedDict()
        self.linkers = []

    def add_slice(self,
                  name: str,
                  instances: List[Any],
                  visualization_type: VisualizationType,
                  label_alternatives=None,
                  highlights=None,
                  mouseover_texts: Dict[str, str] = None,
                  dependency_trees: List[List[Tuple[int, int, str]]] = None):
        """
        Add a slice of data to the corpus.
        """
        self.slices[name] = CorpusSlice(name, instances, visualization_type, label_alternatives, highlights,
                                        mouseover_texts, dependency_trees)

    def add_linker(self, linker):
        self.linkers.append(linker)


def from_dict_list(data: List[Dict], propbank_frames_path: str = None,
                   show_wikipedia: bool = False) -> DataCorpus:
    """
    Create a DataCorpus object from a dictionary.
    """
    propbank_frames_dict = load_propbank_if_applicable(propbank_frames_path)

    data_corpus = DataCorpus()

    for entry in data:
        entry_type = entry.get('type', 'data')  # default to data

        if entry_type == 'data':
            load_data_entry(data_corpus, entry, propbank_frames_dict, show_wikipedia)

        elif entry_type == 'linker':
            load_linker_entry(data_corpus, entry)

        else:
            raise ValueError(f"Error when creating DataCorpus from dict list: unknown entry type '{entry_type}'")
    return data_corpus


def load_linker_entry(data_corpus, entry):
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
        print(f"Retrieved DataCorpus size from 'data' entry \"{entry['name1']}\"--\"{entry['name2']}\":"
              f" {data_corpus.size} instances")


def load_data_entry(data_corpus, entry, propbank_frames_dict, show_wikipedia):
    name = process_name(entry)
    input_format, instance_reader, instances = process_instances(data_corpus, entry, name)
    label_alternatives = process_label_alternatives(data_corpus, entry, name)
    dependency_trees = process_dependency_trees(data_corpus, entry, name)
    highlights = process_highlights(data_corpus, entry, name)
    mouseover_texts = process_mouseover_texts(input_format, instances, propbank_frames_dict, show_wikipedia)
    data_corpus.add_slice(name, instances, instance_reader.get_visualization_type(), label_alternatives,
                          highlights, mouseover_texts, dependency_trees)


def load_propbank_if_applicable(propbank_frames_path):
    if propbank_frames_path:
        print(f"Loading propbank frames from XML files in {propbank_frames_path}. This may take a minute or two...")
        propbank_frames_dict = create_frame_to_definition_dict(propbank_frames_path)
    else:
        propbank_frames_dict = None
    return propbank_frames_dict


def process_name(entry):
    name = entry['name']
    if not name:
        raise ValueError('Error when creating DataCorpus from dict list: "name" entry is required for'
                         '"data" type dictionaries')
    return name


def process_instances(data_corpus, entry, name):
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
        print(f"Retrieved DataCorpus size from 'data' entry {name}: {data_corpus.size} instances")
    input_format = entry.get('format', 'string')
    instance_reader = get_instance_reader_by_name(input_format)
    instances = instance_reader.convert_instances(instances)
    return input_format, instance_reader, instances


def process_mouseover_texts(input_format, instances, propbank_frames_dict, show_wikipedia):
    mouseover_texts = None
    if input_format in [FORMAT_NAME_GRAPH, FORMAT_NAME_GRAPH_STRING]:
        mouseover_texts = get_mouseover_texts(instances, propbank_frames_dict, show_wikipedia)
    return mouseover_texts


def process_highlights(data_corpus, entry, name):
    highlights = entry.get('highlights', None)
    if highlights is not None:
        check_is_list(highlights)
        if len(highlights) != data_corpus.size:
            print(f"WARNING: number of highlight entries for {name} ({len(highlights)})"
                  f" does not match previously seen data ({data_corpus.size} instances).")
            if len(highlights) < data_corpus.size:
                data_corpus.size = len(highlights)
    return highlights


def process_label_alternatives(data_corpus, entry, name):
    label_alternatives = read_label_alternatives(entry)
    # data_corpus.size is now always defined here
    if label_alternatives is not None and data_corpus.size != len(label_alternatives):
        print(f"WARNING: number of label alternative entries for {name} ({len(label_alternatives)})"
              f" does not match previously seen data ({data_corpus.size} instances).")
        if len(label_alternatives) < data_corpus.size:
            data_corpus.size = len(label_alternatives)
    return label_alternatives


def process_dependency_trees(data_corpus, entry, name):
    dependency_trees = read_dependency_trees(entry)
    # data_corpus.size is now always defined here
    if dependency_trees is not None and data_corpus.size != len(dependency_trees):
        print(f"WARNING: number of dependency trees for {name} ({len(dependency_trees)})"
              f" does not match previously seen data ({data_corpus.size} instances).")
        if len(dependency_trees) < data_corpus.size:
            data_corpus.size = len(dependency_trees)
    return dependency_trees


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


def read_dependency_trees(corpus_entry):
    if 'dependency_trees' in corpus_entry:
        dependency_trees = corpus_entry['dependency_trees']
        check_is_list(dependency_trees)
        return dependency_trees
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


def get_mouseover_texts(graphs: List[Dict], propbank_frames_dict=None, do_wiki_lookup: bool = True):
    if propbank_frames_dict is None and not do_wiki_lookup:
        return None
    ret = []
    if do_wiki_lookup:
        print("Loading wikipedia summaries. This can take a while!")
    for i, graph_as_dict in enumerate(graphs):
        mouseover_texts_here = dict()
        if propbank_frames_dict is not None:
            for_each_node_top_down(graph_as_dict,
                                   lambda node: add_propbank_frame_to_mouseover_if_applicable(node,
                                                                                              mouseover_texts_here,
                                                                                              propbank_frames_dict))
        if do_wiki_lookup:
            if i % 20 == 0:
                print(f"Looking up wikipedia summaries for graph {i} of {len(graphs)} (printing every 20 graphs).")
            for_each_node_top_down(graph_as_dict,
                                   lambda node: add_wiki_lookup_to_mouseover_if_applicable(node, mouseover_texts_here))
        ret.append(mouseover_texts_here)
    return ret


def add_propbank_frame_to_mouseover_if_applicable(node: Dict, mouseover_texts_here: Dict, propbank_frames_dict):
    node_label = node["node_label"]
    node_name = node["node_name"]
    if node_label in propbank_frames_dict:
        mouseover_texts_here[node_name] = propbank_frames_dict[node_label]


def add_wiki_lookup_to_mouseover_if_applicable(node: Dict, mouseover_texts_here: Dict):
    # c.f. https://stackoverflow.com/questions/4460921/extract-the-first-paragraph-from-a-wikipedia-article-python
    node_label = node["node_label"]
    node_name = node["node_name"]
    # actually adding to the child node if this is a wiki edge
    node_name = node["node_name"]
    # print(node["incoming_edge"])
    if node["incoming_edge"] == "wiki":
        try:
            wiki_summary = wikipedia.summary(node_label, sentences=2)
            # print(wiki_summary)
            mouseover_texts_here[node_name] = textwrap.fill(wiki_summary, 70)
        except Exception:
            mouseover_texts_here[node_name] = "No Wikipedia entry found for " + node_label

class CorpusSlice:

    def __init__(self,
                 name: str,
                 instances: List,
                 visualization_type: VisualizationType,
                 label_alternatives=None,
                 highlights=None,
                 mouseover_texts: List[Dict[str, str]] = None,
                 dependency_trees: List[List[Tuple[int, int, str]]]=None):
        self.name = name
        self.instances = instances
        self.visualization_type = visualization_type
        self.label_alternatives = label_alternatives
        self.highlights = highlights
        self.mouseover_texts = mouseover_texts
        # if mouseover_texts is not None:
        #     print("mouseover texts", len(mouseover_texts), mouseover_texts[0])
        # else:
        #     print("no mouseover_texts found in corpus slice ", name)
        self.dependency_trees = dependency_trees


def get_instance_reader_by_name(reader_name):
    """

    :param reader_name:
    :return:
    """
    # TODO this has a duplicate in ObjectTableInstanceReader to avoid circular imports.
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
