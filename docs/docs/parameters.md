# Parameters

Define your default parameters and let ParamTools handle the rest.

The ParamTools JSON file is split into two components: a component that defines the structure of your default inputs and a component that defines the variables that are used in your model. The first component is a top level member named `schema`. The second component consists of key-value pairs where the key is the parameter's name and the value is its data.

```json
{
    "schema": {
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
        },
        "additional_members": {
            "cpi_inflatable": {"type": "bool"},
            "cpi_inflated": {"type": "bool"}
        },
        "actions": {
            "array_first": true,
            "label_to_extend": "year",
            "uses_extend_func": true
        }
    },
    "personal_exemption": {
        "title": "Personal Exemption",
        "description": "A simple version of the personal exemption.",
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





## Parameters Schema

```json
{
    "schema": {
        "labels": {
            "year": {
                "type": "int",
                "validators": {"range": {"min": 2013, "max": 2027}}
            }
        },
        "additional_members": {
            "cpi_inflatable": {"type": "bool"},
            "cpi_inflated": {"type": "bool"}
        }
    },
    "actions": {
        "array_first": true,
        "label_to_extend": true,
        "uses_extend_func": true
    }
}
```

- `labels`: Labels are used for defining, accessing, and updating a parameter's values.

- `additional_members`: Additional Members are parameter level members that are specific to your model. For example, "title" is a parameter level member that is required by ParamTools, but "cpi_inflated" is not. Therefore, "cpi_inflated" needs to be defined in `additional_members`.

- `actions`: Actions affect how the data is read into and handled by the `Parameters` class:

    - `array_first`: If value is `true`, parameters' values will be accessed as arrays by default.

    - `label_to_extend`: The name of the label along which the missing values of the parameters will be extended. For more information, check out the [extend docs](/api/extend/).

    - `uses_extend_func`: If value is `true`, special logic is applied to the values of the parameters as they are extended. For more information, check out the [indexing docs](/api/indexing/).


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

- `number_dims`: (*optional, default is 0*) Number of dimensions for the value, as defined by [`np.ndim`][1].

- `value`: Value of the parameter and optionally, the corresponding labels. It can be written in two ways:

    - if labels are used: `{"value": [{"value": "my value", **labels}]}`

    - if labels are not used: `{"value": "my value"}`

- `validators`: Key-value pairs of the validator objects (*the ranges are inclusive*):

```json
{
    "validators": {
        "range": {"min": "min value", "max": "max value"},
        "choice": {"choices": ["list", "of", "allowed", "values"]},
        "date_range": {"min": "2018-01-01", "max": "2018-06-01"}
    }
}
```



[1]: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html
