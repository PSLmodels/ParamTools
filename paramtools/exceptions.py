

class ParamToolsError(Exception):
    pass

class ParameterUpdateException(ParamToolsError):
    pass

class SparseValueObjectsException(ParamToolsError):
    pass

class ValidationError(ParamToolsError):

    def __init__(self, message, parameter_name=None, adjustment=None, errant_value=None):
        self.message = message
        self.parameter_name = parameter_name
        self.adjustment = adjustment
        self.errant_value = errant_value
        super().__init__(self.message)
