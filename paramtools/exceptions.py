import json

from paramtools import utils


class ParamToolsError(Exception):
    pass


class ParameterUpdateException(ParamToolsError):
    pass


class SparseValueObjectsException(ParamToolsError):
    pass


class ValidationError(ParamToolsError):
    def __init__(self, messages, labels):
        self.messages = messages
        self.labels = labels
        raveled_messages = {
            param: utils.ravel(msgs) for param, msgs in self.messages.items()
        }
        super().__init__(json.dumps(raveled_messages, indent=4))


class InconsistentLabelsException(ParamToolsError):
    pass


collision_list = [
    "_data",
    "_errors",
    "select_eq",
    "select_ne",
    "select_gt",
    "_adjust",
    "_numpy_type",
    "_parse_errors",
    "_resolve_order",
    "_set_state",
    "_state",
    "_stateless_label_grid",
    "_update_param",
    "_validator_schema",
    "_defaults_schema",
    "adjust",
    "array_first",
    "clear_state",
    "defaults",
    "label_grid",
    "label_validators",
    "errors",
    "field_map",
    "from_array",
    "read_params",
    "set_state",
    "specification",
    "to_array",
    "validation_error",
    "view_state",
    "extend",
    "extend_func",
    "uses_extend_func",
    "label_to_extend",
    "get_index_rate",
    "index_rates",
]


class ParameterNameCollisionException(ParamToolsError):
    pass
