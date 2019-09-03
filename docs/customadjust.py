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
                    "validators": {"range": {"min": 2000, "max": 2005}},
                }
            }
        },
        "a": {
            "title": "A",
            "description": "a param",
            "type": "int",
            "value": [{"year": 2000, "value": 1}, {"year": 2001, "value": 2}],
        },
        "b": {
            "title": "B",
            "description": "b param",
            "type": "int",
            "value": [{"year": 2000, "value": 3}, {"year": 2001, "value": 4}],
        },
    }

    def adjust(self, params_or_path, **kwargs):
        """
        A custom adjust method that converts CSV files to
        ParamTools compliant Python dictionaries.
        """
        if os.path.exists(params_or_path):
            paramsdf = pd.read_csv(params_or_path, index_col="year")
        else:
            paramsdf = pd.read_csv(
                io.StringIO(params_or_path), index_col="year"
            )

        dfdict = paramsdf.to_dict()
        params = {"a": [], "b": []}
        for label in params:
            for year, value in dfdict[label].items():
                params[label] += [{"year": year, "value": value}]
        breakpoint()
        # call adjust method on paramtools.Parameters which will
        # call _adjust to actually do the update.
        return super().adjust(params, **kwargs)


csv_string = """
year,a,b
2000,5,6\n
2001,6,7\n
"""

params = CSVParams()
print(params.adjust(csv_string))

print(params.a)
print(params.b)
