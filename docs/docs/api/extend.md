# Extend

The values of a parameter can be extended along a specified label. This is helpful when a parameter's values are the same for different values of a label and there is some inherent order in that label. The extend feature allows you to simply write down the minimum amount of information needed to fill in a parameter's values and ParamTools will fill in the gaps.

To use the extend feature, set the `label_to_extend` class attribute to the label that should be extended.

## Example

The standard deduction parameter's values only need to be specified when there is a change in the tax law. For the other years, it does not change (unless its indexed to inflation). It would be annoying to have to manually write out each of its values. Instead, we can more concisely write its values in 2017, its new values in 2018 after the TCJA tax reform was passed, and its values after provisions of the TCJA are phased out in 2026.

```python
import paramtools


class TaxParams(paramtools.Parameters):
    defaults = {
        "schema": {
            "labels": {
                "year": {
                    "type": "int",
                    "validators": {"range": {"min": 2013, "max": 2027}}
                },
                "marital_status": {
                    "type": "str",
                    "validators": {"choice": {"choices": ["single", "joint"]}}
                },
            }
        },
        "standard_deduction": {
            "title": "Standard deduction amount",
            "description": "Amount filing unit can use as a standard deduction.",
            "type": "float",
            "value": [
                {"year": 2017, "marital_status": "single", "value": 6350},
                {"year": 2017, "marital_status": "joint", "value": 12700},
                {"year": 2018, "marital_status": "single", "value": 12000},
                {"year": 2018, "marital_status": "joint", "value": 24000},
                {"year": 2026, "marital_status": "single", "value": 7685},
                {"year": 2026, "marital_status": "joint", "value": 15369}],
            "validators": {
                "range": {
                    "min": 0,
                    "max": 9e+99
                }
            }
        },
    }

    label_to_extend = "year"
    array_first = True

params = TaxParams()
params.standard_deduction

# output:
# array([[ 6350., 12700.],
#        [ 6350., 12700.],
#        [ 6350., 12700.],
#        [ 6350., 12700.],
#        [ 6350., 12700.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [12000., 24000.],
#        [ 7685., 15369.],
#        [ 7685., 15369.]])
```


## Extend behavior by validator

ParamTools uses the validator associated with `label_to_extend` to determine how values should be extended by assuming that there is some order among the range of possible values for the label.

Note: You can view the grid of values for any label by inspecting the `label_grid` attribute of a `paramtools.Parameters` derived instance.

### Range

**Type:** `int`

```json
{
    "range": {"min": 0, "max": 5}
}
```

*Extend values:*

```python
[0, 1, 2, 3, 4, 5]
```

**Type:** `float`

```json
{
    "range": {"min": 0, "max": 2, "step": 0.5}
}
```

*Extend values:*

```python
[0, 0.5, 1.0, 1.5, 2.0]
```

**Type:** `date`

```json
{
    "range": {"min": "2019-01-01", "max": "2019-01-05", "step": {"days": 2}}
}
```

*Extend values:*

```python
[datetime.date(2019, 1, 1),
 datetime.date(2019, 1, 3),
 datetime.date(2019, 1, 5)]
```

### Choice

**Type:** `int`

```json
{
    "choice": {"choices": [-1, -2, -3]}
}
```

*Extend values:*

```python
[-1, -2, -3]
```

**Type:** `str`

```json
{
    "choice": {"choices": ["january", "february", "march"]}
}
```

*Extend values:*

```python
["january", "february", "march"]
```