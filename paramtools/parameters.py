from paramtools.build_schema import SchemaBuilder
from paramtools import utils


class ParameterGetException(Exception):
    pass


class ParameterUpdateException(Exception):
    pass


class Parameters:

    project_schema = None
    baseline_parameters = None
    field_map = {}

    def __init__(self):
        sb = SchemaBuilder(
            self.project_schema, self.baseline_parameters, self.field_map
        )
        base_spec, self._validator_schema = sb.build_schemas()
        for k, v in base_spec.items():
            setattr(self, k, v)
        self._validator_schema.context["base_spec"] = self

    def revise(self, params_or_path):
        """
        Method to deserialize and validate parameter revision.
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
        clean_params = self._validator_schema.load(params)
        for param, value in clean_params.items():
            self._update_param(param, value)
        self._validator_schema.context["base_spec"] = self

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
