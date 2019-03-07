from collections import defaultdict

import numpy as np
from marshmallow import Schema, fields

import paramtools

import taxcalc


class IndexedParameters(paramtools.Parameters):
    def __init__(self):
        super().__init__()
        self.extend()
        self.array_first = True
        self.set_state()

    def extend(self, params_to_extend=None):
        min_allowed_year = min(self._stateless_dim_mesh["year"])
        max_allowed_year = max(self._stateless_dim_mesh["year"])
        adjustment = defaultdict(list)
        spec = self.specification(use_state=False, meta_data=True)
        if params_to_extend is None:
            param_data = spec
        else:
            param_data = {param: spec[param] for param in params_to_extend}

        def get_vo_lookup(vos, dims):
            qh = {}
            for vo in vos:
                qh[tuple(vo[d] for d in dims)] = vo["value"]
            return qh

        for param, data in param_data.items():
            max_year = max(map(lambda x: x["year"], data["value"]))
            if max_year == max_allowed_year:
                continue
            max_year = data["value"][-1]["year"]
            if max_year == max_allowed_year:
                continue
            value_objects = self._get(param, True, year=max_year)
            if data["cpi_inflated"]:
                # preserve order!
                dims_to_match = sorted(
                    [
                        dim_name
                        for dim_name in value_objects[0]
                        if dim_name not in ("year", "value")
                    ]
                )
                vo_lookup = get_vo_lookup(value_objects, dims_to_match)
                rates = self.indexing_rates(param)
                for ix, year in enumerate(
                    range(max_year + 1, max_allowed_year + 1)
                ):
                    for vo in value_objects:
                        dim_values = tuple(
                            vo[dim_name] for dim_name in dims_to_match
                        )
                        v = vo_lookup[dim_values] * (
                            1 + rates[max_year - min_allowed_year + ix]
                        )
                        v = np.round(v, 2) if v < 9e99 else 9e99
                        adjustment[param].append(
                            dict(vo, **{"year": year, "value": v})
                        )
                        vo_lookup[dim_values] = v
            else:
                for year in range(max_year, max_allowed_year + 1):
                    for vo in value_objects:
                        adjustment[param].append(dict(vo, **{"year": year}))
        self.array_first = True
        self.adjust(adjustment)

    def adjust_with_extend(self, params_or_path, raise_errors=False):
        params = self.read_params(params_or_path)
        curr_vals = self.specification()
        for param, param_adj in params.items():
            max_year = max(map(lambda x: x["year"], param_adj))
            for vo in curr_vals[param]:
                if vo["year"] > max_year:
                    params[param].append(dict(vo, **{"value": None}))
        self.array_first = False
        self.adjust(params)
        self.extend(params_to_extend=list(params.keys()))


class CompatibleDataSchema(Schema):
    """
    Schema for Compatible data object
    {
        "compatible_data": {"data1": bool, "data2": bool, ...}
    }
    """

    puf = fields.Boolean()
    cps = fields.Boolean()


class TaxParams(IndexedParameters):
    schema = "schema.json"
    defaults = "defaults.json"
    field_map = {"compatible_data": fields.Nested(CompatibleDataSchema())}

    def __init__(self, *args, **kwargs):
        growfactors = taxcalc.GrowFactors()
        self._inflation_rates = growfactors.price_inflation_rates(2013, 2028)
        self._apply_clp_cpi_offset(2028 - 2013 + 1)
        self._wage_growth_rates = growfactors.wage_growth_rates(2013, 2028)
        super().__init__(*args, **kwargs)

    def indexing_rates(self, param=None):
        if param == "_SS_Earnings_c":
            return self._wage_growth_rates
        else:
            return self._inflation_rates

    def _apply_clp_cpi_offset(self, num_years):
        """
        See taxcalc.Policy._apply_clp_cpi_offset

        If you are curious about what's going on here, the
        cpi_offset parameter is an approximation for the chained
        cpi.
        """
        cpi_offset = [0.0, 0.0, 0.0, 0.0, -0.0025]
        if len(cpi_offset) < num_years:  # extrapolate last known value
            cpi_offset = cpi_offset + cpi_offset[-1:] * (
                num_years - len(cpi_offset)
            )
        for idx in range(0, num_years):
            infrate = round(self._inflation_rates[idx] + cpi_offset[idx], 6)
            self._inflation_rates[idx] = infrate
