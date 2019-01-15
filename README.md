# ParamTools

ParamTools defines the parameter input space for computational modeling projects.
- Defines the default parameter space.
- Facilitates adjusting that space.
- Performs validation on the default space and the adjusted space.

How to get it
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


Specification Schema
--------------------------------------

Define the dimensions of the parameter space

```json
{
    "schema_name": "weather",
    "dims": {
        "city": {
            "type": "str",
            "validators": {"choice": {"choices": ["Atlanta, GA",
                                                  "Washington, D.C."]}}
        },
        "month": {
            "type": "str",
            "validators": {"choice": {"choices": ["January", "February",
                                                  "March", "April", "May",
                                                  "June", "July", "August",
                                                  "September", "October",
                                                  "November", "December"]}}
        },
        "dayofmonth": {
            "type": "int",
            "validators": {"range": {"min": 1, "max": 31}}
        }
    },
    "optional_params": {
        "scale": {"type": "str", "number_dims": 0},
        "source": {"type": "str", "number_dims": 0}
    }
}
```

The "dims" component of the Specification Schema specifies type and validation information for each dimension in the parameter space. `pararmtools` uses this information to check whether the value is the correct type and meets validation requirements, such as a number falling in the correct range. The "dims" component is used to validate the Default Specification and user adjustments to it.

It is likely that the project needs extra information in addition to that required by the minimum parameter definition required by `pararmtools`. This information could add extra documentation or specify parameters for filling out the remaining parts of the default parameter space. It is stored in the "optional_parameters" component of the Parameter Schema.


Default Specification
---------------------------------------------

Define the default values of the project's parameter space

