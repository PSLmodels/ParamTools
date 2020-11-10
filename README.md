# ParamTools

**Define, update, and validate your model's parameters.**

Install using pip:

```
pip install paramtools
```

Install using conda:

```
conda install -c conda-forge paramtools
```

## Usage

Subclass `paramtools.Parameters` and define your model's [parameters](https://paramtools.dev/parameters):

```python
import paramtools


class Params(paramtools.Parameters):
    defaults = {
        "schema": {
            "labels": {
                "date": {
                    "type": "date",
                    "validators": {
                        "range": {
                            "min": "2020-01-01",
                            "max": "2021-01-01",
                            "step": {"months": 1}
                        }
                    }
                }
            },
        },
        "a": {
            "title": "A",
            "type": "int",
            "value": [
                {"date": "2020-01-01", "value": 2},
                {"date": "2020-10-01", "value": 8},
            ],
            "validators": {
                "range" : {
                    "min": 0, "max": "b"
                }
            }
        },
        "b": {
            "title": "B",
            "type": "float",
            "value": [{"date": "2020-01-01", "value": 10.5}]
        }
    }
```

### Access parameter values

Access values using `.sel`:

```python
params = Params()

params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 2},
      {'date': datetime.date(2020, 10, 1), 'value': 8},
    ])

Look up parameter values using a pandas-like api:

```python
from datetime import date

result = params.sel["a"]["date"] == date(2020, 1, 1)
result
```

    QueryResult([
      {'date': datetime.date(2020, 1, 1), 'value': 2}
    ])

```python
result.isel[0]["value"]
```

    2

### Adjust and validate parameter values

Add a new value:

```python
params.adjust({"a": [{"date": "2020-11-01", "value": 22}]})

params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 2},
      {'date': datetime.date(2020, 10, 1), 'value': 8},
      {'date': datetime.date(2020, 11, 1), 'value': 22},
    ])

Update an existing value:

```python
params.adjust({"a": [{"date": "2020-01-01", "value": 3}]})

params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 3},
      {'date': datetime.date(2020, 10, 1), 'value': 8},
      {'date': datetime.date(2020, 11, 1), 'value': 22},
    ])

Update all values:

```python
params.adjust({"a": 7})

params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 7},
      {'date': datetime.date(2020, 10, 1), 'value': 7},
      {'date': datetime.date(2020, 11, 1), 'value': 7},
    ])

Errors on values that are out of range:

```python
params.adjust({"a": -1})
```

    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-8-f8f1b7f6cd9a> in <module>
    ----> 1 params.adjust({"a": -1})


    ~/Paramtools/paramtools/parameters.py in adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, clobber)
        253             least one existing value item's corresponding label values.
        254         """
    --> 255         return self._adjust(
        256             params_or_path,
        257             ignore_warnings=ignore_warnings,


    ~/Paramtools/paramtools/parameters.py in _adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, is_deserialized, clobber)
        371             not ignore_warnings and has_warnings
        372         ):
    --> 373             raise self.validation_error
        374
        375         # Update attrs for params that were adjusted.


    ValidationError: {
        "errors": {
            "a": [
                "a -1 < min 0 "
            ]
        }
    }

```python
params = Params()

params.adjust({"a": [{"date": "2020-01-01", "value": 11}]})
```

    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-9-cc8a21f044d8> in <module>
          1 params = Params()
          2
    ----> 3 params.adjust({"a": [{"date": "2020-01-01", "value": 11}]})


    ~/Paramtools/paramtools/parameters.py in adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, clobber)
        253             least one existing value item's corresponding label values.
        254         """
    --> 255         return self._adjust(
        256             params_or_path,
        257             ignore_warnings=ignore_warnings,


    ~/Paramtools/paramtools/parameters.py in _adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, is_deserialized, clobber)
        371             not ignore_warnings and has_warnings
        372         ):
    --> 373             raise self.validation_error
        374
        375         # Update attrs for params that were adjusted.


    ValidationError: {
        "errors": {
            "a": [
                "a[date=2020-01-01] 11 > max 10.5 b[date=2020-01-01]"
            ]
        }
    }

Errors on invalid values:

