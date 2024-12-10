import pickle
from vulcan.file_loader import BasicLayout
from vulcan.data_handling.data_corpus import from_dict_list

def create_layout_from_input(parse_results: bytes) -> BasicLayout:
    """
    Create a layout from MG Parser's parse results (in binary/pickle format).
    """
    dict_lists = pickle.loads(parse_results)

    data_corpus = from_dict_list(
        data=dict_lists,
        propbank_frames_path=None,
        show_wikipedia=False
    )

    layout = BasicLayout(
        slices=data_corpus.slices.values(),
        linkers=data_corpus.linkers,
        corpus_size=data_corpus.size
    )

    return layout
