import os
import json
import itertools
from collections import OrderedDict, defaultdict
from functools import reduce

try:
    import numpy as np
except ModuleNotFoundError:
    np = None

from marshmallow import ValidationError as MarshmallowValidationError

from paramtools.build_schema import SchemaBuilder
from paramtools import utils
from paramtools.exceptions import (
    ParameterUpdateException,
    SparseValueObjectsException,
    ValidationError,
)


class Parameters:
    schema = None
    defaults = None
    field_map = {}

    def __init__(self):
        sb = SchemaBuilder(self.schema, self.defaults, self.field_map)
        defaults, self._validator_schema = sb.build_schemas()
        for k, v in defaults.items():
            setattr(self, k, v)
        self._validator_schema.context["spec"] = self
        self._errors = {}

    def adjust(self, params_or_path, raise_errors=True):
        """
        Method to deserialize and validate parameter adjustments.
        `params_or_path` can be a file path or a `dict` that has not been
        fully deserialized. The adjusted values replace the current values
        stored in the correspondig parameter attributes.

        Raises:
            marshmallow.exceptions.ValidationError if data is not valid.
            ParameterUpdateException if dimension values do not match at
                least one existing value item's corresponding dimension values.
        """
        if isinstance(params_or_path, str) and os.path.exists(params_or_path):
            params = utils.read_json(params_or_path)
        elif isinstance(params_or_path, str):
            params = json.loads(params_or_path)
        elif isinstance(params_or_path, dict):
            params = params_or_path
        else:
            raise ValueError("params_or_path is not dict or file path")

        # do type validation
        try:
            clean_params = self._validator_schema.load(params)
        except MarshmallowValidationError as ve:
            self._parse_errors(ve, params)

        if not self._errors:
            for param, value in clean_params.items():
                self._update_param(param, value)

        self._validator_schema.context["spec"] = self

        if raise_errors and self._errors:
            raise self.validation_error

    @property
    def errors(self):
        new_errors = {}
        if self._errors:
            for param, messages in self._errors["messages"].items():
                new_errors[param] = utils.ravel(messages)
        return new_errors

    @property
    def validation_error(self):
        return ValidationError(self._errors["messages"], self._errors["dims"])

    def get(self, param, **kwargs):
        """
        Query a parameter's values along dimensions specified in `kwargs`.

        Returns: [{"value": val, "dim0": ..., }]

        Raises:
            KeyError if queried dimension is not used by this parameter.
            AttributeError if parameter does not exist.
        """
        return self._get(param, True, **kwargs)

    def specification(self, meta_data=False, **kwargs):
        """
        Query value(s) of all parameters along dimensions specified in
        `kwargs`. If `meta_data` is `True`, then parameter attributes
        are included, too.

        Returns: serialized data of shape
            {"param_name": [{"value": val, "dim0": ..., }], ...}
        """
        all_params = OrderedDict()
        for param in self._validator_schema.fields:
            result = self._get(param, False, **kwargs)
            if result:
                if meta_data:
                    param_data = getattr(self, param)
                    result = dict(param_data, **{"value": result})
                all_params[param] = result
        return all_params

    def to_array(self, param):
        """
        Convert a Value object to an n-dimensional array. The Value object
        must span the parameter space specified by the Order object.

        Returns: n-dimensional NumPy array.

        Raises:
            NotImplementedError: NumPy must be installed. A pure Python
                version has not yet been implemented.
            SparseValueObjectsException: Value object does not span the
                entire space specified by the Order object.
        """
        if np is None:
            # In the future, an alternative method will be implemented in
            # pure Python.
            raise NotImplementedError(
                "Numpy must be installed to use `to_array`."
            )
        param_meta = getattr(self, param)
        dim_order = param_meta["order"]["dim_order"]
        value_order = param_meta["order"]["value_order"]
        shape = []
        for dim in dim_order:
            shape.append(len(value_order[dim]))
        shape = tuple(shape)
        arr = np.zeros(shape)
        value_items = param_meta["value"]
        # Compare len value items with the expected length if they are full.
        # In the futute, sparse objects should be supported by filling in the
        # unspecified dimensions.
        exp_full_shape = reduce(lambda x, y: x * y, shape)
        if len(value_items) != exp_full_shape:
            raise SparseValueObjectsException(
                f"The Value objects for {param} do not span the specified "
                f"parameter space."
            )
        list_2_tuple = lambda x: tuple(x) if isinstance(x, list) else x
        for vi in value_items:
            # ix stores the indices of `arr` that need to be filled in.
            ix = [[] for i in range(len(dim_order))]
            for dim_pos, dim_name in enumerate(dim_order):
                # assume value_items is dense in the sense that it spans
                # the dimension space.
                ix[dim_pos].append(value_order[dim_name].index(vi[dim_name]))
            ix = tuple(map(list_2_tuple, ix))
            arr[ix] = vi["value"]
        return arr

    def from_array(self, param, array):
        """
        Convert NumPy array to a Value object.

        Returns: Value object (shape: [{"value": val, dims:...}])
        """
        param_meta = getattr(self, param)
        dim_order = param_meta["order"]["dim_order"]
        value_order = param_meta["order"]["value_order"]
        dim_values = itertools.product(*value_order.values())
        dim_indices = itertools.product(
            *map(lambda x: range(len(x)), value_order.values())
        )
        value_items = []
        for dv, di in zip(dim_values, dim_indices):
            vi = {dim_order[j]: dv[j] for j in range(len(dv))}
            vi["value"] = array[di]
            value_items.append(vi)
        return value_items

    def _get(self, param, exact_match, **kwargs):
        """
        Private method for querying a parameter along some dimensions. If
        exact_match is True, all values in `kwargs` must be equal to the
        corresponding dimension in the parameter's "value" dictionary.

        Returns: [{"value": val, "dim0": ..., }]
        """
        value = getattr(self, param)["value"]
        ret = []
        for v in value:
            match = all(
                v[k] == kwargs[k] for k in kwargs if (k in v or exact_match)
            )
            if match:
                ret.append(v)
        return ret

    def _update_param(self, param, new_values):
        """
        Private method for updating the current parameter values with those
        specified by the adjustment. The values that need to be updated are
        chosen by finding all value items with dimension values matching
        the dimension values specified in the adjustment.

        Raises:
            ParameterUpdateException if dimension values do not match at
                least one existing value item's corresponding dimension values.
        """
        curr_vals = getattr(self, param)["value"]
        for i in range(len(new_values)):
            matched_at_least_once = False
            dims_to_check = tuple(k for k in new_values[i] if k != "value")
            for j in range(len(curr_vals)):
                match = all(
                    curr_vals[j][k] == new_values[i][k] for k in dims_to_check
                )
                if match:
                    matched_at_least_once = True
                    curr_vals[j]["value"] = new_values[i]["value"]
            if not matched_at_least_once:
                d = {k: new_values[i][k] for k in dims_to_check}
                raise ParameterUpdateException(
                    f"Failed to match along any of the "
                    f"following dimensions: {d}"
                )

    def _parse_errors(self, ve, params):
        """
        Parse the error messages given by marshmallow.

        Marshamllow error structure:

        {
            "list_param": {
                0: {
                    "value": {
                        0: [err message for first item in value list]
                        i: [err message for i-th item in value list]
                    }
                },
                i-th value object: {
                    "value": {
                        0: [...],
                        ...
                    }
                },
            }
            "nonlist_param": {
                0: {
                    "value": [err message]
                },
                ...
            }
        }

        self._errors structure:
        {
            "messages": {
                "param": [
                    ["value": {0: [msg0, msg1, ...], other_bad_ix: ...},
                     "dim0": {0: msg, ...} // if errors on dimension values.
                ],
                ...
            },
            "dim": {
                "param": [
                    {dim_name: dim_value, other_dim_name: other_dim_value},
                    ...
                    // list indices correspond to the error messages' indices
                    // of the error messages caused by the value of this value
                    // object.
                ]
            }
        }

        """
        error_info = {"messages": defaultdict(dict), "dims": defaultdict(dict)}

        def to_list(value, messages, formatted_errors):
            for message in messages:
                is_type_error = message.startswith(
                    "Invalid"
                ) or message.startswith("Not a valid")
                if is_type_error:
                    formatted_errors_ix.append(f"{message[:-1]}: {value}.")
                else:
                    formatted_errors_ix.append(message)

        for pname, data in ve.messages.items():
            error_dims = []
            formatted_errors = []
            for ix, marshmessages in data.items():
                error_dims.append(
                    {
                        k: v
                        for k, v in params[pname][ix].items()
                        if k != "value"
                    }
                )
                formatted_errors_ix = []
                for attribute, messages in marshmessages.items():
                    value = params[pname][ix][attribute]
                    if isinstance(messages, list):
                        to_list(value, messages, formatted_errors)
                    else:
                        for val_ix, messagelist in messages.items():
                            to_list(
                                value[val_ix], messagelist, formatted_errors_ix
                            )
                formatted_errors.append(formatted_errors_ix)
            error_info["messages"][pname] = formatted_errors
            error_info["dims"][pname] = error_dims

        self._errors.update(dict(error_info))