```json
{
    "average_high_temperature": {
        "long_name": "Average High Temperature",
        "description": "Average high temperature for each day for a selection of cities",
        "notes": "Data has only been collected for Atlanta and Washington and for only the first of the month.",
        "scale": "fahrenheit",
        "source": "NOAA",
        "type": "int",
        "number_dims": 0,
        "value": [
            {"city": "Washington, D.C.", "month": "January", "dayofmonth": 1, "value": 43},
            {"city": "Washington, D.C.", "month": "February", "dayofmonth": 1, "value": 47},
            {"city": "Washington, D.C.", "month": "March", "dayofmonth": 1, "value": 56},
            {"city": "Washington, D.C.", "month": "April", "dayofmonth": 1, "value": 67},
            {"city": "Washington, D.C.", "month": "May", "dayofmonth": 1, "value": 76},
            {"city": "Washington, D.C.", "month": "June", "dayofmonth": 1, "value": 85},
            {"city": "Washington, D.C.", "month": "July", "dayofmonth": 1, "value": 89},
            {"city": "Washington, D.C.", "month": "August", "dayofmonth": 1, "value": 87},
            {"city": "Washington, D.C.", "month": "September", "dayofmonth": 1, "value": 81},
            {"city": "Washington, D.C.", "month": "October", "dayofmonth": 1, "value": 69},
            {"city": "Washington, D.C.", "month": "November", "dayofmonth": 1, "value": 59},
            {"city": "Washington, D.C.", "month": "December", "dayofmonth": 1, "value": 48},
            {"city": "Atlanta, GA", "month": "January", "dayofmonth": 1, "value": 53},
            {"city": "Atlanta, GA", "month": "February", "dayofmonth": 1, "value": 58},
            {"city": "Atlanta, GA", "month": "March", "dayofmonth": 1, "value": 66},
            {"city": "Atlanta, GA", "month": "April", "dayofmonth": 1, "value": 73},
            {"city": "Atlanta, GA", "month": "May", "dayofmonth": 1, "value": 80},
            {"city": "Atlanta, GA", "month": "June", "dayofmonth": 1, "value": 86},
            {"city": "Atlanta, GA", "month": "July", "dayofmonth": 1, "value": 89},
            {"city": "Atlanta, GA", "month": "August", "dayofmonth": 1, "value": 88},
            {"city": "Atlanta, GA", "month": "September", "dayofmonth": 1, "value": 82},
            {"city": "Atlanta, GA", "month": "October", "dayofmonth": 1, "value": 74},
            {"city": "Atlanta, GA", "month": "November", "dayofmonth": 1, "value": 64},
            {"city": "Atlanta, GA", "month": "December", "dayofmonth": 1, "value": 55}
        ],
        "validators": {"range": {"min": -130, "max": 135}},
        "out_of_range_minmsg": "",
        "out_of_range_maxmsg": "",
        "out_of_range_action": "warn"
    },
    "average_precipitation": {
        "long_name": "Average Precipitation",
        "description": "Average precipitation for a selection of cities by month",
        "notes": "Data has only been collected for Atlanta and Washington",
        "scale": "inches",
        "source": "NOAA",
        "type": "float",
        "number_dims": 0,
        "value": [
            {"city": "Washington, D.C.", "month": "January", "value": 3.1},
            {"city": "Washington, D.C.", "month": "February", "value": 2.6},
            {"city": "Washington, D.C.", "month": "March", "value": 3.5},
            {"city": "Washington, D.C.", "month": "April", "value": 3.3},
            {"city": "Washington, D.C.", "month": "May", "value": 4.3},
            {"city": "Washington, D.C.", "month": "June", "value": 4.3},
            {"city": "Washington, D.C.", "month": "July", "value": 4.6},
            {"city": "Washington, D.C.", "month": "August", "value": 3.8},
            {"city": "Washington, D.C.", "month": "September", "value": 3.9},
            {"city": "Washington, D.C.", "month": "October", "value": 3.7},
            {"city": "Washington, D.C.", "month": "November", "value": 3},
            {"city": "Washington, D.C.", "month": "December", "value": 3.5},
            {"city": "Atlanta, GA", "month": "January", "value": 3.6},
            {"city": "Atlanta, GA", "month": "February", "value": 3.7},
            {"city": "Atlanta, GA", "month": "March", "value": 4.3},
            {"city": "Atlanta, GA", "month": "April", "value": 3.5},
            {"city": "Atlanta, GA", "month": "May", "value": 3.8},
            {"city": "Atlanta, GA", "month": "June", "value": 3.6},
            {"city": "Atlanta, GA", "month": "July", "value": 5},
            {"city": "Atlanta, GA", "month": "August", "value": 3.8},
            {"city": "Atlanta, GA", "month": "September", "value": 3.7},
            {"city": "Atlanta, GA", "month": "October", "value": 2.8},
            {"city": "Atlanta, GA", "month": "November", "value": 3.6},
            {"city": "Atlanta, GA", "month": "December", "value": 4.1}
        ],
        "validators": {"range": {"min": 0, "max": 50}},
        "out_of_range_minmsg": "str",
        "out_of_range_maxmsg": "str",
        "out_of_range_action": "stop"
    }
}
```

- `parameter_name`: Name of the variable where this value will be stored
- `long_name`: A "human readable" name that you might use when speaking or writing about this parameter
- `description`: Describes the parameter
- `notes`: Advice for the user pertaining to this parameter
- `type`: Type of the parameter (integer, float, string, boolean, etc)
- `number_dims`: The number of dimensions for the specified value as in [`numpy.ndim`][]
  - e.g. `number_dims` is 1 for `"value': {"city": "Washington", "state": "D.C.", "value": [38, -77]}`, that is "value" points to a one dimensional array `[38, -77]`
- `value`: the default value for this parameter
  - this describes a default value for all points in the parameter space for this particular parameter
  - e.g. if describing the default value for the average temperature in a given city on a given day:
  ```json
    "value": [
        {"city": "Washington, D.C.",
         "month": "November",
         "dayofmonth": 1,
         "value": 50},
        {"city": "Washington, D.C.",
         "month": "March",
         "dayofmonth": 1,
         "value": 49}
    ]
  ```
- `validators`: declares the validation methods that should be used for this parameter.
    - `range`: describes a minimum and maximum value for the parameter
        - the minimum and maximum can point to either "default" or another parameter by its `parameter_name`
        - it could be helpful to have a `choices` operation describing a discrete set of valid values for the parameter
    - `choices`: list of allowed values the parameter's value
