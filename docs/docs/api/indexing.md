# Extend with Indexing

ParamTools provides out-of-the-box parameter indexing. This is helpful for projects that have parameters that change at some rate over time. For example, tax parameters like the standard deduction are often indexed to price inflation. So, the value of the standard deduction actually increases every year by 1 or 2% depending on that year's inflation rate.

The [extend documentation](/api/extend/) may be useful for gaining a better understanding of how ParamTools extends parameter values along `label_to_extend`.

To use the indexing feature:

 - Set the `label_to_extend` class attribute to the label that should be extended
 - Set the `indexing_rates` class attribute to a dictionary of inflation rates where the keys correspond to the value of `label_to_extend` and the values are the indexing rates.
 - Set the `uses_extend_func` class attribute to `True`.
 - In `defaults` or `defaults.json`, set `indexed` to `True` for each parameter that needs to be indexed.

## Example

This is a continuation of the tax parameters example from the [extend documentation](/api/extend/). The differences are `indexed` is set to `True` for the `standard_deducation` parameter, `uses_extend_func` is set to `True`, and `index_rates` is specified with inflation rates obtained from the open-source tax modeling package, [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator/), using version 2.5.0.

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

            # Set indexed to True to extend standard_deduction with the built-in
            # extension logic.
            "indexed": True,

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
    array_first = True
    label_to_extend = "year"
    # Activate use of extend_func method.
    uses_extend_func = True
    # inflation rates from Tax-Calculator v2.5.0
    index_rates = {
        2013: 0.0148,
        2014: 0.0159,
        2015: 0.0012,
        2016: 0.0127,
        2017: 0.0187,
        2018: 0.0224,
        2019: 0.0186,
        2020: 0.0233,
        2021: 0.0229,
        2022: 0.0228,
        2023: 0.0221,
        2024: 0.0211,
        2025: 0.0209,
        2026: 0.0211,
        2027: 0.0208,
        2028: 0.021,
        2029: 0.021
    }


params = TaxParams()
params.standard_deduction

# output:
# array([[ 6074.92, 12149.84],
#        [ 6164.83, 12329.66],
#        [ 6262.85, 12525.7 ],
#        [ 6270.37, 12540.73],
#        [ 6350.  , 12700.  ],
#        [12000.  , 24000.  ],
#        [12268.8 , 24537.6 ],
#        [12497.  , 24994.  ],
#        [12788.18, 25576.36],
#        [13081.03, 26162.06],
#        [13379.28, 26758.55],
#        [13674.96, 27349.91],
#        [13963.5 , 27926.99],
#        [ 7685.  , 15369.  ],
#        [ 7847.15, 15693.29]])
```

Adjustments are also indexed. In the example below, `standard_deduction` is set to 10,000 in 2017, increased to 15,000 for single tax units in 2020, and increased to 20,000 for joint tax units in 2021:

```python
params.adjust(
    {
        "standard_deduction": [
            {"year": 2017, "value": 10000},
            {"year": 2020, "marital_status": "single", "value": 15000},
            {"year": 2021, "marital_status": "joint", "value": 20000}
        ]
    }
)

params.standard_deduction

# output:
# array([[ 6074.92, 12149.84],
#        [ 6164.83, 12329.66],
#        [ 6262.85, 12525.7 ],
#        [ 6270.37, 12540.73],
#        [10000.  , 10000.  ],
#        [10187.  , 10187.  ],
#        [10415.19, 10415.19],
#        [15000.  , 10608.91],
#        [15349.5 , 20000.  ],
#        [15701.  , 20458.  ],
#        [16058.98, 20924.44],
#        [16413.88, 21386.87],
#        [16760.21, 21838.13],
#        [17110.5 , 22294.55],
#        [17471.53, 22764.97]])

```


### Code for getting Tax-Calculator index rates

```python
import taxcalc
pol = taxcalc.Policy()
index_rates = {
    year: value
    for year, value in zip(list(range(2013, 2029 + 1)), pol.inflation_rates())
}

```

Note that there are some subtle details that are implemented in Tax-Calculator's indexing logic that are not implemented in this example. Tax-Calculator has a parameter called `CPI_offset` that adjusts inflation rates up or down by a fixed amount. The `indexed` property can also be turned on and off for each parameter. Implementing these nuanced features is left as the proverbial "trivial exercise to the reader."
