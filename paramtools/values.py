import copy
from collections import defaultdict
from typing import List, Dict, Any, Union, Generator

from paramtools.sorted_key_list import SortedKeyList
from paramtools.typing import ValueObject


def default_cmp_func(x):
    return x


class ValueItem:
    """
    Handles index-based look-ups on the Values class.
    """

    def __init__(self, values: "Values", index: List[int] = None):
        self.values = values
        self.index = list(index) if index is not None else index

    def __getitem__(self, item):
        if isinstance(item, slice):
            if self.index is not None:
                indices = item.indices(len(self.index))
                return [
                    dict(self.values.values[self.index[ix]])
                    for ix in range(*indices)
                ]
            else:
                indices = item.indices(len(self.values))
                return [dict(self.values.values[ix]) for ix in range(*indices)]
        elif self.index is not None:
            return dict(self.values.values[self.index[item]])
        else:
            return dict(self.values.values[item])


class ValueBase:
    @property
    def cmp_attr(self):
        raise NotImplementedError()

    def __eq__(self, value=None, **labels):
        return self.cmp_attr.eq(**{self.label: value})

    def __ne__(self, value):
        return self.cmp_attr.ne(**{self.label: value})

    def __gt__(self, value):
        return self.cmp_attr.gt(**{self.label: value})

    def __ge__(self, value):
        return self.cmp_attr.gte(**{self.label: value})

    def __lt__(self, value):
        return self.cmp_attr.lt(**{self.label: value})

    def __le__(self, value):
        return self.cmp_attr.lte(**{self.label: value})

    def __len__(self):
        return len([item for item in iter(self.cmp_attr)])

    def __iter__(self):
        return iter(self.cmp_attr)

    def __getitem__(self, item):
        return self.cmp_attr[item]

    def eq(self, value, strict=True):
        return self.cmp_attr.eq(strict, **{self.label: value})

    def ne(self, value, strict=True):
        return self.cmp_attr.ne(strict, **{self.label: value})

    def gt(self, value, strict=True):
        return self.cmp_attr.gt(strict, **{self.label: value})

    def gte(self, value, strict=True):
        return self.cmp_attr.gte(strict, **{self.label: value})

    def lt(self, value, strict=True):
        return self.cmp_attr.lt(strict, **{self.label: value})

    def lte(self, value, strict=True):
        return self.cmp_attr.lte(strict, **{self.label: value})

    def isin(self, value, strict=True):
        return self.cmp_attr.isin(strict, **{self.label: value})


class QueryResult(ValueBase):
    def __init__(self, values: "Values", index: List[Any]):
        self.values = values
        self.index = index

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.index) & set(queryresult.index)

        return QueryResult(self.values, res)

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.index) | set(queryresult.index)

        return QueryResult(self.values, res)

    def __repr__(self):
        vo_repr = "\n  ".join(
            str(dict(self.values.values[i])) for i in (self.index or [])
        )
        return f"QueryResult([\n  {vo_repr}\n])"

    def __iter__(self):
        for i in self.index:
            yield self.values.values[i]

    def __getitem__(self, item):
        raise NotImplementedError(
            "Use .isel to do index-based look ups or as_values to chain queries."
        )

    @property
    def isel(self):
        return ValueItem(self.values, self.index)

    def tolist(self):
        return [self.values.values[i] for i in self.index]

    def eq(self, strict=True, **labels):
        return self.cmp_attr.eq(strict, **labels)

    def ne(self, strict=True, **labels):
        return self.cmp_attr.ne(strict, **labels)

    def gt(self, strict=True, **labels):
        return self.cmp_attr.gt(strict, **labels)

    def gte(self, strict=True, **labels):
        return self.cmp_attr.gte(strict, **labels)

    def lt(self, strict=True, **labels):
        return self.cmp_attr.lt(strict, **labels)

    def lte(self, strict=True, **labels):
        return self.cmp_attr.lte(strict, **labels)

    def isin(self, strict=True, **labels):
        return self.cmp_attr.isin(strict, **labels)

    def __eq__(self, *args, **kwargs):
        raise NotImplementedError()

    def __ne__(self, *args, **kwargs):
        raise NotImplementedError()

    def __gt__(self, *args, **kwargs):
        raise NotImplementedError()

    def __ge__(self, *args, **kwargs):
        raise NotImplementedError()

    def __lt__(self, *args, **kwargs):
        raise NotImplementedError()

    def __le__(self, *args, **kwargs):
        raise NotImplementedError()

    def as_values(self):
        return Values(
            values=list(self), index=self.index, keyfuncs=self.values.keyfuncs
        )

    def delete(self):
        self.values.delete(*self.index, inplace=True)

    @property
    def cmp_attr(self):
        return self.values


