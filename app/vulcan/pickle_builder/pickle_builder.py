import pickle
import json
from typing import Dict, Any, Tuple, List, Union

from vulcan.data_handling.format_names import FORMAT_NAME_STRING, FORMAT_NAME_TOKENIZED_STRING, FORMAT_NAME_TOKEN, \
    FORMAT_NAME_OBJECT_TABLE, FORMAT_NAME_STRING_TABLE


class PickleBuilder:
    def __init__(self, name_to_format: Dict[str, str], linkers: List[Tuple[str, str, str]] = None):
        """

        :param name_to_format: For each thing you want to visualize (e.g. sentence, graph, tree), choose a name. You
         can choose any arbitrary name such as "Gold sentence" or "Input sentence" or "Predicted graph" or "tree 2".
         Now for each name, choose a format from the ones in vulcan.data_handling.format_names. For example, if you
         want to visualize an input sentence and a predicted graph, and you give the input sentence as a string and
         the graph in penman format, the name_to_format dictionary could look like this:
            {'Input sentence': 'string', 'Predicted graph': 'graph'}
         For data that is not just its own thing, such as dependency trees, linkers or node label alternatives,
         add them after the constructor with the respective "setup" methods.
        :param linkers: A list of tuples of the form (linker_name, name1, name2). Each tuple specifies a linker
        (alignment or attention) between two structures. The linker_name can be freely chosen (will show up in the
        interface under some conditions) and name1 and name2 are the names of the structures that are linked (from the
        name_to_format dictionary key set). Adding linkers is optional (but if you want to include them, you have to
        add them here). Note that name1 and name2 can be the same (e.g. for self-attention). The linker_name must be
         unique, and also different from all the names in name_to_format.
         """
        self.data = dict()
        for name, format in name_to_format.items():
            self.data[name] = dict({
                'type': 'data',
                'format': format,
                'instances': []
            })
        if linkers is not None:
            for linker_name, name1, name2 in linkers:
                assert name1 in self.data
                assert name2 in self.data
                assert linker_name not in self.data
                self.data[linker_name] = dict({
                    'type': 'linker',
                    'name1': name1,
                    'name2': name2,
                    'scores': []
                })

    def _setup_dependency_tree(self, linked_name: str):
        """
        Sets up the pickle builder to receive dependency trees; this is called automatically when adding a dependency
        tree to a set of structures for the first time.
        :param linked_name: The name of the string or table (e.g. tagged string) data that the dependency trees span.
        For example, if your name_to_format dictionary in the constructor contained 'Input sentence': 'string', then
        'Input sentence' would be a valid choice for linked_name here.
        :return: None
        """
        assert linked_name in self.data
        assert self.data[linked_name]['type'] == 'data'
        assert self.data[linked_name]['format'] in [FORMAT_NAME_STRING, FORMAT_NAME_TOKEN, FORMAT_NAME_TOKENIZED_STRING,
                                                    FORMAT_NAME_STRING_TABLE, FORMAT_NAME_OBJECT_TABLE]
        self.data[linked_name]["dependency_trees"] = []

    def add_instances_by_name(self, name_to_instance: Dict[str, Any], run_checks: bool = True):
        """
        Adds one corpus instance, including all its parts (graphs, sentences, trees, etc.) to the pickle builder.
        :param name_to_instance: Must contain entries for all names that were set up (via the constructor or
            one of the setup methods) and only those names.
        :param run_checks: If false, the condition on name_to_instance is not checked. If true, if the condition is
            not met, an AssertionError is raised.
        :return: None
        """
        if run_checks:
            names_match_data_structure = set(name_to_instance.keys()) == set(self.data.keys())
            assert names_match_data_structure
            assert self._instance_counts_are_in_sync()
        for name, instance in name_to_instance.items():
            self._add_instance_to_data(name, instance)

    def _add_instance_to_data(self, name: str, instance: Any):
        self.data[name]['instances'].append(instance)

    def add_instance_by_name(self, name: str, instance: Any, run_checks: bool = True):
        """
        Adds one part of a corpus instance, i.e. one graph, sentence, tree, etc. to the pickle builder.

        This method assumes that all instances are added synchronously, i.e. that for each name, one instance is added,
        and then again for each name, one instance is added, and so on. This is enforced in the method, and will raise
        an AssertionError if violated (to help you catch the situation where you accidentally get out of synch). If you
        are adding the instances in a different order, set run_checks to False.

        :param name: The name of the data structure, as given to the constructor or one of the setup methods.
        :param instance: The instance to be added
        :param run_checks: See main docstring text of this method.
        :return:
        """
        if run_checks:
            assert name in self.data
            min_number_of_instances_in_data = min(self._get_all_instance_counts())
            addition_will_break_sync = len(self.data[name]['instances']) > min_number_of_instances_in_data
            assert not addition_will_break_sync
        self._add_instance_to_data(name, instance)

    def _get_all_instance_counts(self):
        return [len(d['instances']) for d in self.data.values()]

    def _instance_counts_are_in_sync(self):
        return len(set(self._get_all_instance_counts())) == 1

    def add_dependency_tree_by_name(self,
                                    linked_name: str,
                                    dependency_tree: List[Tuple[int, int, str]],
                                    run_checks: bool = True):
        """
        Adds a dependency tree to the last instance in the list of instances for the given linked_name. For example,
        if you have an entry for "Input Sentence" in your name_to_format dictionary, calling this with linked_name
        "Input Sentence" will add a dependency tree to the last "Input Sentence" structure you added.
        :param linked_name: The table or string to add this dependency tree to. See setup_dependency_tree.
        :param dependency_tree: A list of dependency edges, with each edge being a triple (source, target, label).
            Source and target are 0-indexed, and label is a string.
        :param run_checks: If true, will check that adding this will not put the data out of sync.
        :return:
        """
        instances = self.data[linked_name]['instances']
        if 'dependency_trees' not in self.data[linked_name]:
            self._setup_dependency_tree(linked_name)
        dependency_trees = self.data[linked_name]['dependency_trees']
        self._keep_dependency_trees_synced(dependency_trees, instances, linked_name, run_checks)
        dependency_trees.append(dependency_tree)

    @staticmethod
    def _keep_dependency_trees_synced(dependency_trees, instances, linked_name, run_checks):
        while len(dependency_trees) + 1 < len(instances):
            dependency_trees.append([])
            if run_checks:
                print(f"Warning: adding empty dependency tree to keep data in sync. If all your instances in "
                      f"{linked_name} have dependency trees, then something went wrong; otherwise you can ignore"
                      f"this message. To disable this message, run with run_checks=False.")
        if run_checks:
            assert len(dependency_trees) < len(instances)

    def add_label_alternatives_by_name(self, structure_name: str, element_name: str,
                                       alternative_labels: List, label_formats: List[str],
                                       label_scores: List[float], run_checks: bool = True):
        """
        Adds a list of alternative labels for a given structure element (token, table cell, node or dependency edge;
        Graph and non-dependency-tree edge labels are not yet supported). This function will add the label alternatives
        to the *last added* instance of the given structure name. For example, if you have a entry for 'Input sentence'
        in your name_to_format dictionary, and they are strings, then calling this with structure_name='Input sentence',
        element_name='0', alternative_labels=['a', 'b'], label_formats=['string', 'string'], label_scores=[0.5, 0.5]
        will add the alternative labels 'a' and 'b' to the first token of the last added sentence, with scores 0.5 and
        0.5.
        :param structure_name: The name of the data structure that contains the element.
        :param element_name: The name of the element within the structure. Unique node name for graphs,
        the (0-based) index of the token for tokens, the (0-based) index of the table cell for table cells in the
        string format '(i, j)', and the (0-based) index of the dependency edge for dependency edges, in the string
        format ''. # TODO sync with online documentation, or just refer there.
        :param alternative_labels: The list of alternative labels.
        :param label_formats: A list of label formats, one for each alternative label. Must be one of the
            FORMAT_NAME_* constants.
        :param label_scores: A list of label scores, one for each alternative label.
        :param run_checks: If true, will check that the given structure name actually exists. Does *not* check that
        the element name exists within the structure.
        """
        assert len(alternative_labels) == len(label_formats) == len(label_scores)
        if run_checks:
            assert structure_name in self.data
            assert len(self.data[structure_name]['instances']) > 0
        if 'label_alternatives' not in self.data[structure_name]:
            self.data[structure_name]['label_alternatives'] = []
        while len(self.data[structure_name]['label_alternatives']) < len(self.data[structure_name]['instances']):
            self.data[structure_name]['label_alternatives'].append([])
        self.data[structure_name]['label_alternatives'][-1].append([{"label": lbl,
                                                                     "format": f,
                                                                     "score": s} for lbl, f, s in zip(alternative_labels,
                                                                                                      label_formats,
                                                                                                      label_scores)])

    def add_linker_score(self, linker_name: str, element_name_1: str, element_name_2: str,
                         score: Union[float, List[float], List[List[float]]],
                         run_checks: bool = True):
        """
        Adds a single linker score to the given linker. This function will add the score to the *last added* instances
        of the structure names of this linker. Will link the elements with the given names.
        For example, if you have a linker named "Alignment" for two structure names name1 = "Sentence" and name2 =
        "AMR Graph", then calling this with element_name_1 = "0", element_name_2 = "b2" and score 1.0 will add a linker
        score of 1.0 between the first token of the last added sentence and the node named "b2" in the last added AMR
        graph. To keep things in sync, note that the number of added sentences and added graphs in this example must be
        the same.

        The score can be a float, a list of floats (multiple attention heads) or a list of list of floats (multiple
        attention heads and multiple layers). In the last case, the outer list iterates over the layers, and the inner
        lists iterate over the attention heads.

        """
        if run_checks:
            assert linker_name in self.data
        instances1 = self.data[self.data[linker_name]['name1']]['instances']
        instances2 = self.data[self.data[linker_name]['name2']]['instances']
        if run_checks:
            assert len(instances1) == len(instances2)
        while len(self.data[linker_name]["scores"]) < len(instances1):
            self.data[linker_name]["scores"].append({})
        element_2_dict = self.data[linker_name]["scores"][-1].setdefault(element_name_1, {})
        element_2_dict[element_name_2] = score

    def _make_data_for_pickle(self, run_checks: bool = True):
        if run_checks:
            assert self._instance_counts_are_in_sync()
        data_for_pickle = []
        for name, data in self.data.items():
            # create new dict that also includes {'name': name}
            data_for_pickle.append(dict(data, name=name))
        return data_for_pickle

    def write(self, pickle_path: str):
        """
        :param pickle_path: Path to the pickle file that will be created.
        """
        data_for_pickle = self._make_data_for_pickle()
        with open(pickle_path, 'wb') as f:
            pickle.dump(data_for_pickle, f)

    def write_as_json(self, json_path: str):
        """
        :param json_path: Path to the json file that will be created.
        """
        data_for_pickle = self._make_data_for_pickle()
        with open(json_path, 'w') as f:
            json.dump(data_for_pickle, f)


