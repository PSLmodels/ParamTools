from typing import Any, Iterable, List, Callable


from paramtools.tree import Tree
from paramtools.typing import ValueObject, CmpFunc


def select(
    value_objects: List[ValueObject],
    strict: bool,
    cmp_func: CmpFunc,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    """
    Query a parameter along some labels. If strict is True,
    all values in `labels` must be equal to the corresponding label
    in the parameter's "value" dictionary.

    Ignores state.

    Returns: [{"value": val, "label0": ..., }]
    """
    if not labels:
        return value_objects
    if tree is None:
        tree = Tree(vos=value_objects, label_grid=None)
    return tree.select(labels, cmp_func, strict)


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


def make_cmp_func(
    cmp: Callable[[Any, Iterable], bool],
    all_or_any: Callable[[Iterable], bool],
) -> CmpFunc:
    return lambda x, y: all_or_any(cmp(x, item) for item in y)


def select_eq(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, eq_func, labels, tree)


def select_ne(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, ne_func, labels, tree)


def select_gt(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, gt_func, labels, tree)


def select_gte(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, gte_func, labels, tree)


def select_gt_ix(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    cmp_list: List,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(
        value_objects,
        strict,
        lambda x, y: gt_ix_func(cmp_list, x, y),
        labels,
        tree,
    )


def select_lt(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, lt_func, labels, tree)


def select_lte(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    tree: Tree = None,
) -> List[ValueObject]:
    return select(value_objects, strict, lte_func, labels, tree)
