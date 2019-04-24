from marshmallow import fields

from paramtools.schema import (
    EmptySchema,
    BaseValidatorSchema,
    ValueObject,
    get_type,
    get_param_schema,
)
from paramtools import utils


class SchemaBuilder:
    """
    Uses data from:
    - a schema definition file
    - a baseline specification file

    to extend:
    - `schema.BaseParamSchema`
    - `schema.BaseValidatorSchema`

    Once this has been completed, the `load_params` method can be used to
    deserialize and validate parameter data.
    """

    def __init__(self, defaults, field_map={}):
        self.defaults = utils.read_json(defaults)
        schema = self.defaults.pop("schema")
        (self.BaseParamSchema, self.label_validators) = get_param_schema(
            schema, field_map=field_map
        )

    def build_schemas(self):
        """
        For each parameter defined in the baseline specification file:
        - define a parameter schema for that specific parameter
        - define a validation schema for that specific parameter

        Next, create a baseline specification schema class (`ParamSchema`) for
        all parameters listed in the baseline specification file and a
        validator schema class (`ValidatorSchema`) for all parameters in the
        baseline specification file.

        - `ParamSchema` reads and validates the baseline specification file
        - `ValidatorSchema` reads revisions to the baseline parameters and
          validates their type, structure, and whether they are within the
          specified range.

        `param_schema` is defined and used to read and validate the baseline
        specifications file. `validator_schema` is defined to read and validate
        the parameter revisions. The output from the baseline specification
        deserialization is saved in the `context` attribute on
        `validator_schema` and will be utilized when doing range validation.
        """
        param_dict = {}
        validator_dict = {}
        for k, v in self.defaults.items():
            fieldtype = get_type(v)
            classattrs = {"value": fieldtype, **self.label_validators}

            # TODO: what about case where number_dims > 0
            # if not isinstance(v["value"], list):
            #     v["value"] = [{"value": v["value"]}]

            validator_dict[k] = type(
                "ValidatorItem", (EmptySchema,), classattrs
            )

            classattrs = {"value": ValueObject(validator_dict[k], many=True)}
            param_dict[k] = type(
                "IndividualParamSchema", (self.BaseParamSchema,), classattrs
            )

        classattrs = {k: fields.Nested(v) for k, v in param_dict.items()}
        ParamSchema = type("ParamSchema", (EmptySchema,), classattrs)
        param_schema = ParamSchema()
        cleaned_defaults = param_schema.load(self.defaults)

        classattrs = {
            k: ValueObject(v(many=True)) for k, v in validator_dict.items()
        }
        ValidatorSchema = type(
            "ValidatorSchema", (BaseValidatorSchema,), classattrs
        )
        validator_schema = ValidatorSchema()

        return cleaned_defaults, validator_schema
