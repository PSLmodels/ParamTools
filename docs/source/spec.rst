JSON Spec
=========

Specification Schema
--------------------

Define the labels of the parameter space.

-  "schema\_name": Name of the schema.
-  "labels": Mapping of `Label objects <#label-object>`__.
-  "optional\_params": Mapping of `Optional
   objects <#optional-object>`__.
-  Example:

   .. code:: json

        {
            "schema_name": "policy",
            "labels": {
                "year": {
                    "type": "int",
                    "validators": {"range": {"min": 2013, "max": 2027}}
                },
                "marital_status": {
                    "type": "str",
                    "validators": {"choice": {"choices": ["single", "joint", "separate",
                                                        "headhousehold", "widow"]}}
                },
                "idedtype": {
                    "type": "str",
                    "validators": {"choice": {"choices": ["medical", "statelocal",
                                                        "realestate", "casualty",
                                                        "misc", "interest", "charity"]}}
                },
                "EIC": {
                    "type": "str",
                    "validators": {"choice": {"choices": ["0kids", "1kid",
                                                        "2kids", "3+kids"]}}
                }
            },
            "optional": {
                "section_1": {"type": "str", "number_dims": 0},
                "section_2": {"type": "str", "number_dims": 0},
                "section_3": {"type": "str", "number_dims": 0},
                "irs_ref": {"type": "str", "number_dims": 0},
                "start_year": {"type": "int", "number_dims": 0},
                "cpi_inflatable": {"type": "bool", "number_dims": 0},
                "cpi_inflated": {"type": "bool", "number_dims": 0},
                "compatible_data": {"type": "compatible_data", "number_dims": null}
            }
        }


Default Specification
---------------------

Define the default values of the project"s parameter space.