- `out_of_range_{min/max/other op}_msg`: extra information to be used in the message(s) that will be displayed if the parameter value is outside of the specified range
- `out_of_range_action`: action to take when specified parameter is outside of the specified range. options are `stop` or `warn`


Adjustment Schema
----------------------------

Adjust a specification

```json
{
    "average_temperature": [
        {"city": "Washington, D.C.",
         "month": "November",
         "dayofmonth": 1,
         "value": 60},
        {"city": "Washington, D.C.",
         "month": "November",
         "dayofmonth": 2,
         "value": 63},
    ],
    "average_precipitation": [
        {"city": "Washington, D.C.",
         "month": "November",
         "dayofmonth": 1,
         "value": 0.2},
    ]
}
```

The Adjustment Schema defines the data format used for adjusting a given specification.

Use the `pararmtools` implementation!
-------------------------------------------

`pararmtools` implements the following parameter validation functionality:
- reads, deserializes, and validates the default specification file
- validates user adjustments on a type, range, and structure basis
  - the range includes min/max on "default" and against other parameters
- Attaches parameters to a class instance to be accessed by the downstream project

It does not yet do:
- Format parameters into an array or other structures that the downstream project may find more convenient


Subclass the `Parameters` class and set your schema and specification files:

```python
from paramtools.parameters import Parameters
from paramtools.utils import get_example_paths

adjustment = {
    "average_high_temperature": [
        {
            "city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 1,
            "value": 60,
        },
        {
            "city": "Atlanta, GA",
            "month": "November",
            "dayofmonth": 1,
            "value": 63,
        },
    ]
}
schema, defaults = get_example_paths('weather')
class WeatherParams(Parameters):
    schema = schema
    defaults = defaults

params = WeatherParams()

```

Query along allowed dimensions:

```python
print(params.get("average_high_temperature", month="November"))

# output: [{'month': 'November', 'city': 'Washington, D.C.', 'value': 59, 'dayofmonth': 1}, {'month': 'November', 'city': 'Atlanta, GA', 'value': 64, 'dayofmonth': 1}]

```

Adjust the default specification:

```python
adjustment = {
    "average_high_temperature": [
        {
            "city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 1,
            "value": 60,
        },
        {
            "city": "Atlanta, GA",
            "month": "November",
            "dayofmonth": 1,
            "value": 63,
        },
    ]
}

params.adjust(adjustment)

# check to make sure the values were updated:
print(params.get("average_high_temperature", month="November"))

# output: [{'month': 'November', 'city': 'Washington, D.C.', 'value': 60, 'dayofmonth': 1}, {'month': 'November', 'city': 'Atlanta, GA', 'value': 63, 'dayofmonth': 1}]
```


Errors on invalid input:
```python
adjustment["average_high_temperature"][0]["value"] = "HOT"
# ==> raises error:
params.adjust(adjustment)

# output: marshmallow.exceptions.ValidationError: {'average_high_temperature': ['Not a valid number.']}

```

Silence the errors by setting `raise_errors` to `False`:
```python
adjustment["average_high_temperature"][0]["value"] = "HOT"
# ==> raises error:
params.adjust(adjustment, raise_errors=False)
print(params.errors)
# output: {'average_high_temperature': ['Not a valid number.']}

```

Errors on input that's out of range:
```python
adjustment["average_high_temperature"][0]["value"] = 2000
adjustment["average_high_temperature"][1]["value"] = 3000

params.adjust(adjustment, raise_errors=False)
print(params.errors)

# ouput:
# {
#     'average_high_temperature': ['average_high_temperature 2000 must be less than 135 for dimensions month=November , city=Washington, D.C. , dayofmonth=1', 'average_high_temperature 3000 must be less than 135 for dimensions month=November , city=Atlanta, GA , dayofmonth=1']
# }

```

Credits: ParamTools is built on top of the excellent [marshmallow][] JSON schema and validation framework. I encourage everyone to checkout their repo and documentation. ParamTools was modeled off of [Tax-Calculator's][] parameter processing and validation engine due to its maturity and sophisticated capabilities.


[`numpy.ndim`]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html
[marshmallow]: https://marshmallow.readthedocs.io/en/3.0/
[Tax-Calculator's]: https://github.com/open-source-economics/Tax-Calculator
