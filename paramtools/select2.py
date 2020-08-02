from collections import defaultdict
from typing import List, Dict, Any

from paramtools import filter_labels
from paramtools import SortedKeyList
from paramtools.typing import ValueObject


def default_cmp_func(x):
    return x


class QueryResult:
    def __init__(self, value_objects: List[ValueObject], indices: List[int]):
        self.value_objects = value_objects
        self.indices = indices

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.indices) & set(queryresult.indices)

        return QueryResult(self.value_objects, res)

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.indices) | set(queryresult.indices)

        return QueryResult(self.value_objects, res)

    def __repr__(self):
        return str([self.value_objects[i] for i in (self.indices or [])])

    def __iter__(self):
        for i in self.indices:
            yield self.value_objects[i]


class ValueObjects:
    def __init__(
        self,
        value_objects: List[ValueObject],
        label_validators: Dict[str, Any] = None,
    ):
        self.value_objects = value_objects
        label_values = defaultdict(list)
        for vo in value_objects:
            for label, value in filter_labels(vo, drop=["value"]).items():
                label_values[label].append(value)

        self.skls = {}
        for label, values in label_values.items():
            if label in label_validators:
                cmp_func = label_validators[label].cmp_funcs()["key"]
            else:
                cmp_func = default_cmp_func
            self.skls[label] = SortedKeyList(values, cmp_func)

        if "_auto" not in self.skls:
            self.skls["_auto"] = SortedKeyList([], cmp_func)

    def _handle_strict(self, label: str, match_indices: List[int]):
        for ix, vo in enumerate(self.value_objects):
            if label not in vo and ix not in match_indices:
                match_indices.append(ix)

    def _cmp(self, op, strict, **labels):
        label, value = list(labels.items())[0]
        skl_result = getattr(self.skls[label], op)(value)
        if not strict:
            match_indices = skl_result.indices if skl_result else []
            self._handle_strict(label, match_indices)
        else:
            match_indices = skl_result.indices
        return QueryResult(self.value_objects, match_indices)

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