class Slice(ValueBase):
    def __init__(self, values: "Values", label: str):
        self.values = values
        self.label = label

    @property
    def cmp_attr(self):
        return self.values

    def __getitem__(self, item):
        if isinstance(item, slice):
            indices = item.indices(len(self))
            return [
                self.values.values[ix].get(self.label, None)
                for ix in range(*indices)
            ]
        else:
            return self.values.values[item][self.label]

    @property
    def isel(self):
        raise NotImplementedError(
            "Access values of a Slice object directly: parameters['label'][1]"
        )

    def __repr__(self):
        vo_repr = "\n  ".join(
            str(dict(self.values.values[i])) for i in self.values.values
        )
        return f"Slice([\n  {vo_repr}\n], \nlabel={self.label})"


class Values(ValueBase):
    """
    The Values class is used to query and update parameter values.

    For more information, checkout the
    `Viewing Data <https://paramtools.dev/api/viewing-data.html>`_ docs.
    """

    def __init__(
        self,
        values: List[ValueObject],
        keyfuncs: Dict[str, Any] = None,
        skls: Dict[str, SortedKeyList] = None,
        index: List[Any] = None,
    ):
        self.index = index or list(range(len(values)))
        self.values = {ix: value for ix, value in zip(self.index, values)}
        self.keyfuncs = keyfuncs
        self.label = "value"

        if skls is not None:
            self.skls = skls
        else:
            self.skls = self.build_skls(self.values, keyfuncs or {})

    def build_skls(self, values, keyfuncs):
        label_values = defaultdict(list)
        label_index = defaultdict(list)
        for ix, vo in values.items():
            for label, value in vo.items():
                label_values[label].append(value)
                label_index[label].append(ix)

        skls = {}
        for label in label_values:
            keyfunc = self.get_keyfunc(label, keyfuncs)
            skls[label] = SortedKeyList(
                label_values[label], keyfunc, label_index[label]
            )

        return skls

    def update_skls(self, values):
        # TODO: remove existing values with clashing index
        for ix, vo in values.items():
            for label, value in vo.items():
                if self.skls.get(label, None) is not None:
                    self.skls[label].add(value, index=ix)
                else:
                    self.skls[label] = SortedKeyList(
                        [value],
                        keyfunc=self.get_keyfunc(label, self.keyfuncs),
                        index=[ix],
                    )

    def get_keyfunc(self, label, keyfuncs):
        keyfunc = keyfuncs.get(label)
        return keyfunc or default_cmp_func

    def _cmp(self, op, strict, **labels):
        label, value = list(labels.items())[0]
        skl = self.skls.get(label, None)

        if skl is None and strict:
            raise KeyError(f"Unknown label: {label}.")
        elif skl is None and not strict:
            return QueryResult(self, list(self.index))

        skl_result = getattr(self.skls[label], op)(value)
        if not strict:
            match_index = skl_result.index if skl_result else []
            missing = self.missing(label)
            match_index = set(match_index + missing.index)
        elif skl_result is None:
            match_index = []
        else:
            match_index = skl_result.index
        return QueryResult(self, match_index)

    def __getitem__(self, label):
        if label not in self.skls:
            raise KeyError(f"Unknown label: {label}")
        return Slice(self, label)

    def missing(self, label: str):
        index = list(set(self.index) - self.skls[label].index)
        return QueryResult(self, index)

    def eq(self, strict=True, **labels):
        """
        Returns values that match the given label:

        .. code-block:: Python

            params.sel["my_param"].eq(my_label=5)
            params.sel["my_param"]["my_label"] == 5
        """
        return self._cmp("eq", strict, **labels)

    def ne(self, strict=True, **labels):
        """
        Returns values that do match the given label:

        .. code-block:: Python

            params.sel["my_param"].ne(my_label=5)
            params.sel["my_param"]["my_label"] != 5
        """

        return self._cmp("ne", strict, **labels)

    def gt(self, strict=True, **labels):
        """
        Returns values that have label values greater than the label value:

        .. code-block:: Python

            params.sel["my_param"].gt(my_label=5)
            params.sel["my_param"]["my_label"] > 5

        """

        return self._cmp("gt", strict, **labels)

    def gte(self, strict=True, **labels):
        """
        Returns values that have label values greater than or equal to the label value:

        .. code-block:: Python

            params.sel["my_param"].gte(my_label=5)
            params.sel["my_param"]["my_label"] >= 5

        """
        return self._cmp("gte", strict, **labels)

    def lt(self, strict=True, **labels):
        """
        Returns values that have label values less than the label value:

        .. code-block:: Python

            params.sel["my_param"].lt(my_label=5)
            params.sel["my_param"]["my_label"] < 5

        """

        return self._cmp("lt", strict, **labels)

    def lte(self, strict=True, **labels):
        """
        Returns values that have label values less than or equal to the label value:

        .. code-block:: Python

            params.sel["my_param"].lte(my_label=5)
            params.sel["my_param"]["my_label"] <= 5

        """

        return self._cmp("lte", strict, **labels)

    def isin(self, strict=True, **labels):
        """
        Returns values that have label values less than or equal to the label value:

        .. code-block:: Python

            params.sel["my_param"].isin(my_label=[5, 6])

        """

        label, values = list(labels.items())[0]
        return union(
            self.eq(strict=strict, **{label: value}) for value in values
        )

    def add(
        self, values: List[ValueObject], index: List[Any] = None, inplace=False
    ):
        if index is not None:
            assert len(index) == len(values)
            new_index = index
        else:
            max_index = max(self.index) if self.index else 0
            new_index = [max_index + i + 1 for i in range(len(values))]

        new_values = {ix: value for ix, value in zip(new_index, values)}

        if inplace:
            self.update_skls(new_values)
            self.values.update(new_values)
            self.index += new_index
        else:
            current_index = list(self.index)
            updated_values = dict(self.values)
            updated_values.update(new_values)
            return Values(
                [value for value in updated_values.values()],
                skls=self.build_skls(updated_values, self.keyfuncs),
                index=current_index + new_index,
            )

    def delete(self, *index, inplace=False):
        if not index:
            index = list(self.index)
        if inplace:
            for ix in index:
                self.values.pop(ix)
                self.index.remove(ix)
            self.skls = self.build_skls(self.values, self.keyfuncs)
        else:
            new_index = list(self.index)
            new_values = copy.deepcopy(self.values)
            for ix in index:
                new_values.pop(ix)
                new_index.remove(ix)

            return Values(
                [value for value in new_values.values()],
                keyfuncs=self.keyfuncs,
                index=new_index,
            )

    @property
    def cmp_attr(self):
        return self

    @property
    def isel(self):
        """
        Select values by their index:

        .. code-block:: Python

            params.sel["my_param"].isel[0]
            params.sel["my_param"].isel[:5]

        """

        return ValueItem(self, self.index)

    @property
    def labels(self):
        return list(self.skls.keys())

    def __eq__(self, other):
        if isinstance(other, ValueBase):
            return list(self) == list(other)
        elif isinstance(other, list):
            return list(self) == other
        else:
            raise TypeError(f"Unable to compare Values against {type(other)}")

    def __and__(self, queryresult: "QueryResult"):
        """
        Combine queries with logical 'and':

        .. code-block:: Python

            my_param = params.sel["my_param]
            (my_param["my_label"] == 5) & (my_param["oth_label"] == "hello")
        """

        res = set(self.index) & set(queryresult.index)

        return QueryResult(self, res)

    def __or__(self, queryresult: "QueryResult"):
        """
        Combine queries with logical 'or':

        .. code-block:: Python

            my_param = params.sel["my_param]
            (my_param["my_label"] == 5) | (my_param["oth_label"] == "hello")
        """

        res = set(self.index) | set(queryresult.index)

        return QueryResult(self, res)

    def __iter__(self):
        for value in self.values.values():
            yield value

    def __repr__(self):
        vo_repr = (
            ",\n  ".join(str(dict(self.values[i])) for i in self.index) + ","
        )
        return f"Values([\n  {vo_repr}\n])"


def union(
    queryresults: Union[List[ValueBase], Generator[ValueBase, None, None]]
):
    result = None
    for queryresult in queryresults:
        if result is None:
            result = queryresult
        else:
            result |= queryresult

    return result or QueryResult(None, [])


def intersection(
    queryresults: Union[List[ValueBase], Generator[ValueBase, None, None]]
):
    result = None
    for queryresult in queryresults:
        if result is None:
            result = queryresult
        else:
            result &= queryresult

    return result or QueryResult(None, [])
