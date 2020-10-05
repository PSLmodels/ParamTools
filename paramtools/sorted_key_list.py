from bisect import bisect_left, bisect_right


class SortedKeyListResult:
    def __init__(self, key_list_values):
        self.key_list_values = key_list_values

    @property
    def values(self):
        return [item[0] for item in self.key_list_values]

    @property
    def index(self):
        return [item[2] for item in self.key_list_values]

    def __iter__(self):
        for value in self.values:
            yield value


class SortedKeyList:
    """
    Sorted key list inspired by SortedContainers and the Python docs:

    - http://www.grantjenks.com/docs/sortedcontainers/
    - https://docs.python.org/3.9/library/bisect.html
    """

    def __init__(self, values, keyfunc, index=None):
        if index:
            assert len(values) == len(index)
        if index is None:
            index = range(len(values))
        self.sorted_key_list = [
            (val, keyfunc(val), ix) for ix, val in zip(index, values)
        ]
        self.sorted_key_list.sort(key=lambda r: r[1])
        self.keys = [r[1] for r in self.sorted_key_list]
        self.index = set(index)
        self.keyfunc = keyfunc

    def __repr__(self):
        return str(self.sorted_key_list)

    def eq(self, value):
        left_i = bisect_left(self.keys, self.keyfunc(value))
        if (
            left_i != len(self.keys)
            and self.sorted_key_list[left_i][0] == value
        ):
            right_i = bisect_right(self.keys, self.keyfunc(value))
            return SortedKeyListResult(self.sorted_key_list[left_i:right_i])
        return None

    def ne(self, value):
        result = []
        lt = self.lt(value)
        if lt is not None:
            result += lt.key_list_values
        gt = self.gt(value)
        if gt is not None:
            result += gt.key_list_values

        return SortedKeyListResult(result)

    def lt(self, value):
        i = bisect_left(self.keys, self.keyfunc(value))
        if i:
            return SortedKeyListResult(self.sorted_key_list[: i - 1 + 1])
        return None

    def lte(self, value):
        i = bisect_right(self.keys, self.keyfunc(value))
        if i:
            return SortedKeyListResult(self.sorted_key_list[: i - 1 + 1])
        return None

    def gt(self, value):
        i = bisect_right(self.keys, self.keyfunc(value))
        if i != len(self.keys):
            return SortedKeyListResult(self.sorted_key_list[i:])
        return None

    def gte(self, value):
        i = bisect_left(self.keys, self.keyfunc(value))
        if i != len(self.keys):
            return SortedKeyListResult(self.sorted_key_list[i:])
        return None

    def insert(self, value, index=None):
        key_value = self.keyfunc(value)
        i = bisect_left(self.keys, key_value)
        if index is None:
            index = max(self.index) + 1
        self.sorted_key_list.insert(i, (value, key_value, index))
        self.keys.insert(i, key_value)
        self.index.add(index)
