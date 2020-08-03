from collections import defaultdict
from typing import List, Dict, Any

from paramtools.utils import SortedKeyList
from paramtools.typing import ValueObject


def default_cmp_func(x):
    return x


class QueryResult:
    def __init__(self, value_objects: List[ValueObject], index: List[int]):
        self.value_objects = value_objects
        self.index = index

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.index) & set(queryresult.index)

        return QueryResult(self.value_objects, res)

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.index) | set(queryresult.index)

        return QueryResult(self.value_objects, res)

    def __repr__(self):
        vo_repr = "\n  ".join(
            str(self.value_objects[i]) for i in (self.index or [])
        )
        return f"QueryResult([\n  {vo_repr}\n])"

    def __iter__(self):
        for i in self.index:
            yield self.value_objects[i]

    def tolist(self):
        return [self.value_objects[i] for i in self.index]


class Slice:
    __slots__ = ("value_objects", "label")

    def __init__(self, value_objects, label):
        self.value_objects = value_objects
        self.label = label

    def __eq__(self, value):
        return self.value_objects.eq(**{self.label: value})

    def __ne__(self, value):
        return self.value_objects.ne(**{self.label: value})

    def __gt__(self, value):
        return self.value_objects.gt(**{self.label: value})

    def __ge__(self, value):
        return self.value_objects.gte(**{self.label: value})

    def __lt__(self, value):
        return self.value_objects.lt(**{self.label: value})

    def __le__(self, value):
        return self.value_objects.lte(**{self.label: value})


class ValueObjects:
    def __init__(
        self,
        value_objects: List[ValueObject],
        label_validators: Dict[str, Any] = None,
    ):
        self.value_objects = value_objects
        label_values = defaultdict(list)
        label_index = defaultdict(list)
        for ix, vo in enumerate(value_objects):
            for label, value in vo.items():
                label_values[label].append(value)
                label_index[label].append(ix)
        self.skls = {}
        for label in label_values:
            if label in label_validators and hasattr(
                label_validators[label], "cmp_funcs"
            ):
                cmp_func = label_validators[label].cmp_funcs()["key"]
            else:
                cmp_func = default_cmp_func
            self.skls[label] = SortedKeyList(
                label_values[label], cmp_func, label_index[label]
            )

        if "_auto" not in self.skls:
            self.skls["_auto"] = SortedKeyList([], default_cmp_func)

    def _cmp(self, op, strict, **labels):
        label, value = list(labels.items())[0]
        skl_result = getattr(self.skls[label], op)(value)
        if not strict:
            match_index = skl_result.index if skl_result else []
            missing = self.missing(label)
            match_index = set(match_index + missing.index)
        elif skl_result is None:
            match_index = []
        else:
            match_index = skl_result.index
        return QueryResult(self.value_objects, match_index)

    def __getitem__(self, label):
        return Slice(self, label)

    def missing(self, label: str):
        index = []
        for ix, vo in enumerate(self.value_objects):
            if label not in vo:
                index.append(ix)
        return QueryResult(self.value_objects, index)

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

    def __repr__(self):
        vo_repr = "\n  ".join(str(vo) for vo in self.value_objects)
        return f"ValueObjects([\n  {vo_repr}\n])"
