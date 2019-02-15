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

schema_, defaults_ = get_example_paths('weather')
class WeatherParams(Parameters):
    schema = schema_
    defaults = defaults_

params = WeatherParams(
    initial_state={"month": "November", "dayofmonth": 1},
    array_first=True
)

print(params.state)
# output: {'month': 'November', 'dayofmonth': 1}

```

Parameters are available via instance attributes:

```python
print(params.average_precipitation)
#output:  [[3.6] [3. ]]

```

Get the parameter's [value object](https://paramtools.readthedocs.io/en/latest/spec.html#value-object):
```python
print(params.from_array("average_precipitation"))
# output:  [{'city': 'Atlanta, GA', 'month': 'November', 'value': 3.6}, {'city': 'Washington, D.C.', 'month': 'November', 'value': 3.0}]
```

[Adjust](https://paramtools.readthedocs.io/en/latest/spec.html#adjustment-schema) the default specification:

```python
adjustment = {
    "average_precipitation": [
        {"city": "Washington, D.C.", "month": "November", "value": 10},
        {"city": "Atlanta, GA", "month": "November", "value": 15},
    ]
}
params.adjust(adjustment)
print(params.from_array("average_precipitation"))
#output:  [{'city': 'Atlanta, GA', 'month': 'November', 'value': 15.0}, {'city': 'Washington, D.C.', 'month': 'November', 'value': 10.0}]

print(params.average_precipitation)
#output:  [[15.] [10.]]
```


Errors on invalid input:
```python
adjustment["average_precipitation"][0]["value"] = "rainy"
params.adjust(adjustment)

#output:
Traceback (most recent call last):
  File "doc_ex.py", line 40, in <module>
    raise saved_exc
  File "doc_ex.py", line 30, in <module>
    params.adjust(adjustment)
  File "/home/henrydoupe/Documents/ParamTools/paramtools/parameters.py", line 123, in adjust
    raise self.validation_error
paramtools.exceptions.ValidationError: {'average_precipitation': ['Not a valid number: rainy.']}

```

Errors on input that's out of range:
```python
adjustment["average_precipitation"][0]["value"] = 1000
adjustment["average_precipitation"][1]["value"] = 2000

params.adjust(adjustment, raise_errors=False)

print(params.errors)
#output:  {'average_precipitation': ['average_precipitation 1000.0 must be less than 50 for dimensions city=Washington, D.C. , month=November', 'average_precipitation 2000.0 must be less than 50 for dimensions city=Atlanta, GA , month=November']}

```

How to install ParamTools
-----------------------------------------

Install from PyPI:

```
pip install paramtools
```

Install from source:

```
git clone https://github.com/hdoupe/ParamTools
cd ParamTools
pip install -e .
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