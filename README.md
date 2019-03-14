# ParamTools

ParamTools defines the parameter input space for computational modeling projects.

- Defines the default parameter space.
- Facilitates adjusting that space.
- Performs validation on the default space and the adjusted space.

How to use ParamTools
---------------------------

Subclass the `Parameters` class and set your [specification schema](https://paramtools.readthedocs.io/en/latest/spec.html#specification-schema) and [default specification](https://paramtools.readthedocs.io/en/latest/spec.html#default-specification) files:

```python
from paramtools import Parameters
from paramtools import get_example_paths

schema_, defaults_ = get_example_paths('taxparams-demo')
class TaxParams(Parameters):
    schema = schema_  # schema.json
    defaults = defaults_  # defaults.json

params = TaxParams(
    initial_state={"year": [2024, 2025, 2026]},
    array_first=True
)

print("# output ", params.view_state())
# output  {'year': [2024, 2025, 2026]}

```

Parameters are available via instance attributes:

```python
params.standard_deduction
# output:  [[13673.68 27347.36 13673.68 20510.52 27347.36]
#  [13967.66 27935.33 13967.66 20951.49 27935.33]
#  [ 7690.   15380.    7690.   11323.   15380.  ]]


```

Get the parameter's [value object](https://paramtools.readthedocs.io/en/latest/spec.html#value-object):
```python
params.from_array("standard_deduction")
# output:  [{'year': 2024, 'marital_status': 'single', 'value': 13673.68}, {'year': 2024, 'marital_status': 'joint', 'value': 27347.36}, {'year': 2024, 'marital_status': 'separate', 'value': 13673.68}, {'year': 2024, 'marital_status': 'headhousehold', 'value': 20510.52}, {'year': 2024, 'marital_status': 'widow', 'value': 27347.36}, {'year': 2025, 'marital_status': 'single', 'value': 13967.66}, {'year': 2025, 'marital_status': 'joint', 'value': 27935.33}, {'year': 2025, 'marital_status': 'separate', 'value': 13967.66}, {'year': 2025, 'marital_status': 'headhousehold', 'value': 20951.49}, {'year': 2025, 'marital_status': 'widow', 'value': 27935.33}, {'year': 2026, 'marital_status': 'single', 'value': 7690.0}, {'year': 2026, 'marital_status': 'joint', 'value': 15380.0}, {'year': 2026, 'marital_status': 'separate', 'value': 7690.0}, {'year': 2026, 'marital_status': 'headhousehold', 'value': 11323.0}, {'year': 2026, 'marital_status': 'widow', 'value': 15380.0}]
```

[Adjust](https://paramtools.readthedocs.io/en/latest/spec.html#adjustment-schema) the default specification:

```python
adjustment = {
    "standard_deduction": [
        {"year": 2026, "marital_status": "single", "value": 10000.0}
    ],
    "social_security_tax_rate": [
        {"year": 2026, "value": 0.14}
    ]
}
params.adjust(adjustment)
params.standard_deduction
# output:  [[13673.68 27347.36 13673.68 20510.52 27347.36]
#  [13967.66 27935.33 13967.66 20951.49 27935.33]
#  [10000.   15380.    7690.   11323.   15380.  ]]

print(params.social_security_tax_rate)
# output:  [0.124 0.124 0.14 ]
```


Errors on invalid input:
```python
adjustment["standard_deduction"] = [{
  "year": 2026,
  "marital_status": "single",
  "value": "higher"
}]
params.adjust(adjustment)

# output:
Traceback (most recent call last):
  File "doc_ex.py", line 60, in <module>
    raise saved_exc
  File "doc_ex.py", line 33, in <module>
    params.adjust(adjustment)
  File "/home/henrydoupe/Documents/ParamTools/paramtools/parameters.py", line 123, in adjust
    raise self.validation_error
paramtools.exceptions.ValidationError: {'standard_deduction': ['Not a valid number: higher.']}

```

Errors on input that's out of range:
```python
# get value of ii_bracket_2 at year 2026, marital status "single".
spec = params.specification(year=2026, marital_status="single", use_state=False)
spec
# output:  OrderedDict([('standard_deduction', [{'year': 2026, 'value': 10000.0, 'marital_status': 'single'}]), ('ii_bracket_1', [{'year': 2026, 'value': 11293.0, 'marital_status': 'single'}]), ('ii_bracket_2', [{'year': 2026, 'value': 45957.0, 'marital_status': 'single'}]), ('social_security_tax_rate', [{'year': 2026, 'value': 0.14}])])


ii_bracket_2_val = spec["ii_bracket_2"][0]["value"]
ii_bracket_2_val
# output: 45957.0

adjustment = {
    "standard_deduction": [{
      "year": 2026,
      "marital_status": "single",
      "value": -1
    }],
    "ii_bracket_1": [{
      "year": 2026,
      "marital_status": "single",
      "value": ii_bracket_2_val + 1}
    ]
}

params.adjust(adjustment, raise_errors=False)
params.errors
# output:
# {
#   'standard_deduction': ['standard_deduction -1.0 must be greater than 0 for dimensions marital_status=single , year=2026'],
#   'ii_bracket_1': ['ii_bracket_1 45958.0 must be less than 45957.0 for dimensions marital_status=single , year=2026']
# }

```

How to install ParamTools
-----------------------------------------

Install from PyPI:

```
conda install paramtools -c pslmodels
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
Full documentation available at https://paramtools.readthedocs.io/.

Contributing
-------------------------
Contributions are welcome! Checkout [CONTRIBUTING.md][3] to get started.

Credits
---------
ParamTools is built on top of the excellent [marshmallow][1] JSON schema and validation framework. I encourage everyone to checkout their repo and documentation. ParamTools was modeled off of [Tax-Calculator's][2] parameter processing and validation engine due to its maturity and sophisticated capabilities.

[1]: https://github.com/marshmallow-code/marshmallow
[2]: https://github.com/PSLmodels/Tax-Calculator
[3]: https://github.com/PSLmodels/ParamTools/blob/master/CONTRIBUTING.md