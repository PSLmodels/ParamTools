ParamTools
==========

ParamTools defines the parameter input space for computational modeling
projects.

-  Defines the default parameter space.
-  Facilitates adjusting that space.
-  Performs validation on the default space and the adjusted space.

How to use ParamTools
---------------------

Subclass the ``Parameters`` class and set your `specification
schema <#specification-schema>`__ and `default
specification <#default-specification>`__ files:

.. code:: python

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

Parameters are available via instance attributes:

.. code:: python

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

Set state for the parameters:

.. code:: python

    In [3]: params.set_state(month="November")

    In [3]: params.state
    Out[3]: {'month': 'November'}

    In [4]: params.average_precipitation
    Out[4]:
    [{'value': 3.0, 'month': 'November', 'city': 'Washington, D.C.'},
     {'value': 3.6, 'month': 'November', 'city': 'Atlanta, GA'}]

`Adjust <#adjustment-schema>`__ the default specification:

.. code:: python

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

Errors on invalid input:

.. code:: python

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

Silence the errors by setting ``raise_errors`` to ``False``:

.. code:: python

    In [7]: adjustment["average_precipitation"][0]["value"] = "rainy"
       ...: params.adjust(adjustment, raise_errors=False)
       ...:
       ...: params.errors
       ...:
       ...:
    Out[7]: {'average_precipitation': ['Not a valid number: rainy.']}

Errors on input that's out of range:

.. code:: python

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

Convert `Value objects <#value-object>`__ to and from arrays:

.. code:: python

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

How to install ParamTools
-------------------------

Install from PyPI:

::

    pip install paramtools

Install from source:

::

    git clone https://github.com/hdoupe/ParamTools
    cd ParamTools
    pip install -e .

Credits
-------

ParamTools is built on top of the excellent [marshmallow][] JSON schema
and validation framework. I encourage everyone to checkout their repo
and documentation. ParamTools was modeled off of [Tax-Calculator's][]
parameter processing and validation engine due to its maturity and
sophisticated capabilities.
