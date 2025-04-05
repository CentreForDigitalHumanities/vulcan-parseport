import io
import re
import random

from amconll import AMSentence, parse_amconll, Entry

from vulcan.data_handling.linguistic_objects.graphs.graph_as_dict import add_child, create_root, ROOT_EDGE_LABEL
from vulcan.data_handling.linguistic_objects.graphs.penman_converter import from_penman_graph
from penman import decode

ADDRESS_SEPARATOR = "."
SOURCE_PATTERN = re.compile(r"(?P<source><[a-zA-Z0-9]+>)")


def from_amtree(amtree: AMSentence):
    root_entry = None
    root_id = None
    for i, entry in enumerate(amtree.words):
        if entry.label == ROOT_EDGE_LABEL:
            root_entry = entry
            root_id = i + 1  # IDs in AMSentence are 1-based
            break
    if root_entry is None:
        print(amtree)
        raise Exception("No root entry found in AMSentence")
    address = ""
    all_addresses = []
    return _from_amtree_entry(root_entry, root_id, amtree, address, None, all_addresses)


def _from_amtree_entry(entry, entry_id, amtree, address, parent_in_result, all_addresses):
    """
    recursively builds the amtree below the given entry bottom up.
    Building the addresses is no longer necessary, but keeping it for now in case it becomes useful later.
    :param entry:
    :param entry_id:
    :param amtree:
    :param address:
    :param parent_in_result:
    :param all_addresses:
    :return:
    """
    all_addresses.append(address)
    node_label = get_graph_string_from_node_label(entry.fragment, entry)
    try:
        node_label = from_penman_graph(decode(node_label))
    except Exception as e:
        print("Error while decoding node label: " + node_label)
        node_label = from_penman_graph(decode("(e / ERROR)"))
    if parent_in_result is None:
        result = create_root(str(entry_id), node_label, label_type="GRAPH")
    else:
        result = add_child(parent_in_result, str(entry_id), node_label, entry.label, child_label_type="GRAPH")
    result["aligned_index"] = entry_id - 1  # IDs in AMSentence are 1-based
    children_in_amtree = []
    for i, potential_child in enumerate(amtree):
        if potential_child.head == entry_id:
            children_in_amtree.append((i + 1, potential_child))
    for i, (child_id, child) in enumerate(children_in_amtree):
        child_address = address + ADDRESS_SEPARATOR + str(i)
        _from_amtree_entry(child, child_id, amtree, child_address, result, all_addresses)
    return result


def from_string(string):
    return from_amtree(next(iter(parse_amconll(io.StringIO(string+"\n\n")))))


def get_graph_string_from_node_label(fragment, amconll_entry: Entry):
    node_label = fragment.replace("--LEX--", amconll_entry.lexlabel).replace("$LEMMA$", amconll_entry.lemma)\
                    .replace("$FORM$", amconll_entry.token)
    node_label = node_label.replace("<root>", "")
    return SOURCE_PATTERN.sub(r" / \g<source>", node_label)


def alignments_from_amtree(amtree: AMSentence):
    """
    dict maps address in am tree to index in sentence to score. Score is 1 for aligned node/token pairs, and not
    given (therefore assumed 0) for all others. This can be simplified now that am trees use
      indices from sentence as node names. But the current implementation is simple enough to keep it like this.
    :param amtree:
    :return:
    """
    amtree_as_dict = from_amtree(amtree)
    ret = {}
    _set_alignments_recursively(amtree_as_dict, ret)
    return ret


def _set_alignments_recursively(amtree_as_dict, alignment_dict):
    alignment_dict[amtree_as_dict["node_name"]] = {amtree_as_dict["aligned_index"]: 1}  # random.uniform(0.0, 1.0)}
    for child in amtree_as_dict["child_nodes"]:
        _set_alignments_recursively(child, alignment_dict)


def generate_random_label_alternatives(amtree: AMSentence):
    all_node_labels = []
    for entry in amtree.words:
        if entry.fragment != "_":
            all_node_labels.append(get_graph_string_from_node_label(entry.fragment, entry))
    label_alternatives = {}
    for zero_based_id, entry in enumerate(amtree):
        number_alternatives = min(len(all_node_labels), 3)
        last_score = random.uniform(0.0, 1.0)
        all_alternatives_here = []
        for alt_label in random.sample(all_node_labels, number_alternatives):
            label_alternative_here = {}
            all_alternatives_here.append(label_alternative_here)
            label_alternative_here["label"] = alt_label
            label_alternative_here["score"] = last_score
            last_score = random.uniform(0.0, last_score)
            label_alternative_here["format"] = "graph_string"
        label_alternatives[str(zero_based_id+1)] = all_alternatives_here
    return label_alternatives

