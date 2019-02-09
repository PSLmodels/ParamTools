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
