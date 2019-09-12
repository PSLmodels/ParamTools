# Custom Adjustments

The ParamTools adjustment format and logic can be augmented significantly. This is helpful for projects that need to support a pre-existing data format or require custom adjustment logic. Projects should customize their adjustments by writing their own `adjust` method and then calling the default `adjust` method from there:


```python

class Params(paramtools.Parameters):
    def adjust(self, params_or_path, **kwargs):
        params = self.read_params(params_or_path)

        # ... custom logic here

        # call default adjust method.
        return super().adjust(params, **kwargs)

```


## Example

Some projects may find it convenient to use CSVs for their adjustment format. That's no problem for ParamTools as long as the CSV is converted to a JSON file or Python dictionary that meets the ParamTools criteria.

```python
import io
import os

import pandas as pd

import paramtools


class CSVParams(paramtools.Parameters):
    defaults = {
        "schema": {
            "labels": {
                "year": {
                    "type": "int",
                    "validators": {"range": {"min": 2000, "max": 2005}}
                }
            }
        },
        "a": {
            "title": "A",
            "description": "a param",
            "type": "int",
            "value": [
                {"year": 2000, "value": 1},
                {"year": 2001, "value": 2},
            ]
        },
        "b": {
            "title": "B",
            "description": "b param",
            "type": "int",
            "value": [
                {"year": 2000, "value": 3},
                {"year": 2001, "value": 4},
            ]
        }
    }

    def adjust(self, params_or_path, **kwargs):
        """
        A custom adjust method that converts CSV files to
        ParamTools compliant Python dictionaries.
        """
        if os.path.exists(params_or_path):
            paramsdf = pd.read_csv(params_or_path, index_col="year")
        else:
            paramsdf = pd.read_csv(io.StringIO(params_or_path), index_col="year")

        dfdict = paramsdf.to_dict()
        params = {"a": [], "b": []}
        for label in params:
            for year, value in dfdict[label].items():
                params[label] += [{"year": year, "value": value}]

        # call adjust method on paramtools.Parameters which will
        # call _adjust to actually do the update.
        return super().adjust(params, **kwargs)

```

Now we create an example CSV file. To keep the example self-contained, the CSV is just a string, but this example works with CSV files, too. The values of "A" are updated to 5 in 2000 and 6 in 2001, and the values of "B" are updated to 6 in 2000 and 7 in 2001.


```python

# this could also be a path to a CSV file.
csv_string = """
year,a,b
2000,5,6\n
2001,6,7\n
"""

params = CSVParams()
params.adjust(csv_string)

# output
# OrderedDict([('a', [{'year': 2000, 'value': 5}, {'year': 2001, 'value': 6}]),
#              ('b', [{'year': 2000, 'value': 6}, {'year': 2001, 'value': 7}])])

params.a

# output:
# [{'year': 2000, 'value': 5}, {'year': 2001, 'value': 6}]

params.b

# output
# [{'year': 2000, 'value': 6}, {'year': 2001, 'value': 7}]

```

Now, if we use `array_first` and [`label_to_extend`](/api/extend/), the params instance can be loaded into a Pandas
DataFrame like this:

```python
csv_string = """
year,a,b
2000,5,6\n
2001,6,7\n
"""

params = CSVParams(array_first=True, label_to_extend="year")
params.adjust(csv_string)

# OrderedDict([('a', [{'value': 5, 'year': 2000}, {'value': 6, 'year': 2001}]),
#              ('b', [{'value': 6, 'year': 2000}, {'value': 7, 'year': 2001}])])

params_df = pd.DataFrame.from_dict(params.to_dict())
params_df

# output:
#    a  b
# 0  5  6
# 1  6  7
# 2  6  7
# 3  6  7
# 4  6  7
# 5  6  7

params_df["year"] = params.label_grid["year"]
params_df.set_index("year")

# output:
#       a  b
# year
# 2000  5  6
# 2001  6  7
# 2002  6  7
# 2003  6  7
# 2004  6  7
# 2005  6  7

```