```python
params = Params()

params.adjust({"b": "abc"})
```

    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-10-8373a2715e38> in <module>
          1 params = Params()
          2
    ----> 3 params.adjust({"b": "abc"})


    ~/Paramtools/paramtools/parameters.py in adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, clobber)
        253             least one existing value item's corresponding label values.
        254         """
    --> 255         return self._adjust(
        256             params_or_path,
        257             ignore_warnings=ignore_warnings,


    ~/Paramtools/paramtools/parameters.py in _adjust(self, params_or_path, ignore_warnings, raise_errors, extend_adj, is_deserialized, clobber)
        371             not ignore_warnings and has_warnings
        372         ):
    --> 373             raise self.validation_error
        374
        375         # Update attrs for params that were adjusted.


    ValidationError: {
        "errors": {
            "b": [
                "Not a valid number: abc."
            ]
        }
    }

### Extend parameter values using label definitions

Extend values using `label_to_extend`:

```python
params = Params(label_to_extend="date")
```

```python
params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 2},
      {'date': datetime.date(2020, 2, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 3, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 4, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 5, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 6, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 7, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 8, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 9, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 10, 1), 'value': 8},
      {'date': datetime.date(2020, 11, 1), 'value': 8, '_auto': True},
      {'date': datetime.date(2020, 12, 1), 'value': 8, '_auto': True},
      {'date': datetime.date(2021, 1, 1), 'value': 8, '_auto': True},
    ])

Updates to values are carried through to future dates:

```python
params.adjust({"a": [{"date": "2020-4-01", "value": 9}]})

params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 2},
      {'date': datetime.date(2020, 2, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 3, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 4, 1), 'value': 9},
      {'date': datetime.date(2020, 5, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 6, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 7, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 8, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 9, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 10, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 11, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 12, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2021, 1, 1), 'value': 9, '_auto': True},
    ])

Use `clobber` to only update values that were set automatically:

```python
params = Params(label_to_extend="date")
params.adjust(
    {"a": [{"date": "2020-4-01", "value": 9}]},
    clobber=False,
)

# Sort parameter values by date for nicer output
params.sort_values()
params.sel["a"]
```

    Values([
      {'date': datetime.date(2020, 1, 1), 'value': 2},
      {'date': datetime.date(2020, 2, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 3, 1), 'value': 2, '_auto': True},
      {'date': datetime.date(2020, 4, 1), 'value': 9},
      {'date': datetime.date(2020, 5, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 6, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 7, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 8, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 9, 1), 'value': 9, '_auto': True},
      {'date': datetime.date(2020, 10, 1), 'value': 8},
      {'date': datetime.date(2020, 11, 1), 'value': 8, '_auto': True},
      {'date': datetime.date(2020, 12, 1), 'value': 8, '_auto': True},
      {'date': datetime.date(2021, 1, 1), 'value': 8, '_auto': True},
    ])

### NumPy integration

Access values as NumPy arrays with `array_first`:

```python
params = Params(label_to_extend="date", array_first=True)

params.a
```

    array([2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 8, 8, 8])

```python
params.a * params.b
```

    array([21., 21., 21., 21., 21., 21., 21., 21., 21., 84., 84., 84., 84.])

Only get the values that you want:

```python
arr = params.to_array("a", date=["2020-01-01", "2020-11-01"])
arr
```

    array([2, 8])

Go back to a list of dictionaries:

```python
params.from_array("a", arr, date=["2020-01-01", "2020-11-01"])
```

    [{'date': datetime.date(2020, 1, 1), 'value': 2},
     {'date': datetime.date(2020, 11, 1), 'value': 8}]

## Documentation

Full documentation available at [paramtools.dev](https://paramtools.dev).

## Contributing

Contributions are welcome! Checkout [CONTRIBUTING.md][3] to get started.

## Credits

ParamTools is built on top of the excellent [marshmallow][1] JSON schema and validation framework. I encourage everyone to check out their repo and documentation. ParamTools was modeled off of [Tax-Calculator's][2] parameter processing and validation engine due to its maturity and sophisticated capabilities.

[1]: https://github.com/marshmallow-code/marshmallow
[2]: https://github.com/PSLmodels/Tax-Calculator
[3]: https://github.com/PSLmodels/ParamTools/blob/master/CONTRIBUTING.md
