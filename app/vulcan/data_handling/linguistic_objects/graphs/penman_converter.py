import penman
import vulcan.data_handling.linguistic_objects.graphs.graph_as_dict as graph_as_dict

MADEUP_NODENAME_BASE = "alias"


class StaticAliasCounter:
    alias_count = 0


def from_penman_graph(penman_graph):
    """

    :param penman_graph:
    :return: A "graph-as-dict" equivalent to the input.
    """
    top_node = get_root_node(penman_graph)
    agenda = Agenda(top_node)
    while not agenda.is_empty():
        node = agenda.pop_next()
        explore_outgoing_edges(node, penman_graph, agenda)
        explore_incoming_edges(node, penman_graph, agenda)
        process_attribute_edges(node, penman_graph, agenda)

    return agenda.get_result()


def get_root_node(penman_graph):
    top_node = lookup_penman_node(penman_graph, penman_graph.top)
    return top_node


def explore_outgoing_edges(node, penman_graph, agenda):
    for edge in penman_graph.edges(source=node.source):
        if not agenda.has_seen_edge(edge):
            agenda.log_edge(edge)
            edge_label_reformatted = reformat_edge_label(edge)
            parent_node_name = edge.source
            child_node_name = edge.target
            explore_child(child_node_name, parent_node_name, edge_label_reformatted, penman_graph, agenda)


def explore_incoming_edges(node, penman_graph, agenda):
    for edge in penman_graph.edges(target=node.source):
        if not agenda.has_seen_edge(edge):
            agenda.log_edge(edge)
            edge_label_reformatted = reformat_edge_label(edge) + "-of"
            parent_node_name = edge.target
            child_node_name = edge.source
            explore_child(child_node_name, parent_node_name, edge_label_reformatted, penman_graph, agenda)


def explore_child(child_node_name, parent_node_name, edge_label_reformatted, penman_graph, agenda):
    if agenda.has_seen_node(child_node_name):
        create_reentrancy_node(parent_node_name, child_node_name, edge_label_reformatted, agenda)
    else:
        create_node_and_add_to_agenda(parent_node_name, child_node_name, edge_label_reformatted, penman_graph, agenda)


def create_reentrancy_node(parent_node_name, child_node_name, edge_label_reformatted, agenda):
    graph_as_dict.add_reentrancy_as_child(agenda.node_name2graph_as_dict[parent_node_name],
                                          child_node_name, edge_label_reformatted)


def create_node_and_add_to_agenda(parent_node_name, child_node_name, edge_label_reformatted, penman_graph, agenda):
    child_instance_penman = lookup_penman_node(penman_graph, child_node_name)
    parent_as_dict = agenda.get_graph_as_dict_for_node_name(parent_node_name)
    child_as_dict = create_child_and_add_to_graph(child_instance_penman.target, parent_as_dict, child_node_name,
                                                  edge_label_reformatted)
    agenda.log_node(child_as_dict, child_instance_penman, child_node_name)


def create_child_and_add_to_graph(node_label, parent_as_dict, child_node_name, edge_label_reformatted):
    child_as_dict = graph_as_dict.add_child(parent_as_dict, child_node_name,
                                            node_label, edge_label_reformatted)
    return child_as_dict


def process_attribute_edges(node, penman_graph, agenda):
    for edge in penman_graph.attributes(source=node.source):
        if not agenda.has_seen_edge(edge):
            agenda.log_edge(edge)
            edge_label_reformatted = reformat_edge_label(edge)
            child_nodename = create_alias()
            parent_as_dict = agenda.get_graph_as_dict_for_node_name(edge.source)
            graph_as_dict.add_child(parent_as_dict, child_nodename, edge.target, edge_label_reformatted)
            # don't need to worry about encountering the node name again here, or about exploring below the attribute


def create_alias():
    StaticAliasCounter.alias_count += 1
    return MADEUP_NODENAME_BASE + str(StaticAliasCounter.alias_count)


def reformat_edge_label(edge):
    return edge.role[1:]


def lookup_penman_node(penman_graph, node_name):
    return [n for n in penman_graph.instances() if n.source == node_name][0]


class Agenda:

    def __init__(self, top_node):
        """
        Initializes the agenda with the root of the penman graph.
        :param top_node:
        """
        self.top_node_name = top_node.source
        self.node_name2graph_as_dict = dict()
        self.node_name2graph_as_dict[self.top_node_name] = graph_as_dict.create_root(self.top_node_name, top_node.target)
        self.nodes_to_explore = [top_node]
        self.seen_node_names = []
        self.seen_edges = []

    def is_empty(self):
        return len(self.nodes_to_explore) <= 0

    def pop_next(self):
        return self.nodes_to_explore.pop(0)

    def get_result(self):
        return self.node_name2graph_as_dict[self.top_node_name]

    def get_graph_as_dict_for_node_name(self, node_name):
        return self.node_name2graph_as_dict[node_name]

    def has_seen_node(self, node_name):
        return node_name in self.seen_node_names

    def log_node(self, node_as_dict, node_instance_penman, node_name):
        self.seen_node_names.append(node_name)
        self.node_name2graph_as_dict[node_name] = node_as_dict
        self.nodes_to_explore.append(node_instance_penman)

    def has_seen_edge(self, edge):
        return edge in self.seen_edges

    def log_edge(self, edge):
        self.seen_edges.append(edge)


if __name__ == "__main__":
    graph = penman.decode("(l / like-01 :ARG0 (g / giraffe) :ARG1 (c / car :mod (f / fast :quant 3)))")
    # print(graph.instances())
    # print(graph.edges())
    # print(graph.attributes())
    result = from_penman_graph(graph)
    print(result)
