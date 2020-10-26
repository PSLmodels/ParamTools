import functools
import sortedcontainers


class SortedKeyListResult:
    def __init__(self, key_list_values):
        self.key_list_values = key_list_values

    @property
    def values(self):
        return [item[0] for item in self.key_list_values]

    @property
    def index(self):
        return [item[1] for item in self.key_list_values]

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
        sorted_key_list = [(val, ix) for ix, val in zip(index, values)]
        self.index = set(index)
        self.keyfunc = functools.lru_cache(maxsize=None)(keyfunc)

        self.sorted_key_list_2 = sortedcontainers.SortedKeyList(
            sorted_key_list, key=lambda t: keyfunc(t[0])
        )

    def __repr__(self):
        return str(self.sorted_key_list)

    def eq(self, value):
        key = self.keyfunc(value)
        irange = list(
            self.sorted_key_list_2.irange_key(min_key=key, max_key=key)
        )
        if irange:
            return SortedKeyListResult(irange)
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
        key = self.keyfunc(value)
        irange = list(
            self.sorted_key_list_2.irange_key(
                max_key=key, inclusive=(True, False)
            )
        )
        if irange:
            return SortedKeyListResult(irange)
        return None

    def lte(self, value):
        key = self.keyfunc(value)
        irange = list(
            self.sorted_key_list_2.irange_key(
                max_key=key, inclusive=(True, True)
            )
        )
        if irange:
            return SortedKeyListResult(irange)
        return None

    def gt(self, value):
        key = self.keyfunc(value)
        irange = list(
            self.sorted_key_list_2.irange_key(
                min_key=key, inclusive=(False, True)
            )
        )
        if irange:
            return SortedKeyListResult(irange)
        return None

    def gte(self, value):
        key = self.keyfunc(value)
        irange = list(
            self.sorted_key_list_2.irange_key(
                min_key=key, inclusive=(True, True)
            )
        )
        if irange:
            return SortedKeyListResult(irange)
        return None

    def add(self, value, index=None):
        if index is None:
            index = max(self.index) + 1
        self.sorted_key_list_2.add((value, index))
        self.index.add(index)
