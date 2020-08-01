from collections import defaultdict

from paramtools import filter_labels
from paramtools import SortedKeyList


class QueryResult:
    def __init__(self, value_objects, indices):
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
    def __init__(self, value_objects, label_validators=None, skls=None):
        self.value_objects = value_objects
        label_values = defaultdict(list)
        for vo in value_objects:
            for label, value in filter_labels(vo, drop=["value"]).items():
                label_values[label].append(value)

        self.skls = {
            label: SortedKeyList(
                values, label_validators[label].cmp_funcs()["key"]
            )
            for label, values in label_values.items()
        }

    def eq(self, **labels):
        label, value = list(labels.items())[0]
        skl_result = self.skls[label].eq(value)
        return QueryResult(self.value_objects, skl_result.original_indices)

    def gt(self, **labels):
        label, value = list(labels.items())[0]
        skl_result = self.skls[label].gt(value)
        return QueryResult(self.value_objects, skl_result.original_indices)
