from typing import Any, Iterable, List


from paramtools.tree import Tree
from paramtools.typing import ValueObject, CmpFunc


def select(
    value_objects: List[ValueObject],
    exact_match: bool,
    cmp_func: CmpFunc,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    """
    Query a parameter along some labels. If exact_match is True,
    all values in `labels` must be equal to the corresponding label
    in the parameter's "value" dictionary.

    Ignores state.

    Returns: [{"value": val, "label0": ..., }]
    """
    if not labels:
        return value_objects
    if tree is None:
        tree = Tree(vos=value_objects, label_grid=None)
    return tree.select(labels, cmp_func, exact_match)


def eq_func(x: Any, y: Iterable) -> bool:
    return x in y


def ne_func(x: Any, y: Iterable) -> bool:
    return x not in y


def gt_func(x: Any, y: Iterable) -> bool:
    return all(x > item for item in y)


def gte_func(x: Any, y: Iterable) -> bool:
    return all(x >= item for item in y)


def gt_ix_func(cmp_list: list, x: Any, y: Iterable) -> bool:
    x_val = cmp_list.index(x)
    return all(x_val > cmp_list.index(item) for item in y)


def lt_func(x, y) -> bool:
    return all(x < item for item in y)


def lte_func(x, y) -> bool:
    return all(x <= item for item in y)


def select_eq(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, exact_match, eq_func, labels, tree)


def select_gt(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, exact_match, gt_func, labels, tree)


def select_gte(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, exact_match, gte_func, labels, tree)


def select_gt_ix(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    cmp_list: List,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(
        value_objects,
        exact_match,
        lambda x, y: gt_ix_func(cmp_list, x, y),
        labels,
        tree,
    )


def select_lt(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, exact_match, lt_func, labels, tree)


def select_lte(
    value_objects: List[ValueObject],
    exact_match: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, exact_match, lte_func, labels, tree)
