# Parameters

Define your default parameters as a JSON file and let ParamTools handle the rest. The ParamTools JSON file is split into two components: a component that defines the structure of your default inputs and a component that defines the variables that are used in your model. The first is a top level member named `schema`. The latter are top-level members named as your model refers to them.



```json
{
    "schema": {
        "selectors": {
            "year": {
                "type": "int",
                "validators": {"range": {"min": 2013, "max": 2027}}
            },
            "marital_status": {
                "type": "str",
                "validators": {"choice": {"choices": ["single", "joint", "separate",
                                                     "headhousehold", "widow"]}}
            },
        },
        "additional_members": {
            "cpi_inflatable": {"type": "bool"},
            "cpi_inflated": {"type": "bool"}
        }
    },
    "personal_exemption": {
        "title": "Personal Exemption",
        "description": "A simple version of the personal exemption.",
        "notes": "",
        "cpi_inflatable": true,
        "cpi_inflated": true,
        "type": "float",
        "value": 0,
        "validators": {
            "range": {
                "min": 0,
            }
        }
    },
    "standard_deduction": {
        "title": "Standard deduction amount",
        "description": "Amount filing unit can use as a standard deduction.",
        "cpi_inflatable": true,
        "cpi_inflated": true,
        "type": "float",
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
            {"year": 2025, "marital_status": "widow", "value": 27935.33}],
        "validators": {
            "range": {
                "min": 0,
                "max": 9e+99
            }
        }
    },
}
```





## Input Structure

```json
{
    "schema": {
        "selectors": "mapping of selector objects"
    },
    "additional_members": "mapping of additional member objects"
}
```

- Selector Objects are used to define the ways in which a parameter's values are defined, accessed, and updated.
- Additional Members are top level members that are used by your model and not required by ParamTools.



## Default Parameters

```json
{
	"standard_deduction": {
        "title": "Standard deduction amount",
        "description": "Amount filing unit can use as a standard deduction.",
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
            {"year": 2025, "marital_status": "widow", "value": 27935.33}],
        "validators": {
            "range": {
                "min": 0,
                "max": 9e+99
            }
        }
    }
}
```

###  Members:

- `title`: A human readable name for the parameter.

- `description`: Describe the parameter.
- `notes`: (*optional*) Additional advice or information.
- `type`: Data type of the parameter. Allowed types are `int`, `float`, `bool`, `str` and `date` (YYYY-MM-DD).
- `number_dims`: (*optional, default is 0*) Number of dimensions for the value, as defined by [`np.ndim`][1]

- `value`: Value of the parameter and optionally, the corresponding selectors. It can be written in two ways:

  - if selectors are used:

        ```json
        {
            "value": [{"value": "my value", **selectors}]
        }
        ```



  - if selectors are not used:

        ```json
        {
            "value": "my value"
        }
        ```

- `validators`: Key-value pairs of the validator objects:

        ```json
        {
            "validators": {
                "range": {"min": "min value", "max": "max value"},
                "choice": {"choices": ["list", "of", "allowed", "values"]},
                "date_range": {"min": "2018-01-01", "max": "2018-06-01"}
            }
        }
        ```

    *Note that the ranges are inclusive.*



[1]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html
