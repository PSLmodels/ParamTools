from collections import defaultdict

from paramtools import filter_labels
from paramtools import SortedKeyList


class QueryResult:
    def __init__(self, original_vos, skl_result):
        self.skl_result = skl_result
        self.original_vos = original_vos

    def __and__(self, queryresult: "QueryResult"):
        res = set(self.skl_result.original_indices) & set(
            queryresult.skl_result.original_indices
        )

        return [self.original_vos[i] for i in sorted(res)]

    def __or__(self, queryresult: "QueryResult"):
        res = set(self.skl_result.original_indices) | set(
            queryresult.skl_result.original_indices
        )

        return [self.original_vos[i] for i in sorted(res)]

    def __repr__(self):
        return str(
            [
                self.original_vos[i]
                for i in (self.skl_result.original_indices or [])
            ]
        )


class ValueObjects:
    def __init__(self, value_objects, label_validators):
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

    def eq(self, label, value):
        skl_result = self.skls[label].eq(value)
        # return [self.value_objects[i] for i in (res.original_indices or [])]
        return QueryResult(self.value_objects, skl_result)
