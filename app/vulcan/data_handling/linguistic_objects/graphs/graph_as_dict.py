"""
This defines a graph format. A graph is represented as a tree, with some nodes representing reentrancies
in that they link to other nodes in the tree. Each node has a node_name that is unique in the graph
(but not in the tree: reentrancy-nodes share the node name with the "actual" node they link to). All
non-reentrancy nodes have a node label. Every node in the tree has an incoming edge (traversing an edge
in inverse direction is encoded with the "-of" notation as in AMR). Each node further has a list of all
its child nodes. This way, a graph is represented using only dicts, lists and strings, which can all
be sent as-is to javascript on the client side via socket-IO.
"""


ROOT_EDGE_LABEL = "ROOT"
NODE_NAME_KEY = "node_name"
NODE_LABEL_KEY = "node_label"
LABEL_TYPE_KEY = "label_type"
INCOMING_EDGE_KEY = "incoming_edge"
IS_REENTRANCY_KEY = "is_reentrancy"
CHILD_NODES_KEY = "child_nodes"


def create_root(node_name, node_label, label_type="STRING"):
    return create_node(node_name, node_label, ROOT_EDGE_LABEL, label_type=label_type)


def create_node(node_name, node_label, incoming_edge_label, is_reentrancy=False, label_type="STRING"):
    ret = dict()
    ret["node_name"] = node_name
    ret["node_label"] = node_label
    if not is_reentrancy:
        ret["label_type"] = label_type
    ret["incoming_edge"] = incoming_edge_label
    ret["is_reentrancy"] = is_reentrancy
    ret["child_nodes"] = []
    return ret


def create_reentrancy(node_name, incoming_edge_label):
    return create_node(node_name, None, incoming_edge_label, is_reentrancy=True)


def add_child(parent_node_as_dict, child_node_name, child_node_label, edge_label, child_label_type="STRING"):
    child = create_node(child_node_name, child_node_label, edge_label, label_type=child_label_type)
    parent_node_as_dict["child_nodes"].append(child)
    return child


def add_reentrancy_as_child(parent_node_as_dict, child_node_name, edge_label):
    child = create_reentrancy(child_node_name, edge_label)
    parent_node_as_dict["child_nodes"].append(child)
    return child


def for_each_node_top_down(graph_as_dict, node_consumer):
    node_consumer(graph_as_dict)
    for child in graph_as_dict["child_nodes"]:
        for_each_node_top_down(child, node_consumer)


def edge_label_has_inverse_direction(edge_label: str):
    return edge_label.endswith("-of")



