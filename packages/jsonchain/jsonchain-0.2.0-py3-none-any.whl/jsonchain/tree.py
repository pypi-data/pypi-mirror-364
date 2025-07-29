from copy import copy
from typing import Hashable, Union, Optional, Any
import operator
import deepmerge

def compare_tree_values(
    tree_a: dict | list,
    tree_b: dict | list,
    levels_a: list[Hashable | None],
    levels_b: list[Hashable | None],
    leaf_a: Hashable,
    leaf_b: Hashable,
    compare_func: Union[str, callable, None],
    comparison_key: Optional[Hashable]= None,
    *args,
    **kwargs,
) -> dict:
    """
    Returns a dictionary tree keyed according to 
    'tree_a': the first tree to compare
    'tree_b': the second tree to compare
    'levels_a': The levels to iterate through in order to access the leaf keys in
        'leaves_a'. If a level is listed is None, then all keys at that level will
        be iterated over.
    'levels_b': The levels to iterate through in order to access the leaf keys in
        'leaves_b'. If a level is listed is None, then all keys at that level will
        be iterated over.
    'leaf_a': The leaf in the tree_a to compare to the leaf in tree_b
    'leaf_b': The leaf in the tree_b to compare to the leaf in tree_a
    'compare_func': Either one of 
        {'div', 'sub', 'add', 'mult', 'ge', 'le', 'lt', 'gt', 'eq', 'ne'}, None, or a 
        user-supplied callable whose call signature takes the values of the individual
        elements of 'leaf_a' as the first param, the individual elements of 'leaf_b'
        as the second param. Optionally, args and kwargs can be passed and they
        will be passed on to the callable.
        If compare_func is None, then no function is called and the values for
        comparison are both entered into the returned dictionary but without
        a special comparison operation performed. If compare_func is None,
        'comparison_key' is ignored.
    'comparison_key': If provided, will serve as the key for the comparison value.
        If None, then the name of the comparison operator will used instead.
    """
    ops = {
        "div": operator.truediv,
        "sub": operator.sub,
        "add": operator.add,
        "mul": operator.mul,
        "ge": operator.ge,
        "le": operator.le,
        "lt": operator.lt,
        "gt": operator.gt,
        "eq": operator.eq,
        "ne": operator.ne,
    }
    env_acc = {}
    # If we are at the last branch...
    subtree_a = retrieve_leaves(tree_a, levels_a, leaf_a)
    subtree_b = retrieve_leaves(tree_b, levels_b, leaf_b)

    branch_a = trim_branches(subtree_a, levels_a)
    branch_b = trim_branches(subtree_b, levels_b)

    for trunk in branch_a.keys():
        value_a = branch_a[trunk]
        value_b = branch_b[trunk]
        env_acc.setdefault(trunk, {})
        env_acc[trunk].setdefault(leaf_a, value_a)
        env_acc[trunk].setdefault(leaf_b, value_b)
        comparison_operator = ops.get(compare_func, compare_func)
        if comparison_operator is not None:
            compared_value = comparison_operator(value_a, value_b)
            if comparison_key is None:
                comparison_key = comparison_operator.__name__
            env_acc[trunk].setdefault(comparison_key, compared_value)
    return env_acc


def trim_branches(
    tree: dict | list,
    levels: list[Hashable | None],
):
    """
    Returns a copy of the 'tree' but with the branches in 
    'levels' trimmed off.
    """
    trimmed = tree.copy()
    for i in range(len(levels)):
        leaf = levels.pop()
        trimmed = retrieve_leaves(trimmed, levels, leaf=leaf)
    return trimmed


def retrieve_leaves(
    tree: dict | list, 
    levels: list[Hashable | None], 
    leaf: list[Hashable] | Hashable | None,
) -> dict:
    """
    Envelopes the tree at the leaf node with 'agg_func'.
    """
    env_acc = {}
    key_error_msg = (
        "Key '{level}' does not exist at this level. Available keys: {keys}. "
        "Perhaps not all of your tree elements have the same keys. Try enveloping over trees "
        "that have the same branch structure and leaf names."
    )
    # If we are at the last branch...
    if not levels:
        if leaf is None:
            return tree
        if isinstance(leaf, list):
            leaf_values = {}
            for leaf_elem in leaf:
                try:
                    tree[leaf_elem]
                except KeyError:
                    raise KeyError(key_error_msg.format(level=leaf_elem, keys=list(tree.keys())))
                leaf_values.update({leaf_elem: tree[leaf_elem]})
        else:
            try:
                tree[leaf]
            except KeyError:
                raise KeyError(key_error_msg.format(level=leaf, keys=list(tree.keys())))
            leaf_values = tree[leaf]
        return leaf_values
    else:
        # Otherwise, pop the next level and dive into the tree on that branch
        level = levels[0]
        if level is not None:
            try:
                tree[level]
            except KeyError:
                raise KeyError(key_error_msg.format(level=level, keys=list(tree.keys())))
            env_acc.update({level: retrieve_leaves(tree[level], levels[1:], leaf)})
            return env_acc
        else:
            # If None, then walk all branches of this node of the tree
            if isinstance(tree, list):
                tree = {idx: leaf for idx, leaf in enumerate(tree)}
            for k, v in tree.items():
                env_acc.update({k: retrieve_leaves(v, levels[1:], leaf)})
            return env_acc
        

def extract_keys(
        object: dict[str, Any], 
        key_name: str,
        include_startswith: Optional[str] = None,
        exclude_startswith: Optional[str] = None,
    ) -> list[dict[str, Any]]:
    """
    Returns a list of dicts where each dict has a key of 'key_name'
    and a value of one of the keys of 'object'.

    e.g.
    object = {"key1": value, "key2": value, "key3": value}
    key_name = "label"

    extract_keys(object, key_name) # [{"label": "key1"}, {"label": "key2"}, {"label": "key3"}]

    'include_startswith': If provided, will only include keys that start with this string.
    'exclude_startswith': If provided, will exclude all keys that start with this string.

    If both 'include_startswith' and 'exclude_startswith' are provided, exclude is executed
    first.
    """
    shortlist = []
    for key in object.keys():
        if exclude_startswith is not None and key.startswith(exclude_startswith):
            continue
        else:
            shortlist.append(key)

    acc = []
    for key in shortlist:
        if include_startswith is not None and key.startswith(include_startswith):
            acc.append({key_name: key})
        elif include_startswith is None:
            acc.append({key_name: key})

    return acc

    

def merge_trees(trees: list[dict[str, dict]]) -> dict[str, dict]:
    """
    Merges all of the tress (dictionaries) in 'result_trees'. 

    This is different than a typical dictionary merge (e.g. a | b)
    which will merge dictionaries with different keys but will over-
    write values if two keys are the same.

    Instead, it crawls each branch of the tree and merges the data
    within each branch, no matter how deep the branches go.
    """
    acc = {}
    for result_tree in trees:
        acc = deepmerge.always_merger.merge(acc, result_tree)
    return acc