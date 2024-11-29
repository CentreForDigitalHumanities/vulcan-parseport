# Just a string. Will be split into tokens along whitespace.
FORMAT_NAME_STRING = "string"

# A single token (python type: str). Will not be split.
FORMAT_NAME_TOKEN = "token"

# A list of tokens (python type: List[str]). Will not be split further.
FORMAT_NAME_TOKENIZED_STRING = "tokenized_string"

# An NLTK tree.
FORMAT_NAME_NLTK_TREE = "nltk_tree"

# A string encoding of an NLTK tree.
FORMAT_NAME_NLTK_TREE_STRING = "nltk_tree_string"

# A graph; specifically, a Graph object from the penman pip package.
FORMAT_NAME_GRAPH = "graph"

# A graph in penman notation (a string object)
FORMAT_NAME_GRAPH_STRING = "graph_string"

# An AMSentence object of the amconll pip package.
FORMAT_NAME_AMTREE = "amtree"

# An AM tree as spelled out in a string in the amconll file format (c.f. the amconll pip package).
FORMAT_NAME_AMTREE_STRING = "amtree_string"

# A table of string values (python type: List[List[str]]). First index is column, second index is row.
#   This is also the format to use for tagged sentences.
FORMAT_NAME_STRING_TABLE = "string_table"

# A table of objects (python type: List[List[Tuple[str, Any]]]). First index is column, second index is row.
#  In the tuples, the first entry is again a format name from this file, and the second entry is an object of that
#  format. This is also the format to use for tagged sentences, if the tags are not just strings.
FORMAT_NAME_OBJECT_TABLE = "object_table"
