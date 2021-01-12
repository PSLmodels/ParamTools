import json
from collections import defaultdict

from paramtools import utils


class ParamToolsError(Exception):
    pass


class ParameterUpdateException(ParamToolsError):
    pass


class SparseValueObjectsException(ParamToolsError):
    pass


class UnknownTypeException(ParamToolsError):
    pass


class ValidationError(ParamToolsError):
    def __init__(self, messages, labels):
        self.messages = messages
        self.labels = labels
        error_msg = defaultdict(dict)
        for error_type, msgs in self.messages.items():
            for param, msg in msgs.items():
                error_msg[error_type][param] = utils.ravel(msg)
        super().__init__(json.dumps(error_msg, indent=4))


class InconsistentLabelsException(ParamToolsError):
    pass


collision_list = [
    "_data",
    "_errors",
    "_warnings",
    "select_eq",
    "select_ne",
    "select_gt",
    "select_gte",
    "select_lt",
    "select_lte",
    "_adjust",
    "_delete",
    "_numpy_type",
    "_parse_errors",
    "_resolve_order",
    "_schema",
    "_set_state",
    "_state",
    "_stateless_label_grid",
    "_update_param",
    "_validator_schema",
    "_defaults_schema",
    "_select",
    "_defer_validation",
    "operators",
    "adjust",
    "delete",
    "validate",
    "transaction",
    "array_first",
    "clear_state",
    "defaults",
    "dump",
    "items",
    "keys",
    "label_grid",
    "label_validators",
    "keyfuncs",
    "errors",
    "warnings",
    "from_array",
    "parse_labels",
    "read_params",
    "schema",
    "set_state",
    "specification",
    "sort_values",
    "to_array",
    "validation_error",
    "view_state",
    "extend",
    "extend_func",
    "uses_extend_func",
    "label_to_extend",
    "get_index_rate",
    "index_rates",
    "to_dict",
    "_parse_validation_messages",
    "sel",
]


class ParameterNameCollisionException(ParamToolsError):
    pass
