from collections import defaultdict
from typing import List, Dict, Any, Union

from paramtools.utils import SortedKeyList
from paramtools.typing import ValueObject


def default_cmp_func(x):
    return x


class Base:
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


class QueryResult(Base):
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


class Slice:
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


class Values:
    def __init__(
        self,
        values: List[ValueObject],
        label_validators: Dict[str, Any] = None,
        skls: Dict[str, SortedKeyList] = None,
        index: List[Any] = None,
    ):
        self.values = values
        self.index = index or list(range(len(values)))

        if skls is not None:
            self.skls = skls
        else:
            self.skls = self.build_skls(label_validators or {})

        if "_auto" not in self.skls:
            self.skls["_auto"] = SortedKeyList([], default_cmp_func)

    def build_skls(self, label_validators):
        label_values = defaultdict(list)
        label_index = defaultdict(list)
        for ix, vo in enumerate(self.values):
            for label, value in vo.items():
                label_values[label].append(value)
                label_index[label].append(ix)

        skls = {}
        for label in label_values:
            if label in label_validators and hasattr(
                label_validators[label], "cmp_funcs"
            ):
                cmp_func = label_validators[label].cmp_funcs()["key"]
            else:
                cmp_func = default_cmp_func
            skls[label] = SortedKeyList(
                label_values[label], cmp_func, label_index[label]
            )

        return skls

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
        index = []
        for ix, vo in enumerate(self.values):
            if label not in vo:
                index.append(ix)
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

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.index) & set(queryresult.index)

        return QueryResult(self, res)

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.index) | set(queryresult.index)

        return QueryResult(self, res)

    def __iter__(self):
        return iter(self.values)

    def __repr__(self):
        vo_repr = "\n  ".join(str(vo) for vo in self.values)
        return f"ValueObjects([\n  {vo_repr}\n])"


def _check(valuelike):
    if len(valuelike) == 0:
        return []

    res = valuelike[0]

    if len(valuelike) == 1 and isinstance(res, Values):
        return QueryResult(res.values, res.index)
    elif len(valuelike) == 1 and isinstance(res, QueryResult):
        return res
    elif len(valuelike) == 1:
        raise TypeError(
            f"any requires a list of Values or QueryResults. "
            f"Got {type(res)}."
        )


def union(*valuelike: Union[Values, QueryResult]):
    checked = _check(valuelike)
    if checked is not None:
        return checked

    res = valuelike[0]
    for value in valuelike[1:]:
        res |= value

    return res


def intersection(*valuelike: Union[Values, QueryResult]):
    checked = _check(valuelike)
    if checked is not None:
        return checked

    res = valuelike[0]
    for value in valuelike[1:]:
        res &= value

    return res
