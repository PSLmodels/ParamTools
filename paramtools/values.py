import copy
from collections import defaultdict
from typing import List, Dict, Any, Union, Generator

from paramtools.utils import SortedKeyList
from paramtools.typing import ValueObject


def default_cmp_func(x):
    return x


class ValueBase:
    pass


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
            str(self.values.values[i]) for i in (self.index or [])
        )
        return f"QueryResult([\n  {vo_repr}\n])"

    def __iter__(self):
        for i in self.index:
            yield self.values.values[i]

    def tolist(self):
        return [self.values.values[i] for i in self.index]

    def eq(self, strict=True, **labels):
        return self.values.eq(strict, **labels)

    def ne(self, strict=True, **labels):
        return self.values.ne(strict, **labels)

    def gt(self, strict=True, **labels):
        return self.values.gt(strict, **labels)

    def gte(self, strict=True, **labels):
        return self.values.gte(strict, **labels)

    def lt(self, strict=True, **labels):
        return self.values.lt(strict, **labels)

    def lte(self, strict=True, **labels):
        return self.values.lte(strict, **labels)

    def isin(self, strict=True, **labels):
        return self.values.isin(strict, **labels)

    def as_values(self):
        return Values(
            values=list(self),
            index=self.index,
            label_validators=self.values.label_validators,
        )

    def delete(self):
        self.values.delete(*self.index, inplace=True)


class Slice(ValueBase):
    def __init__(self, values: "Values", label: str):
        self.values = values
        self.label = label

    def __eq__(self, value=None, **labels):
        return self.values.eq(**{self.label: value})

    def __ne__(self, value):
        return self.values.ne(**{self.label: value})

    def __gt__(self, value):
        return self.values.gt(**{self.label: value})

    def __ge__(self, value):
        return self.values.gte(**{self.label: value})

    def __lt__(self, value):
        return self.values.lt(**{self.label: value})

    def __le__(self, value):
        return self.values.lte(**{self.label: value})

    def eq(self, value, strict=True):
        return self.values.eq(strict, **{self.label: value})

    def ne(self, value, strict=True):
        return self.values.ne(strict, **{self.label: value})

    def gt(self, value, strict=True):
        return self.values.gt(strict, **{self.label: value})

    def gte(self, value, strict=True):
        return self.values.gte(strict, **{self.label: value})

    def lt(self, value, strict=True):
        return self.values.lt(strict, **{self.label: value})

    def lte(self, value, strict=True):
        return self.values.lte(strict, **{self.label: value})

    def isin(self, value, strict=True):
        return self.values.isin(strict, **{self.label: value})


class Values(ValueBase):
    def __init__(
        self,
        values: List[ValueObject],
        label_validators: Dict[str, Any] = None,
        skls: Dict[str, SortedKeyList] = None,
        index: List[Any] = None,
    ):
        self.index = index or list(range(len(values)))
        self.values = {ix: value for ix, value in zip(self.index, values)}
        self.label_validators = label_validators

        if skls is not None:
            self.skls = skls
        else:
            self.skls = self.build_skls(self.values, label_validators or {})

        if "_auto" not in self.skls:
            self.skls["_auto"] = SortedKeyList([], default_cmp_func)

    def build_skls(self, values, label_validators):
        label_values = defaultdict(list)
        label_index = defaultdict(list)
        for ix, vo in values.items():
            for label, value in vo.items():
                label_values[label].append(value)
                label_index[label].append(ix)

        skls = {}
        for label in label_values:
            keyfunc = self.get_keyfunc(label, label_validators)
            skls[label] = SortedKeyList(
                label_values[label], keyfunc, label_index[label]
            )

        return skls

    def update_skls(self, values):
        # TODO: remove existing values with clashing index
        for ix, vo in values.items():
            for label, value in vo.items():
                if label in self.skls:
                    self.skls[label].insert(value, index=ix)
                else:
                    self.skls[label] = SortedKeyList(
                        [vo],
                        keyfunc=self.get_keyfunc(label, self.label_validators),
                        index=[ix],
                    )

    def get_keyfunc(self, label, label_validators):
        if label in label_validators and hasattr(
            label_validators[label], "cmp_funcs"
        ):
            return label_validators[label].cmp_funcs()["key"]
        else:
            return default_cmp_func

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
        return Slice(self, label)

    def missing(self, label: str):
        index = list(set(self.index) - self.skls[label].index_map.keys())
        return QueryResult(self, index)

    def eq(self, strict=True, **labels):
        return self._cmp("eq", strict, **labels)

    def ne(self, strict=True, **labels):
        return self._cmp("ne", strict, **labels)

    def gt(self, strict=True, **labels):
        return self._cmp("gt", strict, **labels)

    def gte(self, strict=True, **labels):
        return self._cmp("gte", strict, **labels)

    def lt(self, strict=True, **labels):
        return self._cmp("lt", strict, **labels)

    def lte(self, strict=True, **labels):
        return self._cmp("lte", strict, **labels)

    def isin(self, strict=True, **labels):
        label, values = list(labels.items())[0]
        return union(
            self.eq(strict=strict, **{label: value}) for value in values
        )

    def insert(
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
                updated_values.values(),
                skls=self.build_skls(updated_values, self.label_validators),
                index=current_index + new_index,
            )

    def delete(self, *index, inplace=False):
        if not index:
            index = list(self.index)
        if inplace:
            for ix in index:
                self.values.pop(ix)
                self.index.remove(ix)

            self.skls = self.build_skls(self.values, self.label_validators)
        else:
            new_index = list(self.index)
            new_values = copy.deepcopy(self.values)
            for ix in index:
                new_values.pop(ix)
                new_index.remove(ix)

            return Values(
                new_values.values(),
                label_validators=self.label_validators,
                index=new_index,
            )

    @property
    def labels(self):
        return list(self.skls.keys())

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.index) & set(queryresult.index)

        return QueryResult(self, res)

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.index) | set(queryresult.index)

        return QueryResult(self, res)

    def __iter__(self):
        for value in self.values.values():
            yield value

    def __repr__(self):
        vo_repr = "\n  ".join(str(self.values[i]) for i in self.index)
        return f"ValueObjects([\n  {vo_repr}\n])"


def union(
    queryresults: Union[List[ValueBase], Generator[ValueBase, None, None]]
):
    result = None
    for queryresult in queryresults:
        if result is None:
            result = queryresult
        else:
            result |= queryresult

    return result or []


def intersection(
    queryresults: Union[List[ValueBase], Generator[ValueBase, None, None]]
):
    result = None
    for queryresult in queryresults:
        if result is None:
            result = queryresult
        else:
            result &= queryresult

    return result or []
