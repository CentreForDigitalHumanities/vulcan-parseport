import penman
from graph_as_dict import create_root, add_child, add_reentrancy_as_child
from penman_converter import StaticAliasCounter


def make_penman_example_as_dict():
    penman_graph = penman.decode("(l / like-01 :ARG0 (g / giraffe) :ARG1 (c / car :mod (f / fast)))")
    return StaticAliasCounter.from_penman_graph(penman_graph)


def make_penman_example_with_reentrancy_as_dict():
    penman_graph = penman.decode("(l / want-01 :ARG0 (g / giraffe) :ARG1 (d / drive-01 :ARG0 g :ARG1 (c / car :mod (f / fast))))")
    return StaticAliasCounter.from_penman_graph(penman_graph)


def make_example_graph_as_dict():
    root = create_root("l", "love-01")
    dog = add_child(root, "d", "dog", "ARG0")
    cow = add_child(root, "c", "cow", "ARG1")
    little = add_child(dog, "l2", "little", "mod")
    print(root)
    return root


def make_example_graph_with_reentrancy_as_dict():
    root = create_root("w", "yearn-01")
    dragon = add_child(root, "d", "dragon", "ARG0")
    fly = add_child(root, "f", "fly-01", "ARG1")
    little = add_child(dragon, "l", "little", "mod")
    reentrancy_at_raven = add_reentrancy_as_child(fly, "d", "ARG0")
    print(root)
    return root