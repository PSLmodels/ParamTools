import os
import json

from marshmallow import ValidationError

from paramtools.build_schema import SchemaBuilder
from paramtools import utils


class ParameterGetException(Exception):
    pass


class ParameterUpdateException(Exception):
    pass


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
        self.errors = {}

    def adjust(self, params_or_path, raise_errors=True, compress_errors=True):
        """
        Method to deserialize and validate parameter adjustments.
        `params_or_path` can be a file path or a `dict` that has not been
        fully deserialized.

        Returns: serialized data.

        Throws: `marshmallow.exceptions.ValidationError` if data is not valid.
        """
        if isinstance(params_or_path, str) and os.path.exists(params_or_path):
            params = utils.read_json(params_or_path)
        elif isinstance(params_or_path, str):
            params = json.loads(params_or_path)
        elif isinstance(params_or_path, dict):
            params = params_or_path
        else:
            raise ValueError("params_or_path is not dict or file path")

        self.errors = {}
        # do type validation
        try:
            clean_params = self._validator_schema.load(params)
        except ValidationError as ve:
            self.format_errors(ve, compress_errors)

        # if no errors from type validation, do choice, range, etc. validation.
        if not self.errors:
            for param, value in clean_params.items():
                try:
                    self._update_param(param, value)
                except ValidationError as ve:
                    self.format_errors(ve, compress_errors)

        self._validator_schema.context["spec"] = self

        if raise_errors and self.errors:
            raise ValidationError(self.errors)

    def get(self, param, **kwargs):
        value = getattr(self, param)["value"]
        ret = []
        try:
            for v in value:
                if all(v[k] == kwargs[k] for k in kwargs):
                    ret.append(v)
        except KeyError:
            raise ParameterGetException(
                f"One of the provided keys {kwargs.keys()} is "
                f"not allowed for parameter {param}"
            )
        return ret

    def specification(self, **kwargs):
        all_params = {}
        for param in self._validator_schema.fields:
            try:
                result = self.get(param, **kwargs)
                if result:
                    all_params[param] = result
            except ParameterGetException:
                pass
        return all_params

    def format_errors(self, validation_error, compress_errors=True):
        if compress_errors:
            for param, messages in validation_error.messages.items():
                if param in self.errors:
                    self.errors[param].append(utils.get_leaves(messages))
                else:
                    self.errors[param] = utils.get_leaves(messages)
            validation_error.messages = self.errors
        else:
            self.errors.update(validation_error.messages)

    def _update_param(self, param, new_values):
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
