from vulcan.data_handling.visualization_type import VisualizationType
from vulcan.search.graph_nodes.has_at_least_x_outgoing_edges import HasAtLeastXOutgoingEdges
from vulcan.search.graph_nodes.node_content_equals import NodeContentEquals
from vulcan.search.graph_nodes.outer_graph_node_layer import OuterGraphNodeLayer
from vulcan.search.string.outer_string_tokens_layer import OuterStringTokensLayer
from vulcan.search.string.token_content_equals import TokenContentEquals
from vulcan.search.string.token_content_matches import TokenContentMatches
from vulcan.search.table.column_count_at_least import ColumnCountAtLeast
from vulcan.search.table.outer_table_as_a_whole_layer import OuterTableAsAWholeLayer
from vulcan.search.table_cells.cell_content_equals import CellContentEquals
from vulcan.search.table_cells.cell_content_matches import CellContentMatches
from vulcan.search.table_cells.outer_table_cells_layer import OuterTableCellsLayer

OUTER_SEARCH_LAYERS = {
    "OuterStringTokensLayer": OuterStringTokensLayer(),
    "OuterTableCellsLayer": OuterTableCellsLayer(),
    "OuterTableAsAWholeLayer": OuterTableAsAWholeLayer(),
    "OuterGraphNodeLayer": OuterGraphNodeLayer()
}

INNER_SEARCH_LAYERS = {
    "CellContentEquals": CellContentEquals(),
    "CellContentMatches": CellContentMatches(),
    "NodeContentEquals": NodeContentEquals(),
    "ColumnCountAtLeast": ColumnCountAtLeast(),
    "HasAtLeastXOutgoingEdges": HasAtLeastXOutgoingEdges(),
    "TokenContentEquals": TokenContentEquals(),
    "TokenContentMatches": TokenContentMatches(),
}

OUTER_TO_INNER_SEARCH_LAYERS = {
    "OuterStringTokensLayer": ["TokenContentEquals", "TokenContentMatches"],
    "OuterTableCellsLayer": ["CellContentEquals", "CellContentMatches"],
    "OuterTableAsAWholeLayer": ["ColumnCountAtLeast"],
    "OuterGraphNodeLayer": ["NodeContentEquals", "HasAtLeastXOutgoingEdges"]
}

# TODO maybe do different ones for table and string, and for graph and tree
VISUALIZATION_TYPE_TO_OUTER_SEARCH_LAYERS = {
    VisualizationType.TABLE: ["OuterTableCellsLayer", "OuterTableAsAWholeLayer"],
    VisualizationType.GRAPH: ["OuterGraphNodeLayer"],
    VisualizationType.STRING: ["OuterStringTokensLayer"],
    VisualizationType.TREE: ["OuterGraphNodeLayer"],
    VisualizationType.LINKER: []
}
