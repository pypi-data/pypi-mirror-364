# iteroo

Object-oriented iterator wrapper for Python


## Description

**iteroo** provides a functional, object-oriented interface for working with iterators in Python. It wraps any iterable and exposes a rich set of methods for chaining, transformation, and collection, inspired by functional programming and modern iterator libraries.

- Chainable, lazy iterator operations
- Functional-style methods: `map`, `filter`, `takewhile`, `dropwhile`, `flatten`, etc.
- Collect results as lists, sum, count, and more
- 100% test coverage, MIT licensed

## Features

- `it`: Main iterator wrapper class
- `map`, `filter`, `enumerate`, `takewhile`, `dropwhile`, `flatten`, `pairwise`, `select`, `zip`, `cycle`, `diff`, `inmap`, `alltrue`, `allfalse`, `equal`, `allequal`, `sum`, `count`, `max`, `take_n`, `take_every_nth`
- Utility functions: `range`, `count`, `repeat`

## Installation

```bash
pip install iteroo
```
Or for development:
```bash
uv pip install -e '.[test]'
```

## Usage

```python
from iteroo import it

# Basic usage
nums = it([1, 2, 3, 4, 5])
even = nums.filter(lambda x: x % 2 == 0).collect()  # [2, 4]

# Chaining
result = (
    it.range(10)
      .filter(lambda x: x % 2)
      .map(lambda x: x * 10)
      .take_n(3)
      .collect()
)
# result: [10, 30, 50]

# Flattening
nested = it([[1, 2], [3, 4]])
flat = nested.flatten().collect()  # [1, 2, 3, 4]

# Pairwise difference
seq = it([1, 4, 9, 16])
diffs = seq.diff().collect()  # [3, 5, 7]

# Inmap (apply multiple functions to each element)
a = it([[1, 1], [2, 2], [3, 3]])
b = a.inmap([lambda x: x + 1, lambda x: x + 2]).collect()  # [[2, 3], [3, 4], [4, 5]]

# Utilities
from iteroo.it import repeat
assert repeat('a', 3).collect() == ['a', 'a', 'a']

```

## Testing

To run the tests and check coverage:

```bash
uv pip install -e '.[test]'
pytest --cov=src/iteroo --cov-report=term-missing
```

To generate an HTML coverage report:

```bash
pytest --cov=src/iteroo --cov-report=html
# Open htmlcov/index.html in your browser
```

## License

MIT License. See [LICENSE](LICENSE).
