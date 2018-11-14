ParamTools defines the parameter input space for computational modeling projects.
- Defines the baseline parameter space.
- Facilitates updating that space.
- Performs validation on the baseline space and the updated space.


Step 1: Define the parameter schema
--------------------------------------
The project is required to fill in the dimensions of its parameter space.

```json
{
    "schema_name": "weather",
    "dims": {
        "city": {
            "type": "str",
            "validator": {"name": "OneOf",
                          "args": {"choices": ["Atlanta, GA",
                                               "Washington, D.C."]}}
        },
        "month": {
            "type": "str",
            "validator": {"name": "OneOf",
                          "args": {"choices": ["January", "February", "March",
                                               "April", "May", "June", "July",
                                               "August", "September", "October",
                                               "November", "December"]}}
        },
        "dayofmonth": {
            "type": "int",
            "validator": {"name": "Range", "args": {"min": 1, "max": 31}}
        }
    },
    "optional_params": {
        "scale": {"type": "str", "number_dims": 0},
        "source": {"type": "str", "number_dims": 0}
    }
}
```

The "dims" component of the Parameter Schema Definition specifies type and range information for each dimension in the parameter space. `pararmtools` uses this information to check whether the value is the correct type and meets validation requirements, such as a number falling in the correct range. The "dims" component is used to validate the baseline parameter specification and user revisions to it.

It is likely that the project needs extra information in addition to that required by the minimum parameter definition required by `pararmtools`. This information could add extra documentation or specify parameters for filling out the remaining parts of the baseline parameter space. It is stored in the "optional_parameters" component of the Parameter Schema Definition.


Step 2: Define the project's parameter space
---------------------------------------------
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
            {"city": "Atlanta, GA", "month": "January", "dayofmonth": 1, "value": 53},
            {"city": "Atlanta, GA", "month": "February", "dayofmonth": 1, "value": 58},
        ],
        "range": {"min": -130, "max": 135},
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
            {"city": "Atlanta, GA", "month": "January", "value": 3.6},
            {"city": "Atlanta, GA", "month": "February", "value": 3.7},
        ],
        "range": {"min": 0, "max": 50},
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
- `value`: the baseline value for this parameter
  - this describes a baseline value for all points in the parameter space for this particular parameter
  - e.g. if describing the baseline value for the average temperature in a given city on a given day:
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
- `range`: describes a minimum and maximum value for the parameter
  - the minimum and maximum can point to either "default" or another parameter by its `parameter_name`
  - it could be helpful to have a `choices` operation describing a discrete set of valid values for the parameter
- `out_of_range_{min/max/other op}_msg`: extra information to be used in the message(s) that will be displayed if the parameter value is outside of the specified range
- `out_of_range_action`: action to take when specified parameter is outside of the specified range. options are `stop` or `warn`


Step 3: Revise the schema
----------------------------
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

The Revision Schema defines the data format used for revising baseline parameters. This schema is defined using the parameter space dimension from the Project Schema Definition and the "type" and "num_dimensions" fields in the Base Schema Definition.

Step 4: Use the `pararmtools` implementation!
-------------------------------------------

`pararmtools` implements the following parameter validation functionality:
- reads, deserializes, and validates the baseline parameter file
- validates user revisions on a type, range, and structure basis
  - the range includes min/max on "default" and against other parameters

It does not yet do:
- Attach parameters to a class instance to be accessed by the downstream project
- Format parameters into an array or other structures that the downstream project may find more convenient

`pararmtools` can be used like:

```python
# in directory pararmtools/
from paramtools.build_schema import SchemaBuilder
from paramtools.utils import get_example_paths

revision = """
{
    "average_high_temperature": [
        {"city": "Washington, D.C.",
        "month": "November",
        "dayofmonth": 1,
        "value": 60},
        {"city": "Washington, D.C.",
        "month": "November",
        "dayofmonth": 2,
        "value": 63}
    ]
}
"""
schema_def_path, base_spec_path = get_example_paths('weather')
sb = SchemaBuilder(schema_def_path, base_spec_path)
sb.build_schemas()
deserialized_revision = sb.load_params(revision)
print(deserialized_revision)

# output:
{'average_high_temperature': [{'dayofmonth': 1,
   'month': 'November',
   'city': 'Washington, D.C.',
   'value': 60},
  {'dayofmonth': 2,
   'month': 'November',
   'city': 'Washington, D.C.',
   'value': 63}]}


# change value of int parameter to string:
revision["average_high_temperature"][0]["value"] = "HOT"
# ==> raises error:
deserialized_revision = sb.load_params(revision)
```

`deserialized_revision` is a validated, deserialized Python object that can now safely be used for modeling, running simulations, etc.

Credits: `pararmtools` is built on top of the excellent [marshmallow][] JSON schema and validation framework. I encourage everyone to checkout their repo and documentation.


[`numpy.ndim`]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html
[marshmallow]: https://marshmallow.readthedocs.io/en/3.0/