from paramtools import utils


class ParamToolsError(Exception):
    pass


class ParameterUpdateException(ParamToolsError):
    pass


class SparseValueObjectsException(ParamToolsError):
    pass


class ValidationError(ParamToolsError):
    def __init__(self, messages, dims):
        self.messages = messages
        self.dims = dims
        raveled_messages = {
            param: utils.ravel(msgs) for param, msgs in self.messages.items()
        }
        super().__init__(raveled_messages)


class InconsistentDimensionsException(ParamToolsError):
    pass


collision_list = [
    "_data",
    "_errors",
    "_get",
    "_numpy_type",
    "_parse_errors",
    "_resolve_order",
    "_state",
    "_stateless_dim_mesh",
    "_update_param",
    "_validator_schema",
    "adjust",
    "array_first",
    "clear_state",
    "defaults",
    "dim_mesh",
    "dim_validators",
    "errors",
    "field_map",
    "from_array",
    "read_params",
    "schema",
    "set_state",
    "specification",
    "to_array",
    "validation_error",
    "view_state",
]


class ParameterNameCollisionException(ParamToolsError):
    pass
