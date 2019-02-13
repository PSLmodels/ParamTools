JSON Spec
=========

Specification Schema
--------------------

Define the dimensions of the parameter space.

-  "schema\_name": Name of the schema.
-  "dims": Mapping of `Dimension objects <#dimension-object>`__.
-  "optional\_params": Mapping of `Optional
   objects <#optional-object>`__.
-  Example:

   .. code:: json

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

Default Specification
---------------------

Define the default values of the project's parameter space.

-  A mapping of `Parameter Objects <#parameter-object>`__.
-  Example:

   .. code:: json

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

Adjustment Schema
-----------------

Adjust a given specification.

-  A mapping of parameters and lists of `Value
   objects <#value-object>`__.
-  Example:

   .. code:: json

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

JSON Object and Property Definitions
------------------------------------

Objects
~~~~~~~

Dimension object
^^^^^^^^^^^^^^^^

-  Used for defining the dimensions of the parameter space.

   -  "type": Define the datatype of the dimension values. See the `Type
      property <#type-property>`__.
   -  "validators": A mapping of `Validator
      objects <#validator-object>`__

   .. code:: json

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

Optional object
^^^^^^^^^^^^^^^

-  Used for defining optional parameters on the schema. Upstream
   projects may find it value to attach additional information to each
   parameter that is not essential for ParamTools to perform validation.

   -  Arguments:

      -  "type": See `Type property <#type-property>`__.
      -  "number\_dims": See `Number-Dimensions
         Property <#number-dimensions-property>`__.

   -  Example:

      .. code:: json

          {
              "scale": {"type": "str", "number_dims": 0},
          }

   -  Note: `Validator objects <#validator-object>`__ may be defined on
      this object in the future.

Parameter object
^^^^^^^^^^^^^^^^

-  Used for documenting the parameter and defining the default value of
   a parameter over the entire parameter space and its validation
   behavior.

   -  Arguments:

      -  "param\_name": The name of the parameter as it is used in the
         modeling project.
      -  "title": "title": A human readable name for the parameter.
      -  "description": Describes the parameter.
      -  "notes": Additional advice or information.
      -  "type": Data type of the parameter. See `Type
         property <#type-property>`__.
      -  "number\_dims": Number of dimensions of the parameter. See
         `Number-Dimensions property <#number-dimensions-property>`__
      -  "value": A list of (Value objects)[#value-object].
      -  "validators": A mapping of (Validator
         objects)[#validator-object]
      -  "out\_of\_range\_{min/max/other op}\_msg": Extra information to
         be used in the message(s) that will be displayed if the
         parameter value is outside of the specified range. Note that
         this is in the spec but not currently implemented.
      -  "out\_of\_range\_action": Action to take when specified
         parameter is outside of the specified range. Options are "stop"
         or "warn". Note that this is in the spec but only "stop" is
         currently implemented.

   -  Example:

      .. code:: json

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

Validator object
^^^^^^^^^^^^^^^^

-  Used for validating user input.
-  Available validators:

   -  "range": Define a minimum and maximum value for a given parameter.

      -  Arguments:

         -  "min": Minimum allowed value.
         -  "max": Maximum allowed value.

      -  Example:

         .. code:: json

             {
                 "range": {"min": 0, "max": 10}
             }

   -  "choice": Define a set of values that this parameter can take.

      -  Arguments:

         -  "choice": List of allowed values.

      -  Example:

         .. code:: json

             {
                 "choice": {"choices": ["allowed choice", "another allowed choice"]}
             }

Value object
^^^^^^^^^^^^

-  Used to describe the value of a parameter for one or more points in
   the parameter space.

   -  "value": The value of the parameter at this point in space.
   -  Zero or more dimension properties that define which parts of the
      parameter space this value should be applied to. These dimension
      properties are defined by `Dimension
      objects <#dimension-object>`__ in the `Specification
      Schema <#specification-schema>`__.

   -  Example:

      .. code:: json

          {
              "city": "Washington, D.C.",
              "month": "November",
              "dayofmonth": 1,
              "value": 50
          }

Properties
~~~~~~~~~~

Type property
^^^^^^^^^^^^^

-  "type": The parameter's data type. Supported types are:

   -  "int": Integer.
   -  "float": Floating point.
   -  "bool": Boolean. Either True or False.
   -  "str"\`: String.
   -  "date": Date. Needs to be of the format "YYYY-MM-DD".
   -  Example:

      .. code:: json

          {
              "type": "int"
          }

Number-Dimensions property
^^^^^^^^^^^^^^^^^^^^^^^^^^

-  "number\_dims": The number of dimensions for the specified value. A
   scalar (e.g. 10) has zero dimensions, a list (e.g. [1, 2]) has one
   dimension, a nested list (e.g. [[1, 2], [3, 4]]) has two dimensions,
   etc.

   -  Example: Note that "value" is a scalar.

      .. code:: json

          {
              "number_dims": 0,
              "value": [{"city": "Washington", "state": "D.C.", "value": 10}]
          }

      Note that "value" is an one-dimensional list.

      .. code:: json

          {
              "number_dims": 1,
              "value": [{"city": "Washington", "state": "D.C.", "value": [38, -77]}]
          }
