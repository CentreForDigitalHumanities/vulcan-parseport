from conllu import parse

from vulcan.data_handling.format_names import FORMAT_NAME_STRING_TABLE
from vulcan.pickle_builder.pickle_builder import PickleBuilder

"""
Converts a CoNLL-U file to a Vulcan (pickle) file.
"""


def conllu_sentences_to_vulcan_pickle(sentences, output_pickle_path):
    pickle_builder = PickleBuilder({"Sentence": FORMAT_NAME_STRING_TABLE})

    for sentence in sentences:
        table = get_table_from_conll_sentence(sentence)
        pickle_builder.add_instance_by_name("Sentence", table)
        dependency_tree = get_dependency_edges_from_conll_sentence(sentence)
        pickle_builder.add_dependency_tree_by_name("Sentence", dependency_tree)

    pickle_builder.write(output_pickle_path)


def get_table_from_conll_sentence(sentence):
    table = []
    for token in sentence:
        if isinstance(token["id"], int):
            table.append([token["form"], token["lemma"], token["upos"], token["xpos"]])
    return table


def get_dependency_edges_from_conll_sentence(sentence):
    dependency_tree = []
    for token in sentence:
        # format is "source", "target", "label"
        if token["head"] is not None and isinstance(token["id"], int):
            dependency_tree.append((token["head"] - 1, token["id"] - 1, token["deprel"]))
    return dependency_tree


def conllu_path_to_vulcan_pickle(input_conllu_path, output_pickle_path):
    with open(input_conllu_path, "r", encoding="utf-8") as f:
        sentences = parse(f.read())
    conllu_sentences_to_vulcan_pickle(sentences, output_pickle_path)


if __name__ == "__main__":
    # get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Converts a CoNLL-U file to a Vulcan (pickle) file.")
    parser.add_argument("input_conllu_path", help="Path to the input CoNLL-U file.")
    parser.add_argument("output_pickle_path", help="Path to the output pickle file.")
    args = parser.parse_args()
    conllu_path_to_vulcan_pickle(args.input_conllu_path, args.output_pickle_path)
