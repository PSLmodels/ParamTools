from typing import Any, Iterable, List, Callable
import warnings


from paramtools.typing import ValueObject, CmpFunc
from paramtools import values


def select(
    value_objects: List[ValueObject],
    strict: bool,
    cmp_func: CmpFunc,
    labels: dict,
    tree=None,
    op=None,
) -> List[ValueObject]:
    """
    Deprecated. Use Values instead.
    """
    warnings.warn("The select module is deprecated. Use Values instead.")
    assert op, "Op is required."
    values_ = values.Values(value_objects)
    res = []
    for label, value in labels.items():
        if isinstance(value, list):
            if op == "ne":
                agg_func = values.intersection
            else:
                agg_func = values.union
            res.append(
                agg_func(
                    values_._cmp(op, strict, **{label: element})
                    for element in value
                )
            )
        else:
            res.append(values_._cmp(op, strict, **{label: value}))
    return list(values.intersection(res))


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
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, eq_func, labels, tree, op="eq")


def select_ne(
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, ne_func, labels, tree, op="ne")


def select_gt(
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, gt_func, labels, tree, op="gt")


def select_gte(
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, gte_func, labels, tree, op="gte")


def select_gt_ix(
    value_objects: List[ValueObject],
    strict: bool,
    labels: dict,
    cmp_list: List,
    tree=None,
) -> List[ValueObject]:
    raise Exception("select_gt_ix is deprecated. Use Values instead.")


def select_lt(
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, lt_func, labels, tree, op="lt")


def select_lte(
    value_objects: List[ValueObject], strict: bool, labels: dict, tree=None
) -> List[ValueObject]:
    return select(value_objects, strict, lte_func, labels, tree, op="lte")
