from typing import List, Any, Optional

from vulcan.search.inner_search_layer import InnerSearchLayer
from vulcan.search.outer_search_layer import OuterSearchLayer
from vulcan.search.table_cells.cell_content_equals import CellContentEquals
from vulcan.search.table_cells.outer_table_cells_layer import OuterTableCellsLayer
from vulcan.data_handling.data_corpus import CorpusSlice
from vulcan.data_handling.visualization_type import VisualizationType



class BasicLayout:

    def __init__(self, slices, linkers, corpus_size):
        self.layout: List[List[CorpusSlice]] = []
        last_active_row = []
        self.layout.append(last_active_row)
        for slice in slices:
            if get_slice_screen_width(slice) >= 1.0:
                self.layout.append([slice])
                continue
            current_fill = sum([get_slice_screen_width(s) for s in last_active_row])
            if current_fill + get_slice_screen_width(slice) > 1:
                last_active_row = [slice]
                self.layout.append(last_active_row)
            else:
                last_active_row.append(slice)
        if [] in self.layout:
            self.layout.remove([])  # if last_active_row is still empty, we remove it
        self.linkers = linkers
        self.corpus_size = corpus_size

    def get_visualization_type_for_slice_name(self, slice_name: str) -> Optional[VisualizationType]:
        for row in self.layout:
            for slc in row:
                if slc.name == slice_name:
                    return slc.visualization_type
        return None


def get_slice_screen_width(corpus_slice: CorpusSlice) -> float:
    if corpus_slice.visualization_type in [VisualizationType.STRING, VisualizationType.TABLE]:
        return 1.0
    elif corpus_slice.visualization_type in [VisualizationType.TREE, VisualizationType.GRAPH]:
        return 0.3
