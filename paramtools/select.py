from paramtools.tree import Tree


def select(value_objects, exact_match, cmp_func, labels, tree=None):
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


def eq_func(x, y):
    return x in y


def ne_func(x, y):
    return x not in y


def gt_func(x, y):
    return all(x > item for item in y)


def gt_ix_func(cmp_list, x, y):
    x_val = cmp_list.index(x)
    return all(x_val > cmp_list.index(item) for item in y)


def select_eq(value_objects, exact_match, labels):
    return select(value_objects, exact_match, eq_func, labels)


def select_gt(value_objects, exact_match, labels):
    return select(value_objects, exact_match, gt_func, labels)


def select_gt_ix(value_objects, exact_match, labels, cmp_list):
    return select(
        value_objects,
        exact_match,
        lambda x, y: gt_ix_func(cmp_list, x, y),
        labels,
    )
