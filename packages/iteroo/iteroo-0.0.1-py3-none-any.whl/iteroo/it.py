"""Module provides the main iterator wrapper."""

import itertools


class it:
    """Iterator wrapper that provides an objector orientated functional style."""

    def __init__(self, it):
        """Construct an iterator object wrapping iterator `it`."""
        self._it = it

    def __iter__(self):
        """Provide iterator interface to underlying iterator."""
        return iter(self._it)

    def filter(self, func):
        """See builtin `filter`."""
        return it(filter(func, self._it))

    def map(self, func):
        """See builtin `map`."""
        return it(map(func, self._it))

    def collect(self):
        """Collect the iterms of the iterator into a list."""
        return list(self._it)

    def max(self):
        """See builtin `max`."""
        return max(self)

    def enumerate(self):
        """See builtin `enumerate`."""
        return it(enumerate(self._it))

    def takewhile(self, func):
        """See `itertools.takewhile`."""
        return it(itertools.takewhile(func, self._it))

    def dropwhile(self, func):
        """See `itertools.dropwhile`."""
        return it(itertools.dropwhile(func, self._it))

    def take_every_nth(self, n):
        """Yield every nth entry."""
        return it((b for i, b in self.enumerate() if (i + 1) % n == 0))

    def take_n(self, n):
        """Take up to n elements."""
        return it((b for i, b in self.enumerate().takewhile(lambda x: x[0] < n)))

    def pairwise(self):
        """See `itertools.pairwise`."""
        return it(itertools.pairwise(self._it))

    def select(self, n):
        """See `itertools.compress`."""
        return it(itertools.compress(self._it, n))

    def inmap(self, m):
        """Given a list of iterables, apply functions to each element.

        :param m (list): List of functions to apply to each list.

        For example:
        >>> a = iteroo.it.it([[1, 1], [2, 2], [3, 3]])
        >>> a.inmap([lambda x: x+1, lambda x: x+2]).collect()
         [[2, 3], [3, 4], [4, 5]]
        """
        return self.map(lambda vals: [f(v) for f, v in zip(m, vals)])

    def flatten(self):
        """Un-nest a list of iterables into a flat list.

        Example:
        iteroo.it.it([[1, 3, 4], [1, 5, 6]])
        assert a.flatten() == [1, 3, 4, 2, 5, 6]
        """
        return it(itertools.chain(*self._it))

    def sum(self):
        """See builtin `sum`."""
        return sum(self)

    def count(self):
        """Count the number of elements in this iterable."""
        return sum(1 for _ in self._it)

    def diff(self):
        """Calculate the pairwise forward difference between elements."""
        return it([b - a for a, b in self.pairwise()])

    def alltrue(self):
        """Return True if all elements evaluate true, otherwise False."""
        return self.map(lambda x: 1 if not x else 0).sum() == 0

    def allfalse(self):
        """Return True if all elements evaluate false, otherwise True."""
        return self.map(lambda x: 0 if not x else 1).sum() == 0

    def equal(self, other):
        """Element wise equality between self and other."""
        return it((a == b for a, b in zip(self, other)))

    def allequal(self, other):
        """Whole iterable equality between self and other."""
        return it((a == b for a, b in zip(self, other))).alltrue()

    def zip(self, other):
        """See builtin `zip`."""
        return it(zip(self, other))

    def cycle(self):
        """See `itertools.cycle`."""
        return it(itertools.cycle(self))


def count(*args, **kwargs):
    """See `itertools.count`."""
    return it(itertools.count(*args, **kwargs))


def repeat(*args, **kwargs):
    """See `itertools.repeat`."""
    return it(itertools.repeat(*args, **kwargs))


_range = range


def range(*args, **kwargs):
    """See builtin `range`."""
    return it(_range(*args, **kwargs))

