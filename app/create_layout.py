import json
from vulcan.server.basic_layout import BasicLayout
from vulcan.data_handling.data_corpus import from_dict_list

def create_layout_from_input(data: list[dict]) -> BasicLayout:
    """
    Create a layout from the given data.

    Simplified version of vulcan.file_loader.create_layout_from_filepath.
    """
    input_dicts = json.load(data)

    data_corpus = from_dict_list(
        data=input_dicts,
        propbank_frames_path=None,
        show_wikipedia=False
    )

    layout = BasicLayout(
        slices=data_corpus.slices.values(),
        linkers=data_corpus.linkers,
        corpus_size=data_corpus.size
    )

    return layout
    