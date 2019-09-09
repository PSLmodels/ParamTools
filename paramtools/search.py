from collections import defaultdict
from typing import List

from paramtools.exceptions import ParamToolsError
from paramtools.typing import ValueObject


class Tree:
    def __init__(self, vos: List[ValueObject], label_grid: dict):
        self.vos = vos
        self.label_grid = label_grid
        self.tree = self.build()

    def build(self):
        search_tree = {}
        for ix, vo in enumerate(self.vos):
            for label, label_value in vo.items():
                if label == "value":
                    continue
                if label not in search_tree:
                    search_tree[label] = defaultdict(set)

                search_tree[label][label_value].add(ix)
        return search_tree

    def update(self, tree: "Tree"):
        # case where no labels
        not_matched = []
        if not self.tree and tree.vos:
            del self.vos[:]
            not_matched = list(range(len(tree.vos)))
        else:
            search_hits = {ix: set([]) for ix in range(len(tree.vos))}
            for label in self.label_grid:
                if label in tree.tree and label in self.tree:
                    for label_value in (
                        tree.tree[label].keys() & self.tree[label].keys()
                    ):
                        for new_ix in tree.tree[label][label_value]:
                            if new_ix in search_hits:
                                if search_hits[new_ix]:
                                    search_hits[new_ix] &= self.tree[label][
                                        label_value
                                    ]
                                else:
                                    search_hits[new_ix] |= self.tree[label][
                                        label_value
                                    ]
                    for label_value in (
                        tree.tree[label].keys() - self.tree[label].keys()
                    ):
                        for new_ix in tree.tree[label][label_value]:
                            search_hits.pop(new_ix)
                            not_matched.append(new_ix)
                elif label in self.tree:
                    unused_label = set.union(*self.tree[label].values())
                    for new_ix in search_hits:
                        if search_hits[new_ix]:
                            search_hits[new_ix] &= unused_label
                        else:
                            search_hits[new_ix] |= unused_label
                elif label in tree.tree:
                    raise ParamToolsError(
                        f"Label {label} was not defined in the defaults."
                    )

            to_delete = []
            for ix, search_hit_ixs in search_hits.items():
                if search_hit_ixs:
                    if tree.vos[ix]["value"] is not None:
                        for search_hit_ix in search_hit_ixs:
                            self.vos[search_hit_ix]["value"] = tree.vos[ix][
                                "value"
                            ]
                    else:
                        to_delete += search_hit_ixs
                else:
                    not_matched.append(ix)
            if to_delete:
                # Iterate in reverse so that indices point to the correct
                # value. If iterating ascending then the values will be shifted
                # towards the front of the list as items are removed.
                # print(to_delete, len(self.vos))
                for ix in sorted(set(to_delete), reverse=True):
                    del self.vos[ix]

        if not_matched:
            for ix in not_matched:
                if tree.vos[ix]["value"] is not None:
                    self.vos.append(tree.vos[ix])

    def select(self, labels, cmp_func, exact_match=False):
        search_hits = set([])
        if not labels:
            return self.vos
        if not self.tree:
            return self.vos
        for label, _label_value in labels.items():
            if not isinstance(_label_value, list):
                label_value = (_label_value,)
            else:
                label_value = _label_value
            label_search_hits = set([])
            if label in self.tree:
                for tree_label_value, ixs in self.tree[label].items():
                    match = cmp_func(tree_label_value, label_value)
                    if match:
                        label_search_hits |= ixs
                if search_hits:
                    search_hits &= label_search_hits
                else:
                    search_hits |= label_search_hits
            elif exact_match:
                raise KeyError(
                    f"Label {label} is not used for this parameter."
                )
        return [self.vos[ix] for ix in search_hits]