def main():
    """
    This is a test for the PickleBuilder class and has no further purpose.
    """
    pb = PickleBuilder({'Sentence': 'string', 'Graph': 'graph_string'})
    pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                              'Graph': '(s / sentence :domain (t / this) :mod (t2 / test))'})

    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence that is missing a graph.'})
        raise Exception('Checks for correct set of names when adding multiple instances failed.')
    except AssertionError:
        pass

    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                                  'Graph': 'This is a test sentence.',
                                  'Sentence2': 'This is a test sentence that is too much.'})
        raise Exception('Checks for correct set of names when adding multiple instances failed.')
    except AssertionError:
        pass

    pb.add_instance_by_name('Sentence', 'This is another test sentence.')
    try:
        pb.write("test.pickle")
        raise Exception('Checks for writing failed.')
    except AssertionError:
        pass

    try:
        pb.add_instance_by_name('Sentence', 'This is another test sentence.')
        raise Exception('Asynchronicity checks for adding single instance failed.')
    except AssertionError:
        pass

    try:
        pb.add_instances_by_name({'Sentence': 'This is a test sentence.',
                                  'Graph': '(s / sentence :domain (t / this) :mod (t2 / test))'})
        raise Exception('Asynchronicity checks for adding multiple instances failed.')
    except AssertionError:
        pass

    pb.add_instance_by_name('Graph', '(s / sentence :domain (t / this) :mod (t2 / test) :mod (a / another))')

    pb.write("test.pickle")


if __name__ == '__main__':
    main()
