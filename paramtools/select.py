def select(value_objects, exact_match, cmp_func, agg_cmp_func, labels):
    """
    Query a parameter along some labels. If exact_match is True,
    all values in `labels` must be equal to the corresponding label
    in the parameter's "value" dictionary.

    Ignores state.

    Returns: [{"value": val, "label0": ..., }]
    """
    ret = []
    for value_object in value_objects:
        matches = []
        for label_name, label_value in labels.items():
            if label_name in value_object or exact_match:
                if isinstance(label_value, list):
                    match = cmp_func(value_object[label_name], label_value)
                else:
                    match = cmp_func(value_object[label_name], (label_value,))
                matches.append(match)
        if agg_cmp_func(matches):
            ret.append(value_object)
    return ret


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
    return select(value_objects, exact_match, eq_func, all, labels)


def select_ne(value_objects, exact_match, labels):
    return select(value_objects, exact_match, ne_func, any, labels)


def select_gt(value_objects, exact_match, labels):
    return select(value_objects, exact_match, gt_func, all, labels)


def select_gt_ix(value_objects, exact_match, labels, cmp_list):
    return select(
        value_objects,
        exact_match,
        lambda x, y: gt_ix_func(cmp_list, x, y),
        all,
        labels,
    )
