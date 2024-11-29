import json
import pickle

from vulcan.data_handling.data_corpus import from_dict_list
from vulcan.server.basic_layout import BasicLayout


def create_layout_from_filepath(input_path: str, is_json_file: bool = False, propbank_path: str = None,
                                show_wikipedia_articles: bool = False):
    input_dicts = load_input_file(input_path, is_json_file)

    data_corpus = from_dict_list(input_dicts, propbank_frames_path=propbank_path,
                                 show_wikipedia=show_wikipedia_articles)

    layout = BasicLayout(data_corpus.slices.values(), data_corpus.linkers, data_corpus.size)

    return layout


def load_input_file(input_path, is_json_file):
    if is_json_file:
        with open(input_path, "r") as f:
            input_dicts = json.load(f)
    else:
        with open(input_path, "rb") as f:
            input_dicts = pickle.load(f)
    return input_dicts
