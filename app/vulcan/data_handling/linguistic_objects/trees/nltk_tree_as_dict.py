from typing import Dict

from vulcan.data_handling.linguistic_objects.graphs.graph_as_dict import create_root, add_child

from nltk import Tree


def nltk_tree_to_dict(tree: Tree):
    root_label = tree.label()
    address = "0"
    ret = create_root(address, root_label)

    _add_descendants_recursively(ret, address, tree)

    return ret


def _add_descendants_recursively(node_as_dict: Dict, address: str, nltk_subtree: Tree):
    # print(nltk_subtree.label())
    for i, nltk_child in enumerate(nltk_subtree):
        # print(nltk_child)
        child_address = address + "." + str(i)
        child_label = nltk_child if isinstance(nltk_child, str) else nltk_child.label()
        child_as_dict = add_child(parent_node_as_dict=node_as_dict,
                  child_node_name=child_address,
                  child_node_label=child_label,
                  edge_label="")

        if isinstance(nltk_child, Tree):
            _add_descendants_recursively(child_as_dict, child_address, nltk_child)


def main():
    nltk_tree = Tree.fromstring('(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))')
    print(nltk_tree)
    print(nltk_tree_to_dict(nltk_tree))


if __name__ == "__main__":
    main()
