from collections import defaultdict
from typing import Dict, List

import marshallow as ma

from .utils import SortedKeyList

# from .schema import FIELD_MAP
from .typing import ValueObject


class ValueObjects:
    def __init__(
        self,
        value_objects: List[ValueObject],
        label_validators: Dict[str, ma.fields.Field],
    ):
        self.value_objects = value_objects

        skls = defaultdict(list)
        for vo in value_objects:
            for label, value in vo.items():
                if label == "value":
                    continue
                self.skls[label].append(value)

        self.skls = {}
        for label, values in skls.items():
            self.skls[label] = SortedKeyList(
                values, label_validators[label].cmp_funcs()
            )

    def eq(self, label, value):
        result = self.skls[label].eq(value)
        if result is not None:
            return self.value_objects[result.indices]