-  A mapping of `Parameter Objects <#parameter-object>`__.
-  Example:

   .. code:: json

        {
            "standard_deduction": {
        "title": "Standard deduction amount",
                "description": "Amount filing unit can use as a standard deduction.",
                "section_1": "Standard Deduction",
                "section_2": "Standard Deduction Amount",
                "irs_ref": "Form 1040, line 8, instructions. ",
                "notes": "",
                "start_year": 2024,
                "cpi_inflatable": true,
                "cpi_inflated": true,
                "type": "float",
                "number_dims": 0,
                "value": [
                    {"year": 2024, "marital_status": "single", "value": 13673.68},
                    {"year": 2024, "marital_status": "joint", "value": 27347.36},
                    {"year": 2024, "marital_status": "separate", "value": 13673.68},
                    {"year": 2024, "marital_status": "headhousehold", "value": 20510.52},
                    {"year": 2024, "marital_status": "widow", "value": 27347.36},
                    {"year": 2025, "marital_status": "single", "value": 13967.66},
                    {"year": 2025, "marital_status": "joint", "value": 27935.33},
                    {"year": 2025, "marital_status": "separate", "value": 13967.66},
                    {"year": 2025, "marital_status": "headhousehold", "value": 20951.49},
                    {"year": 2025, "marital_status": "widow", "value": 27935.33},
                    {"year": 2026, "marital_status": "single", "value": 7690.0},
                    {"year": 2026, "marital_status": "joint", "value": 15380.0},
                    {"year": 2026, "marital_status": "separate", "value": 7690.0},
                    {"year": 2026, "marital_status": "headhousehold", "value": 11323.0},
                    {"year": 2026, "marital_status": "widow", "value": 15380.0}],
                "out_of_range_minmsg": "",
                "out_of_range_maxmsg": "",
                "out_of_range_action": "stop",
                "validators": {
                    "range": {
                        "min": 0,
                        "max": 9e+99
                    }
                }
            },
            "social_security_tax_rate": {
                "description": "Social Security FICA rate, including both employer and employee.",
                "section_1": "Payroll Taxes",
                "section_2": "Social Security FICA",
                "irs_ref": "",
                "notes": "",
                "start_year": 2026,
                "cpi_inflatable": false,
                "cpi_inflated": false,
                "value": [
                    {"year": 2024, "value": 0.124},
                    {"year": 2025, "value": 0.124},
                    {"year": 2026, "value": 0.124}
                ],
                "out_of_range_minmsg": "",
                "out_of_range_maxmsg": "",
                "out_of_range_action": "stop",
                "number_dims": 0,
                "title": "Social Security payroll tax rate",
                "type": "float",
                "validators": {
                    "range": {
                        "min": 0,
                        "max": 1
                    }
                }
            },
            "ii_bracket_1": {
                "title": "Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 1",
                "description": "Taxable income below this threshold is taxed at tax rate 1.",
                "section_1": "Personal Income",
                "section_2": "Regular: Non-AMT, Non-Pass-Through",
                "irs_ref": "Form 1040, line 44, instruction (Schedule XYZ).",
                "notes": "",
                "start_year": 2013,
                "cpi_inflatable": true,
                "cpi_inflated": true,
                "number_dims": 0,
                "type": "float",
                "value": [
                    {"year": 2024, "marital_status": "single", "value": 10853.48},
                    {"year": 2024, "marital_status": "joint", "value": 21706.97},
                    {"year": 2024, "marital_status": "separate", "value": 10853.48},
                    {"year": 2024, "marital_status": "headhousehold", "value": 15496.84},
                    {"year": 2024, "marital_status": "widow", "value": 21706.97},
                    {"year": 2025, "marital_status": "single", "value": 11086.83},
                    {"year": 2025, "marital_status": "joint", "value": 22173.66},
                    {"year": 2025, "marital_status": "separate", "value": 11086.83},
                    {"year": 2025, "marital_status": "headhousehold", "value": 15830.02},
                    {"year": 2025, "marital_status": "widow", "value": 22173.66},
                    {"year": 2026, "marital_status": "single", "value": 11293.0},
                    {"year": 2026, "marital_status": "joint", "value": 22585.0},
                    {"year": 2026, "marital_status": "separate", "value": 11293.0},
                    {"year": 2026, "marital_status": "headhousehold", "value": 16167.0},
                    {"year": 2026, "marital_status": "widow", "value": 22585.0}],
                "out_of_range_minmsg": "",
                "out_of_range_maxmsg": "for _II_brk2",
                "out_of_range_action": "stop",
                "validators": {
                    "range": {
                        "min": 0,
                        "max": "ii_bracket_2"
                    }
                }
            },
            "ii_bracket_2": {
                "title": "Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 2",
                "description": "Income below this threshold and above tax bracket 1 is taxed at tax rate 2.",
                "section_1": "Personal Income",
                "section_2": "Regular: Non-AMT, Non-Pass-Through",
                "irs_ref": "Form 1040, line 11, instruction (Schedule XYZ).",
                "notes": "",
                "start_year": 2013,
                "cpi_inflatable": true,
                "cpi_inflated": true,
                "number_dims": 0,
                "type": "float",
                "value":  [
                    {"year": 2024, "marital_status": "single", "value": 44097.61},
                    {"year": 2024, "marital_status": "joint", "value": 88195.23},
                    {"year": 2024, "marital_status": "separate", "value": 44097.61},
                    {"year": 2024, "marital_status": "headhousehold", "value": 59024.71},
                    {"year": 2024, "marital_status": "widow", "value": 88195.23},
                    {"year": 2025, "marital_status": "single", "value": 45045.71},
                    {"year": 2025, "marital_status": "joint", "value": 90091.43},
                    {"year": 2025, "marital_status": "separate", "value": 45045.71},
                    {"year": 2025, "marital_status": "headhousehold", "value": 60293.74},
                    {"year": 2025, "marital_status": "widow", "value": 90091.43},
                    {"year": 2026, "marital_status": "single", "value": 45957.0},
                    {"year": 2026, "marital_status": "joint", "value": 91915.0},
                    {"year": 2026, "marital_status": "separate", "value": 45957.0},
                    {"year": 2026, "marital_status": "headhousehold", "value": 61519.0},
                    {"year": 2026, "marital_status": "widow", "value": 91915.0}],
                "out_of_range_minmsg": "",
                "out_of_range_maxmsg": "",
                "out_of_range_action": "stop",
                "validators": {
                    "range": {
                        "min": "ii_bracket_1",
                        "max": 9e+99
                    }
                }
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
            "standard_deduction": [
                {"year": 2026, "marital_status": "single", "value": 10000.0}
            ],
            "social_security_tax_rate": [
                {"year": 2026, "value": 0.14}
            ]
       }

JSON Object and Property Definitions
------------------------------------

Objects
~~~~~~~

Label object
^^^^^^^^^^^^^^^^

-  Used for defining the labels of the parameter space.

   -  "type": Define the datatype of the label values. See the `Type
      property <#type-property>`__.
   -  "validators": A mapping of `Validator
      objects <#validator-object>`__

   .. code:: json

       {
            "marital_status": {
                "type": "str",
                "validators": {"choice": {"choices": ["single", "joint", "separate",
                                                    "headhousehold", "widow"]}}
            }
       }

Optional object
^^^^^^^^^^^^^^^

-  Used for defining optional parameters on the schema. Upstream
   projects may find it value to attach additional information to each
   parameter that is not essential for ParamTools to perform validation.

   -  Arguments:

      -  "type": See `Type property <#type-property>`__.
      -  "number\_labels": See `Number-Labels
         Property <#number-labels-property>`__.

   -  Example:

      .. code:: json

          {
              "start_year": {"type": "int", "number_dims": 0}
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
      -  "number\_labels": Number of labels of the parameter. See
         `Number-Labels property <#number-labels-property>`__
      -  "value": A list of `Value objects <#value-object>`__.
      -  "validators": A mapping of `Validator
         objects <#validator-object>`__.
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
            "standard_deduction": {
                "title": "Standard deduction amount",
                "description": "Amount filing unit can use as a standard deduction.",
                "section_1": "Standard Deduction",
                "section_2": "Standard Deduction Amount",
                "irs_ref": "Form 1040, line 8, instructions. ",
                "notes": "",
                "start_year": 2013,
                "cpi_inflatable": true,
                "cpi_inflated": true,
                "type": "float",
                "number_dims": 0,
                "value": [
                    {"year": 2024, "marital_status": "single", "value": 13673.68},
                    {"year": 2024, "marital_status": "joint", "value": 27347.36},
                    {"year": 2024, "marital_status": "separate", "value": 13673.68},
                    {"year": 2024, "marital_status": "headhousehold", "value": 20510.52},
                    {"year": 2024, "marital_status": "widow", "value": 27347.36},
                    {"year": 2025, "marital_status": "single", "value": 13967.66},
                    {"year": 2025, "marital_status": "joint", "value": 27935.33},
                    {"year": 2025, "marital_status": "separate", "value": 13967.66},
                    {"year": 2025, "marital_status": "headhousehold", "value": 20951.49},
                    {"year": 2025, "marital_status": "widow", "value": 27935.33},
                    {"year": 2026, "marital_status": "single", "value": 7690.0},
                    {"year": 2026, "marital_status": "joint", "value": 15380.0},
                    {"year": 2026, "marital_status": "separate", "value": 7690.0},
                    {"year": 2026, "marital_status": "headhousehold", "value": 11323.0},
                    {"year": 2026, "marital_status": "widow", "value": 15380.0}],
                "out_of_range_minmsg": "",
                "out_of_range_maxmsg": "",
                "out_of_range_action": "stop",
                "compatible_data": {
                    "puf": true,
                    "cps": true
                },
                "validators": {
                    "range": {
                        "min": 0,
                        "max": 9e+99
                    }
                }
            }
        }

Validator object
^^^^^^^^^^^^^^^^

-  Used for validating user input.
-  Available validators:

   -  "range": Define a minimum and maximum value for a parameter.

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

   -  "date_range": Define a minimum and maximum value for a date type parameter.

      -  Arguments:

         -  "min": Minimum allowed value.
         -  "max": Maximum allowed value.

      -  Example:

         .. code:: json

             {
                 "range": {"min": "2019-01-01", "max": "2019-06-01"}
             }


Value object
^^^^^^^^^^^^

-  Used to describe the value of a parameter for one or more points in
   the parameter space.

   -  "value": The value of the parameter at this point in space.
   -  Zero or more label properties that define which parts of the
      parameter space this value should be applied to. These label
      properties are defined by `Label
      objects <#label-object>`__ in the `Specification
      Schema <#specification-schema>`__.

   -  Example:

      .. code:: json

        {
            "year": 2026,
            "marital_status": "single",
            "value": 7690.0
        }


Properties
~~~~~~~~~~

Type property
^^^^^^^^^^^^^

-  "type": The parameter"s data type. Supported types are:

   -  "int": Integer.
   -  "float": Floating point.
   -  "bool": Boolean. Either True or False.
   -  "str": String.
   -  "date": Date. Needs to be of the format "YYYY-MM-DD".
   -  Example:

      .. code:: json

          {
              "type": "int"
          }


Number-Labels property
^^^^^^^^^^^^^^^^^^^^^^^^^^

-  "number\_labels": The number of labels for the specified value. A
   scalar (e.g. 10) has zero labels, a list (e.g. [1, 2]) has one
   label, a nested list (e.g. [[1, 2], [3, 4]]) has two labels,
   etc.

   -  Example: Note that "value" is a scalar.

      .. code:: json

          {
              "number_dims": 0,
              "value": [{"year": 2026, "marital_status": "single", "value": 7690.0}]
          }

      Note that "value" is an one-labelal list.

      .. code:: json

          {
              "number_dims": 1,
              "value": [{"position": "shortstop", "value": ["Derek Jeter", "Andrelton Simmons"]}]
          }
