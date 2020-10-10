# ParamTools

Define, update, and validate your model's parameters.

How to use ParamTools
---------------------------

Subclass `paramtools.Parameters` and define your model's [parameters](https://paramtools.dev/parameters):

```python
import paramtools


class TaxParams(paramtools.Parameters):
    defaults = {
        "schema": {
            "labels": {
                "year": {
                    "type": "int",
                    "validators": {"range": {"min": 2013, "max": 2027}}
                },
                "marital_status": {
                    "type": "str",
                    "validators": {"choice": {"choices": ["single", "joint"]}}
                },
            },
            "additional_members": {
                "cpi_inflatable": {"type": "bool", "number_dims": 0},
                "cpi_inflated": {"type": "bool", "number_dims": 0}
            }
        },
        "standard_deduction": {
            "title": "Standard deduction amount",
            "description": "Amount filing unit can use as a standard deduction.",
            "cpi_inflatable": True,
            "cpi_inflated": True,
            "type": "float",
            "value": [
                {"year": 2024, "marital_status": "single", "value": 13673.68},
                {"year": 2024, "marital_status": "joint", "value": 27347.36},
                {"year": 2025, "marital_status": "single", "value": 13967.66},
                {"year": 2025, "marital_status": "joint", "value": 27935.33},
                {"year": 2026, "marital_status": "single", "value": 7690.0},
                {"year": 2026, "marital_status": "joint", "value": 15380.0}],
            "validators": {
                "range": {
                    "min": 0,
                    "max": 9e+99
                }
            }
        },
    }

params = TaxParams(
    initial_state={"year": [2024, 2025, 2026]},
    array_first=True
)


```

Check out the state:

```python
params.view_state()

# {'year': [2024, 2025, 2026]}

```

Parameters are available via instance attributes:

```python
params.standard_deduction

# array([[13673.68, 27347.36],
#        [13967.66, 27935.33],
#        [ 7690.  , 15380.  ]])
```

Take a look at the standard deduction parameter's labels:
```python
params.from_array("standard_deduction")

# [{'year': 2024, 'marital_status': 'single', 'value': 13673.68},
#  {'year': 2024, 'marital_status': 'joint', 'value': 27347.36},
#  {'year': 2025, 'marital_status': 'single', 'value': 13967.66},
#  {'year': 2025, 'marital_status': 'joint', 'value': 27935.33},
#  {'year': 2026, 'marital_status': 'single', 'value': 7690.0},
#  {'year': 2026, 'marital_status': 'joint', 'value': 15380.0}]
```

Query the parameters:
```python
params.specification(year=2026, marital_status="single", use_state=False)

# OrderedDict([('standard_deduction',
#               [{'value': 0.0, 'year': 2026, 'marital_status': 'single'}])])
```

Adjust the default values:

```python
adjustment = {
    "standard_deduction": [
        {"year": 2026, "marital_status": "single", "value": 10000.0}
    ],
}
params.adjust(adjustment)
params.standard_deduction

# array([[13673.68, 27347.36],
#        [13967.66, 27935.33],
#        [10000.  , 15380.  ]])

```

Set all values of the standard deduction parameter to 0:

```python
adjustment = {
    "standard_deduction": 0,
}
params.adjust(adjustment)
params.standard_deduction

# array([[0., 0.],
#        [0., 0.],
#        [0., 0.]])

```


Errors on invalid input:
```python
adjustment["standard_deduction"] = "higher"
params.adjust(adjustment)

# ---------------------------------------------------------------------------
# ValidationError                           Traceback (most recent call last)
# <ipython-input-7-d9ad03cf54d8> in <module>
#       1 adjustment["standard_deduction"] = "higher"
# ----> 2 params.adjust(adjustment)

# ~/Documents/ParamTools/paramtools/parameters.py in adjust(self, params_or_path, raise_errors)
#     134
#     135         if raise_errors and self._errors:
# --> 136             raise self.validation_error
#     137
#     138         # Update attrs.

# ValidationError: {'standard_deduction': ['Not a valid number: higher.']}
```

Errors on input that's out of range:

```python
adjustment["standard_deduction"] = [
    {"marital_status": "single", "year": 2025, "value": -1}
]
params.adjust(adjustment)

# output:
# ---------------------------------------------------------------------------
# ValidationError                           Traceback (most recent call last)
# <ipython-input-14-208948dfbd1d> in <module>
#       1 adjustment["standard_deduction"] = [{"marital_status": "single", "year": 2025, "value": -1}]
# ----> 2 params.adjust(adjustment)

# ~/Documents/ParamTools/paramtools/parameters.py in adjust(self, params_or_path, raise_errors, extend_adj)
#     183
#     184         if raise_errors and self._errors:
# --> 185             raise self.validation_error
#     186
#     187         if self.label_to_extend is not None and extend_adj:

# ValidationError: {
#     "standard_deduction": [
#         "standard_deduction[marital_status=single, year=2025] -1.0 < min 0 "
#     ]
# }

```

How to install ParamTools
-----------------------------------------

Install with conda:

```
conda install -c conda-forge paramtools
```

Install from source:

```
git clone https://github.com/PSLmodels/ParamTools
cd ParamTools
conda env create
conda activate paramtools-dev
pip install -e .

# optionally run tests:
py.test -v
```

Documentation
----------------
Full documentation available at [paramtools.dev](https://paramtools.dev).

Contributing
-------------------------
Contributions are welcome! Checkout [CONTRIBUTING.md][3] to get started.

Credits
---------
ParamTools is built on top of the excellent [marshmallow][1] JSON schema and validation framework. I encourage everyone to check out their repo and documentation. ParamTools was modeled off of [Tax-Calculator's][2] parameter processing and validation engine due to its maturity and sophisticated capabilities.

[1]: https://github.com/marshmallow-code/marshmallow
[2]: https://github.com/PSLmodels/Tax-Calculator
[3]: https://github.com/PSLmodels/ParamTools/blob/master/CONTRIBUTING.md
