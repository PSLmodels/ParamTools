# ParamTools

ParamTools defines the parameter input space for computational modeling projects.
- Defines the default parameter space.
- Facilitates adjusting that space.
- Performs validation on the default space and the adjusted space.

How to use ParamTools
---------------------------

Subclass the `Parameters` class and set your [specification schema](#specification-schema) and [default specification](#default-specification) files:

```python
In [1]: from paramtools import Parameters
   ...: from paramtools import get_example_paths
   ...:
   ...: schema, defaults = get_example_paths('weather')
   ...:
   ...: class WeatherParams(Parameters):
   ...:     schema = schema
   ...:     defaults = defaults
   ...:
   ...: params = WeatherParams()
   ...:
   ...:

```

Parameters are available via instance attributes:

```python
In [2]: params.average_precipitation
Out[2]:
[{'city': 'Washington, D.C.', 'value': 3.1, 'month': 'January'},
 {'city': 'Washington, D.C.', 'value': 2.6, 'month': 'February'},
 {'city': 'Washington, D.C.', 'value': 3.5, 'month': 'March'},
 {'city': 'Washington, D.C.', 'value': 3.3, 'month': 'April'},
 {'city': 'Washington, D.C.', 'value': 4.3, 'month': 'May'},
 {'city': 'Washington, D.C.', 'value': 4.3, 'month': 'June'},
 {'city': 'Washington, D.C.', 'value': 4.6, 'month': 'July'},
 {'city': 'Washington, D.C.', 'value': 3.8, 'month': 'August'},
 {'city': 'Washington, D.C.', 'value': 3.9, 'month': 'September'},
 {'city': 'Washington, D.C.', 'value': 3.7, 'month': 'October'},
 {'city': 'Washington, D.C.', 'value': 3.0, 'month': 'November'},
 {'city': 'Washington, D.C.', 'value': 3.5, 'month': 'December'},
 {'city': 'Atlanta, GA', 'value': 3.6, 'month': 'January'},
 {'city': 'Atlanta, GA', 'value': 3.7, 'month': 'February'},
 {'city': 'Atlanta, GA', 'value': 4.3, 'month': 'March'},
 {'city': 'Atlanta, GA', 'value': 3.5, 'month': 'April'},
 {'city': 'Atlanta, GA', 'value': 3.8, 'month': 'May'},
 {'city': 'Atlanta, GA', 'value': 3.6, 'month': 'June'},
 {'city': 'Atlanta, GA', 'value': 5.0, 'month': 'July'},
 {'city': 'Atlanta, GA', 'value': 3.8, 'month': 'August'},
 {'city': 'Atlanta, GA', 'value': 3.7, 'month': 'September'},
 {'city': 'Atlanta, GA', 'value': 2.8, 'month': 'October'},
 {'city': 'Atlanta, GA', 'value': 3.6, 'month': 'November'},
 {'city': 'Atlanta, GA', 'value': 4.1, 'month': 'December'}]


```

Set state for the parameters:

```python
In [3]: params.set_state(month="November")

In [3]: params.state
Out[3]: {'month': 'November'}

In [4]: params.average_precipitation
Out[4]:
[{'value': 3.0, 'month': 'November', 'city': 'Washington, D.C.'},
 {'value': 3.6, 'month': 'November', 'city': 'Atlanta, GA'}]
```

[Adjust](#adjustment-schema) the default specification:

```python
In [5]: adjustment = {
   ...:     "average_precipitation": [
   ...:         {
   ...:             "city": "Washington, D.C.",
   ...:             "month": "November",
   ...:             "value": 10,
   ...:         },
   ...:         {
   ...:             "city": "Atlanta, GA",
   ...:             "month": "November",
   ...:             "value": 15,
   ...:         },
   ...:     ]
   ...: }
   ...:
   ...: params.adjust(adjustment)
   ...:
   ...: # check to make sure the values were updated:
   ...: params.average_precipitation
   ...:
   ...:
Out[5]:
[{'value': 10.0, 'month': 'November', 'city': 'Washington, D.C.'},
 {'value': 15.0, 'month': 'November', 'city': 'Atlanta, GA'}]
```


Errors on invalid input:
```python
In [6]: adjustment["average_precipitation"][0]["value"] = "rainy"
   ...: # ==> raises error
   ...: params.adjust(adjustment)
   ...:
   ...:
---------------------------------------------------------------------------
ValidationError                           Traceback (most recent call last)
<ipython-input-6-af74e66e2b48> in <module>()
      1 adjustment["average_precipitation"][0]["value"] = "rainy"
      2 # ==> raises error
----> 3 params.adjust(adjustment)

~/Documents/ParamTools/paramtools/parameters.py in adjust(self, params_or_path, raise_errors)
    112
    113         if raise_errors and self._errors:
--> 114             raise self.validation_error
    115
    116         # Update attrs.

ValidationError: {'average_precipitation': ['Not a valid number: rainy.']}

```

Silence the errors by setting `raise_errors` to `False`:
```python
In [7]: adjustment["average_precipitation"][0]["value"] = "rainy"
   ...: params.adjust(adjustment, raise_errors=False)
   ...:
   ...: params.errors
   ...:
   ...:
Out[7]: {'average_precipitation': ['Not a valid number: rainy.']}

```

Errors on input that's out of range:
```python
In [8]: adjustment["average_precipitation"][0]["value"] = 1000
   ...: adjustment["average_precipitation"][1]["value"] = 2000
   ...:
   ...: params.adjust(adjustment, raise_errors=False)
   ...:
   ...: params.errors
   ...:
   ...:
Out[8]:
{'average_precipitation': ['average_precipitation 1000.0 must be less than 50 for dimensions city=Washington, D.C. , month=November',
  'average_precipitation 2000.0 must be less than 50 for dimensions city=Atlanta, GA , month=November']}

```

Convert [Value objects](#value-object) to and from arrays:
```python
In [9]: arr = params.to_array("average_precipitation")
   ...: arr
   ...:
   ...:
Out[9]:
array([[15.],
       [10.]])

In [10]: vi_list = params.from_array("average_precipitation", arr)
    ...:

In [11]: vi_list
Out[11]:
[{'city': 'Atlanta, GA', 'month': 'November', 'value': 15.0},
 {'city': 'Washington, D.C.', 'month': 'November', 'value': 10.0}]

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

Credits: ParamTools is built on top of the excellent [marshmallow][] JSON schema and validation framework. I encourage everyone to checkout their repo and documentation. ParamTools was modeled off of [Tax-Calculator's][] parameter processing and validation engine due to its maturity and sophisticated capabilities.

Specification Schema
--------------------------------------

Define the dimensions of the parameter space.

- "schema_name": Name of the schema.
- "dims": Mapping of [Dimension objects](#dimension-object).
- "optional_params": Mapping of [Optional objects](#optional-object).
- Example:
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
        "optional": {
            "scale": {"type": "str", "number_dims": 0},
            "source": {"type": "str", "number_dims": 0}
        }
    }
    ```

Default Specification
---------------------------------------------

Define the default values of the project's parameter space.
- A mapping of [Parameter Objects](#parameter-object).
- Example:
    ```json
    {
        "average_high_temperature": {
            "title": "Average High Temperature",
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
            "title": "Average Precipitation",
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


Adjustment Schema
----------------------------

Adjust a given specification.
- A mapping of parameters and lists of [Value objects](#value-object).
- Example:
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

JSON Object and Property Definitions
---------------------------------------

### Objects

#### Dimension object
- Used for defining the dimensions of the parameter space.
  - "type": Define the datatype of the dimension values. See the [Type property](#type-property).
  - "validators": A mapping of [Validator objects](#validator-object)

    ```json
    {
        "month": {
            "type": "str",
            "validators": {"choice": {"choices": ["January", "February",
                                                    "March", "April", "May",
                                                    "June", "July", "August",
                                                    "September", "October",
                                                    "November", "December"]}}
        },
    }
    ```

#### Optional object
- Used for defining optional parameters on the schema. Upstream projects may
  find it value to attach additional information to each parameter that is
  not essential for ParamTools to perform validation.
  - Arguments:
    - "type": See [Type property](#type-property).
    - "number_dims": See [Number-Dimensions Property](#number-dimensions-property).
  - Example:
    ```json
    {
        "scale": {"type": "str", "number_dims": 0},
    }
    ```
  - Note: [Validator objects](#validator-object) may be defined on this object in the future.


#### Parameter object
- Used for documenting the parameter and defining the default value of a parameter over the entire parameter space and its validation behavior.
  - Arguments:
    - "param_name": The name of the parameter as it is used in the modeling project.
    - "title": "title": A human readable name for the parameter.
    - "description": Describes the parameter.
    - "notes": Additional advice or information.
    - "type": Data type of the parameter. See [Type property](#type-property).
    - "number_dims": Number of dimensions of the parameter. See [Number-Dimensions property](#number-dimensions-property)
    - "value": A list of (Value objects)[#value-object].
    - "validators": A mapping of (Validator objects)[#validator-object]
    - "out_of_range_{min/max/other op}_msg": Extra information to be used in the message(s) that will be displayed if the parameter value is outside of the specified range. Note that this is in the spec but not currently implemented.
    - "out_of_range_action": Action to take when specified parameter is outside of the specified range. Options are "stop" or "warn". Note that this is in the spec but only "stop" is currently implemented.
  - Example:
    ```json
    {
        "title": "Average Precipitation",
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
            {"city": "Atlanta, GA", "month": "February", "value": 3.7}
        ],
        "validators": {"range": {"min": 0, "max": 50}},
        "out_of_range_minmsg": "str",
        "out_of_range_maxmsg": "str",
        "out_of_range_action": "stop"
    }
    ```

#### Validator object
- Used for validating user input.
- Available validators:
  - "range": Define a minimum and maximum value for a given parameter.
    - Arguments:
      - "min": Minimum allowed value.
      - "max": Maximum allowed value.
    - Example:
        ```json
        {
            "range": {"min": 0, "max": 10}
        }
        ```
  - "choice": Define a set of values that this parameter can take.
    - Arguments:
      - "choice": List of allowed values.
    - Example:
        ```json
        {
            "choice": {"choices": ["allowed choice", "another allowed choice"]}
        }
        ```

#### Value object
- Used to describe the value of a parameter for one or more points in the parameter space.
  - "value": The value of the parameter at this point in space.
  - Zero or more dimension properties that define which parts of the parameter space this value should be applied to. These dimension properties are defined by [Dimension objects](#dimension-object) in the [Specification Schema](#specification-schema).
  - Example:
  ```json
        {"city": "Washington, D.C.",
         "month": "November",
         "dayofmonth": 1,
         "value": 50},
  ```


### Properties

#### Type property
- "type": The parameter's data type. Supported types are:
    - "int": Integer.
    - "float": Floating point.
    - "bool": Boolean. Either True or False.
    - "str"`: String.
    - "date": Date. Needs to be of the format "YYYY-MM-DD".
    - Example:
        ```json
        {
            "type": "int"
        }
        ```

#### Number-Dimensions property
- "number_dims": The number of dimensions for the specified value. A scalar (e.g. 10) has zero dimensions, a list (e.g. [1, 2]) has one dimension, a nested list (e.g. [[1, 2], [3, 4]]) has two dimensions, etc.
  - Example:
   Note that "value" is a scalar.
   ```json
   {
       "number_dims": 0,
       "value": [{"city": "Washington", "state": "D.C.", "value": 10}]
   }
   ```

   Note that "value" is an one-dimensional list.
   ```json
   {
       "number_dims": 1,
       "value": [{"city": "Washington", "state": "D.C.", "value": [38, -77]}]
   }
   ```


[`numpy.ndim`]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html
[marshmallow]: https://marshmallow.readthedocs.io/en/3.0/
[Tax-Calculator's]: https://github.com/open-source-economics/Tax-Calculator
