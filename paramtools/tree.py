from collections import defaultdict
from typing import List

from paramtools.exceptions import ParamToolsError
from paramtools.typing import ValueObject, CmpFunc


class Tree:
    """
    Builds a tree structure for more efficient searching. The structure
    is:
    label
        --> label value
            --> set of indices corresponding to value object that has
                a label with this value.
    """

    def __init__(self, vos: List[ValueObject], label_grid: dict):
        self.vos = vos
        self.label_grid = dict(label_grid or {}, _auto=[False, True])
        self.tree = None
        self.new_values = None
        self.needs_build = True

    def init(self):
        """
        Initializes tree data structure. Trees are lazy and this method
        should be called before the tree's methods are used.

        Cases:
        1. If needs_build is false, no action is taken and the existing
            tree is returned.

        2. If the tree has not yet been there are no new values, the tree
            is built from self.vos.

        3. If tree has already been initialized and there are new values,
            the tree is updated with the new values.
        """
        if not self.needs_build:
            return self.tree
        if self.new_values and self.tree:
            ixs = self.new_values
            search_tree = self.tree
        else:
            search_tree = {}
            ixs = range(len(self.vos))
        for ix in ixs:
            vo = self.vos[ix]
            for label, label_value in vo.items():
                if label == "value":
                    continue
                if label not in search_tree:
                    search_tree[label] = defaultdict(set)
                search_tree[label][label_value].add(ix)
        self.tree = search_tree
        self.needs_build = False
        self.new_values = None
        return self.tree

    def update(self, tree: "Tree") -> List[ValueObject]:
        """
        Update this tree's value objects with value objects from the
        other tree.

        1. If this tree is empty, but it has value objects,
            then it does not use any labels. Thus, we replace
            self.vos with the other tree's value objects.

        2. Find all value objects with labels that match the labels
            in tree.vos. "Search Hits" are the intersection of all
            indices in current value objects that have the same value
            for a given label of a value object in the other tree.
            Value objects in the other tree that do not match value
            objects in this tree are added to not_matched and appended
            to self.vos at the end.

            2.a. Loop over all labels used by this project.
                2.a.i. Both trees use this label.
                    2.a.i.1. Find all values that are in both trees
                        for the given label and update the search hits
                        set for matches.
                    2.a.i.2. Find all values that are in the other tree
                        but are not in this tree and add them to not_matched.
                        (VO's in not matched will be added at the end.)
                2.a.ii. The label is in this tree but is not in the other tree.
                    We treat all of the values under this label as search hits
                    and add their values to the search hits set.
                2.a.iii. The label is not in this tree but is in the new tree.
                    New labels can not be added to a list of value objects and
                    an error is thrown.
                2.a.iv. Neither tree has this label; so, ignore it.

            2.b. Loop over all indices in search_hits.
                2.a. Replace value of matches with the new value.
                    (if value is None, save to delete later.)
                2.b. If there are no matches for a given index, append them to
                    not_matched.

        3. Drop all indices from to_delete, and append all items in not_matched.

        4. If there were no deletions, save the new values to update the tree
            when it is used again. If there are deletions, do not save the new
            values because the tree needs to be re-built from the new value
            objects.

        Returns:
            List of updated value objects.

        Raises:
            ParamToolsError if a label is specied in the new value objects
                that is not present in the default value objects.
        """
        new_values = set([])
        not_matched = set([])
        to_delete = set([])
        # Trees are lazy and need to be initialized before use.
        self.init()
        tree.init()
        # self.tree doesn't have labels -> there are no labels to query.
        if not self.tree and tree.vos:
            del self.vos[:]
            not_matched = range(len(tree.vos))
        else:
            # search_hits saves the intersection of all label matches.
            # The indices in the sets at the end are the search hits.
            search_hits = {ix: set([]) for ix in range(len(tree.vos))}
            for label in self.label_grid:
                if label in ("_auto",):
                    continue
                if label in tree.tree and label in self.tree:
                    # All label values that exist in both trees.
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
                    # All label values in the new tree that are not in this tree.
                    # Value objects that have a label value that is not included
                    # in the current tree means that they will not be matched.
                    for label_value in (
                        tree.tree[label].keys() - self.tree[label].keys()
                    ):
                        for new_ix in tree.tree[label][label_value]:
                            search_hits.pop(new_ix)
                            not_matched.add(new_ix)
                elif label in self.tree:
                    # All value objects with labels not specified in the other
                    # tree are treated as search hits (for this label).
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

            for ix, search_hit_ixs in search_hits.items():
                if search_hit_ixs:
                    if tree.vos[ix]["value"] is not None:
                        for search_hit_ix in search_hit_ixs:
                            self.vos[search_hit_ix]["value"] = tree.vos[ix][
                                "value"
                            ]
                    else:
                        to_delete |= search_hit_ixs
                else:
                    not_matched.add(ix)
            if to_delete:
                # Iterate in reverse so that indices point to the correct
                # value. If iterating ascending then the values will be shifted
                # towards the front of the list as items are removed.
                for ix in sorted(to_delete, reverse=True):
                    del self.vos[ix]

        if not_matched:
            for ix in not_matched:
                if tree.vos[ix]["value"] is not None:
                    self.vos.append(tree.vos[ix])
                    new_values.add(len(self.vos) - 1)

        # It's faster to just re-build from scratch if values are deleted.
        if to_delete:
            self.new_values = None
            self.needs_build = True
        else:
            self.new_values = new_values
            self.needs_build = True

        return self.vos

    def select(
        self, labels: dict, cmp_func: CmpFunc, strict: bool = False
    ) -> List[ValueObject]:
        """
        Select all value objects from self.vos according to the label query,
        labels, and the comparison function, cmp_func. strict dictates
        whether vos missing a label in the query are eligble for inclusion
        in the select results.

        1. Loop over labels from query.
        2. Find all value objects that have a value that returns true
            from the cmp_func (e.g. it is equal to the query value).
        3. Take the intersection of all of the successful matches across
            the different labels to get the final reasult.

        Returns:
            List of value objects satisfying the query.
        """
        if not labels:
            return self.vos
        search_hits = set([])
        self.init()
        if not self.tree:
            return self.vos
        all_ixs = set(range(len(self.vos)))
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
                elif not strict or label_search_hits:
                    search_hits |= label_search_hits
                if not strict:
                    search_hits |= all_ixs - set.union(
                        *self.tree[label].values()
                    )
        return [self.vos[ix] for ix in search_hits]
