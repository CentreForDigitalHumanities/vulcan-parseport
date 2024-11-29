import pickle
from typing import Iterable, List

from vulcan.data_handling.linguistic_objects.trees.am_tree_as_dict import SOURCE_PATTERN
from vulcan.pickle_builder.pickle_builder import PickleBuilder

import penman

from amconll import parse_amconll, AMSentence, Entry


def main():
    edge_label_dicts = read_custom_scores_file("../am-parser/output/little_prince/edge_label_scores.txt")
    print(len(edge_label_dicts))

    head_index_dicts = read_custom_scores_file("../am-parser/output/little_prince/edge_existence_scores.txt")
    print(len(head_index_dicts))

    supertag_dicts = read_custom_scores_file("../am-parser/output/little_prince/supertag_scores.txt")
    print(len(supertag_dicts))

    gold_amrs = penman.load("../am-parser/output/little_prince/goldAMR.txt")
    print(len(gold_amrs))

    predicted_amrs = penman.load("../am-parser/output/little_prince/parserOut.txt")
    print(len(predicted_amrs))

    with open("../am-parser/output/little_prince/AMR-2020_pred.amconll", "r", encoding="utf-8") as f:
        amconll_sents = [s for s in parse_amconll(f)]  # make it so we can close the file
    print(len(amconll_sents))

    pickle_builder = PickleBuilder({"Gold graph": "graph", "Predicted graph": "graph",
                                    "AM tree": "amtree", "Sentence": "object_table"})

    pickle_builder_simple = PickleBuilder({"Gold graph": "graph", "Predicted graph": "graph",
                                           "Sentence": "tokenized_string"})

    label_alternatives_data = []

    for el_dict, head_dict, st_dict, gold_amr, predicted_amr, amconll_sent in zip(edge_label_dicts, head_index_dicts,
                                                                                 supertag_dicts, gold_amrs,
                                                                                 predicted_amrs, amconll_sents):
        label_alternatives_data.append(make_label_alternatives_dict(el_dict, head_dict, st_dict, amconll_sent))
        tagged_sentence = []
        sentence = []
        for entry in amconll_sent.words:
            sentence.append(entry.token)
            tagged_token = []
            tagged_sentence.append(tagged_token)
            tagged_token.append(("token", entry.token))
            tagged_token.append(("token", make_head_info_label(entry.head, amconll_sent)))
            if entry.fragment == "_":
                tagged_token.append(("token", entry.fragment))
            else:
                tagged_token.append(("graph_string", relabel_supertag(entry.fragment, entry)))

        pickle_builder.add_instances_by_name({"Gold graph": gold_amr,
                                              "Predicted graph": predicted_amr,
                                              "AM tree": amconll_sent,
                                              "Sentence": tagged_sentence})
        pickle_builder_simple.add_instances_by_name({"Gold graph": gold_amr,
                                                     "Predicted graph": predicted_amr,
                                                     "Sentence": sentence})
        deptree = make_dependency_tree(amconll_sent)
        pickle_builder.add_dependency_tree_by_name("Sentence", deptree)

    final_data = pickle_builder._make_data_for_pickle()
    for data_dict in final_data:
        if data_dict["name"] == "Sentence":
            data_dict["label_alternatives"] = label_alternatives_data

    with open("little_prince.pickle", "wb") as f:
        pickle.dump(final_data, f)

    pickle_builder_simple.write("little_prince_simple.pickle")


def make_dependency_tree(amconll_sent):
    ret = []
    for i, entry in enumerate(amconll_sent.words):
        if entry.label not in ["IGNORE", "ROOT"]:
            ret.append((entry.head - 1, i, entry.label))
    ret += [(-1, i, "ROOT") for i, entry in enumerate(amconll_sent.words) if entry.label == "ROOT"]
    return ret


def make_head_info_label(head, amconll_sent: AMSentence):
    if head == 0:
        return str(head - 1)
    elif head >= len(amconll_sent.words):
        return f"Out of bounds ({head-1})"
    else:
        return f"{str(head - 1)} ({amconll_sent.words[head - 1].token})"


def make_label_alternatives_dict(el_dict, head_dict, st_dict, amconll_sent):
    ret = {}
    for i, el in enumerate(el_dict[1:len(amconll_sent.words) + 1]):
        edge_name = get_edge_name(i, amconll_sent)
        label_alternatives_here = []
        ret[edge_name] = label_alternatives_here
        for edge_label, score in el.items():
            label_alternatives_here.append({"score": score,
                                            "label": edge_label,
                                            "format": "string"})
    for i, head in enumerate(head_dict[1:len(amconll_sent.words) + 1]):
        cell_name = str((1, i))
        label_alternatives_here = []
        ret[cell_name] = label_alternatives_here
        for head_index, score in head.items():
            label_alternatives_here.append({"score": score,
                                            "label": make_head_info_label(int(head_index), amconll_sent),
                                            "format": "token"})

    for i, st in enumerate(st_dict[1:len(amconll_sent.words) + 1]):
        cell_name = str((2, i))  # TODO if the above gets commented back out, change to (1, i)
        label_alternatives_here = []
        ret[cell_name] = label_alternatives_here
        for supertag, score in st.items():
            supertag = supertag.split("--TYPE--")[0]
            if supertag == "_" or supertag == "NONE":
                label_alternatives_here.append({"score": score,
                                                "label": supertag,
                                                "format": "token"})
            else:
                label_alternatives_here.append({"score": score,
                                                "label": relabel_supertag(supertag, amconll_sent.words[i]),
                                                "format": "graph_string"})

    return ret


def relabel_supertag(supertag, amconll_entry: Entry):
    if supertag == "_" or supertag == "NONE":
        return supertag
    else:
        supertag = supertag.replace("--LEX--", amconll_entry.lexlabel).replace("$LEMMA$", amconll_entry.lemma)\
                    .replace("$FORM$", amconll_entry.token)
        supertag = supertag.replace("<root>", "")
        return SOURCE_PATTERN.sub(r" / \g<source>", supertag)


def get_edge_name(target_pos, amconll_sent: AMSentence):
    head_pos = amconll_sent.get_heads()[target_pos] - 1
    return f"depedge_{head_pos}_{target_pos}"


def read_custom_scores_file(file_path: str):
    edge_label_dicts = []
    current_edge_label_dicts_by_token = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.strip() == "":
                edge_label_dicts.append(current_edge_label_dicts_by_token)
                current_edge_label_dicts_by_token = []
            else:
                current_edge_label_dicts_by_token.append(get_scores_from_line(line))
    return edge_label_dicts


def get_scores_from_line(line: str):
    bits = line.strip().split("\t|\t")
    ret = {}
    for bit in bits:
        last_colon = bit.rfind(":")
        ret[bit[:last_colon]] = float(bit[last_colon + 1:])
    return ret


if __name__ == '__main__':
    main()
