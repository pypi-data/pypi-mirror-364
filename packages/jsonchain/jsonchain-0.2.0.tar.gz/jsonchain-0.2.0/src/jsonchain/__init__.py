"""
A small package to aid in the use of the chaining techniques taught by Structural Python
"""

__version__ = "0.2.0"


from .io import (load_json, dump_json)
from .envelope import envelope_tree
from .tree import (
    compare_tree_values,
    extract_keys,
    trim_branches,
    retrieve_leaves
)
import tables