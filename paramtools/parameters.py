import copy
import os
import json
import itertools
from collections import OrderedDict, defaultdict
from functools import reduce

import numpy as np
from marshmallow import ValidationError as MarshmallowValidationError

from paramtools.build_schema import SchemaBuilder
from paramtools import utils
from paramtools.exceptions import (
    SparseValueObjectsException,
    ValidationError,
    InconsistentLabelsException,
    collision_list,
    ParameterNameCollisionException,
)


class Parameters:
    defaults = None
    field_map = {}
    array_first = False

    def __init__(self, initial_state=None, array_first=None):
        sb = SchemaBuilder(self.defaults, self.field_map)
        defaults, self._validator_schema = sb.build_schemas()
        self.label_validators = sb.label_validators
        self._stateless_label_grid = OrderedDict(
            [(name, v.grid()) for name, v in self.label_validators.items()]
        )
        self.label_grid = copy.deepcopy(self._stateless_label_grid)
        self._data = defaults
        self._validator_schema.context["spec"] = self
        self._errors = {}
        self._state = initial_state or {}
        if array_first is not None:
            self.array_first = array_first
        self.set_state()

    def set_state(self, **labels):
        """
        Sets state for the Parameters instance. The state, label_grid, and
        parameter attributes are all updated with the new state.

        Raises:
            ValidationError if the labels kwargs contain labels that are not
                specified in schema.json or if the label values fail the
                validator set for the corresponding label in schema.json.
        """
        messages = {}
        for name, values in labels.items():
            if name not in self.label_validators:
                messages[name] = f"{name} is not a valid label."
                continue
            if not isinstance(values, list):
                values = [values]
            for value in values:
                try:
                    self.label_validators[name].deserialize(value)
                except MarshmallowValidationError as ve:
                    messages[name] = str(ve)
        if messages:
            raise ValidationError(messages, labels=None)
        self._state.update(labels)
        for label_name, label_value in self._state.items():
            if not isinstance(label_value, list):
                label_value = [label_value]
            self.label_grid[label_name] = label_value
        spec = self.specification(include_empty=True, **self._state)
        for name, value in spec.items():
            if name in collision_list:
                raise ParameterNameCollisionException(
                    f"The paramter name, '{name}', is already used by the Parameters object."
                )
            if self.array_first:
                setattr(self, name, self.to_array(name))
            else:
                setattr(self, name, value)

    def clear_state(self):
        """
        Reset the state of the Parameters instance.
        """
        self._state = {}
        self.label_grid = copy.deepcopy(self._stateless_label_grid)
        self.set_state()

    def view_state(self):
        """
        Access the label state of the ``Parameters`` instance.
        """
        return self._state

    def read_params(self, params_or_path):
        if isinstance(params_or_path, str) and os.path.exists(params_or_path):
            params = utils.read_json(params_or_path)
        elif isinstance(params_or_path, str):
            params = json.loads(params_or_path)
        elif isinstance(params_or_path, dict):
            params = params_or_path
        else:
            raise ValueError("params_or_path is not dict or file path")
        return params

    def adjust(self, params_or_path, raise_errors=True):
        """
        Deserialize and validate parameter adjustments. `params_or_path`
        can be a file path or a `dict` that has not been fully deserialized.
        The adjusted values replace the current values stored in the
        corresponding parameter attributes.

        Raises:
            marshmallow.exceptions.ValidationError if data is not valid.

            ParameterUpdateException if label values do not match at
                least one existing value item's corresponding label values.
        """
        params = self.read_params(params_or_path)

        # Validate user adjustments.
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

        # Update attrs.
        self.set_state()

    @property
    def errors(self):
        new_errors = {}
        if self._errors:
            for param, messages in self._errors["messages"].items():
                new_errors[param] = utils.ravel(messages)
        return new_errors

    @property
    def validation_error(self):
        return ValidationError(
            self._errors["messages"], self._errors["labels"]
        )

    def specification(
        self, use_state=True, meta_data=False, include_empty=False, **labels
    ):
        """
        Query value(s) of all parameters along labels specified in
        ``labels``. If ``use_state`` is ``True``, the current state is updated with
        ``labels``. If ``meta_data`` is ``True``, then parameter attributes
        are included, too. If ``include_empty`` is ``True``, then values that
        do not match the query labels set with ``self._state`` or
        ``labels`` will be included and set to an empty list.

        Returns: serialized data of shape
            {"param_name": [{"value": val, "label0": ..., }], ...}
        """
        if use_state:
            labels.update(self._state)

        all_params = OrderedDict()
        for param in self._validator_schema.fields:
            result = self._select(param, False, **labels)
            if result or include_empty:
                if meta_data:
                    param_data = self._data[param]
                    result = dict(param_data, **{"value": result})
                all_params[param] = result
        return all_params

    def to_array(self, param):
        """
        Convert a Value object to an n-labelal array. The list of Value
        objects must span the specified parameter space. The parameter space
        is defined by inspecting the label validators in schema.json
        and the state attribute of the Parameters instance.

        Returns: n-labelal NumPy array.

        Raises:
            InconsistentLabelsException: Value objects do not have consistent
                labels.
            SparseValueObjectsException: Value object does not span the
                entire space specified by the Order object.
        """
        value_items = self._select(param, False, **self._state)
        label_order, value_order = self._resolve_order(param)
        shape = []
        for label in label_order:
            shape.append(len(value_order[label]))
        shape = tuple(shape)
        arr = np.empty(shape, dtype=self._numpy_type(param))
        # Compare len value items with the expected length if they are full.
        # In the futute, sparse objects should be supported by filling in the
        # unspecified labels.
        if not shape:
            exp_full_shape = 1
        else:
            exp_full_shape = reduce(lambda x, y: x * y, shape)
        if len(value_items) != exp_full_shape:
            # maintains label value order over value objects.
            exp_grid = list(itertools.product(*value_order.values()))
            # preserve label value order for each value object by
            # iterating over label_order.
            actual = set(
                [tuple(vo[d] for d in label_order) for vo in value_items]
            )
            missing = "\n\t".join(
                [str(d) for d in exp_grid if d not in actual]
            )
            raise SparseValueObjectsException(
                f"The Value objects for {param} do not span the specified "
                f"parameter space. Missing combinations:\n\t{missing}"
            )

        def list_2_tuple(x):
            return tuple(x) if isinstance(x, list) else x

        for vi in value_items:
            # ix stores the indices of `arr` that need to be filled in.
            ix = [[] for i in range(len(label_order))]
            for label_pos, label_name in enumerate(label_order):
                # assume value_items is dense in the sense that it spans
                # the label space.
                ix[label_pos].append(
                    value_order[label_name].index(vi[label_name])
                )
            ix = tuple(map(list_2_tuple, ix))
            arr[ix] = vi["value"]
        return arr

    def from_array(self, param, array=None):
        """
        Convert NumPy array to a Value object.

        Returns:
            Value object (shape: [{"value": val, labels:...}])

        Raises:
            InconsistentLabelsException: Value objects do not have consistent
                labels.
        """
        if array is None:
            array = getattr(self, param)
            if not isinstance(array, np.ndarray):
                raise TypeError(
                    "A NumPy Ndarray should be passed to this method "
                    "or the instance attribute should be an array."
                )
        label_order, value_order = self._resolve_order(param)
        label_values = itertools.product(*value_order.values())
        label_indices = itertools.product(
            *map(lambda x: range(len(x)), value_order.values())
        )
        value_items = []
        for dv, di in zip(label_values, label_indices):
            vi = {label_order[j]: dv[j] for j in range(len(dv))}
            vi["value"] = array[di]
            value_items.append(vi)
        return value_items

    def _resolve_order(self, param):
        """
        Resolve the order of the labels and their values by
        inspecting data in the label grid values.

        The label grid for all labels is stored in the label_grid
        attribute. The labels to be used are the ones that are specified
        for each value object. Note that the labels must be specified
        _consistently_ for all value objects, i.e. none can be added or omitted
        for any value object in the list.

        Returns:
            label_order: The label order.
            value_order: The values, in order, for each label.

        Raises:
            InconsistentLabelsException: Value objects do not have consistent
                labels.
        """
        value_items = self._select(param, False, **self._state)
        used = utils.consistent_labels(value_items)
        if used is None:
            raise InconsistentLabelsException(
                f"Some labels in {value_items} were added or omitted for some value object(s)."
            )
        label_order, value_order = [], {}
        for label_name, label_values in self.label_grid.items():
            if label_name in used:
                label_order.append(label_name)
                value_order[label_name] = label_values
        return label_order, value_order

    def _numpy_type(self, param):
        """
        Get the numpy type for a given parameter.
        """
        return (
            self._validator_schema.fields[param].nested.fields["value"].np_type
        )

    def _select(self, param, exact_match, **labels):
        """
        Query a parameter along some labels. If exact_match is True,
        all values in `labels` must be equal to the corresponding label
        in the parameter's "value" dictionary.

        Ignores state.

        Returns: [{"value": val, "label0": ..., }]
        """
        value_objects = self._data[param]["value"]
        ret = []
        for value_object in value_objects:
            matches = []
            for label_name, label_value in labels.items():
                if label_name in value_object or exact_match:
                    if isinstance(label_value, list):
                        match = value_object[label_name] in label_value
                    else:
                        match = value_object[label_name] == label_value
                    matches.append(match)
            if all(matches):
                ret.append(value_object)
        return ret

    def _update_param(self, param, new_values):
        """
        Update the current parameter values with those specified by
        the adjustment. The values that need to be updated are chosen
        by finding all value items with label values matching the
        label values specified in the adjustment. If the value is
        set to None, then that value object will be removed.

        Note: _update_param used to raise a ParameterUpdateException if one of the new
            values did not match at least one of the current value objects. However,
            this was dropped to better support the case where the parameters are being
            extended along some label to fill the parameter space. An exception could
            be raised if a new value object contains a label that is not used in the
            current value objects for the parameter. However, it seems like it could be
            expensive to check this case, especially when a project is extending parameters.
            For now, no exceptions are raised by this method.

        """
        curr_vals = self._data[param]["value"]
        for i in range(len(new_values)):
            matched_at_least_once = False
            labels_to_check = tuple(k for k in new_values[i] if k != "value")
            to_delete = []
            for j in range(len(curr_vals)):
                match = all(
                    curr_vals[j][k] == new_values[i][k]
                    for k in labels_to_check
                )
                if match:
                    matched_at_least_once = True
                    if new_values[i]["value"] is None:
                        to_delete.append(j)
                    else:
                        curr_vals[j]["value"] = new_values[i]["value"]
            if to_delete:
                # Iterate in reverse so that indices point to the correct
                # value. If iterating ascending then the values will be shifted
                # towards the front of the list as items are removed.
                for ix in sorted(to_delete, reverse=True):
                    del curr_vals[ix]
            if not matched_at_least_once:
                curr_vals.append(new_values[i])

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
                     "label0": {0: msg, ...} // if errors on label values.
                ],
                ...
            },
            "label": {
                "param": [
                    {label_name: label_value, other_label_name: other_label_value},
                    ...
                    // list indices correspond to the error messages' indices
                    // of the error messages caused by the value of this value
                    // object.
                ]
            }
        }

        """
        error_info = {
            "messages": defaultdict(dict),
            "labels": defaultdict(dict),
        }

        for pname, data in ve.messages.items():
            param_data = utils.ensure_value_object(params[pname])
            error_labels = []
            formatted_errors = []
            for ix, marshmessages in data.items():
                error_labels.append(
                    {k: v for k, v in param_data[ix].items() if k != "value"}
                )
                formatted_errors_ix = []
                for _, messages in marshmessages.items():
                    if messages:
                        if isinstance(messages, list):
                            formatted_errors_ix += messages
                        else:
                            for _, messagelist in messages.items():
                                formatted_errors_ix += messagelist
                formatted_errors.append(formatted_errors_ix)
            error_info["messages"][pname] = formatted_errors
            error_info["labels"][pname] = error_labels

        self._errors.update(dict(error_info))
