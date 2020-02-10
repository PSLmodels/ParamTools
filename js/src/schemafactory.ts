import * as yup from "yup";

export interface ValueObject {
  value: number | string | boolean | Date | Array<number | string | boolean | Date>;
  [key: string]: any;
}

export interface FormValueObject {
  value: Array<any>;
  [key: string]: any;
}

export interface Range {
  min?: any;
  max?: any;
  level?: "error" | "warning";
}

export interface Choice {
  choices: Array<any>;
  level?: "error" | "warning";
}

export interface DateRange {
  min: Date;
  max: Date;
  level: "error" | "warning";
}

export interface Validators {
  range?: Range;
  choice?: Choice;
  date_range?: DateRange;
}

type AllowedTypes = "int" | "float" | "bool" | "date" | "str";

export interface Param {
  title: string;
  description: string;
  notes?: string;
  section_1?: string;
  section_2?: string;
  type: AllowedTypes;
  number_dims?: number;
  value: Array<ValueObject>;
  validators: Validators;
  form_fields?: any;
  indexable?: boolean;
  checkbox?: boolean;
  [additionalMember: string]: any;
}

interface ParamSchemaObject {
  title: yup.StringSchema<string>;
  description: yup.StringSchema<string>;
  type: yup.MixedSchema<AllowedTypes>;
  number_dims: yup.NumberSchema<number>;
  value: yup.ArraySchema<ValueObject>;
  validators: yup.ObjectSchema<Validators>;
  [additionalMember: string]: yup.MixedSchema<any> | yup.ObjectSchema<any>;
}

interface AdditionalMembers {
  [name: string]: { type: AllowedTypes; number_dims: Number; };
}

export interface Labels {
  [label: string]: {
    type: AllowedTypes;
    validators: Validators;
  };
}

export interface Operators {
  array_first?: boolean;
  label_to_extend?: string;
  uses_extend_func?: boolean;
}

export interface Schema {
  labels?: Labels;
  operators?: Operators;
  additional_members?: AdditionalMembers;
}

export interface Params {
  [paramName: string]: Param;
}

export interface Adjustment {
  [param: string]: Array<ValueObject>;
}

export type Defaults = string | Params;

const integerMsg: string = "Must be an integer.";
const floatMsg: string = "Must be a floating point number.";
const dateMsg: string = "Must be a date.";
const boolMsg: string = "Must be a boolean value.";
const minMsg: string = "Must be greater than or equal to ${min}";
const maxMsg: string = "Must be less than or equal to ${max}";
const oneOfMsg: string = "Must be one of the following values: ${values}";

const inspectType = (type: AllowedTypes) => {
  if (type == "int") {
    return yup.number().typeError(integerMsg);
  } else if (type == "float") {
    return yup.number().typeError(floatMsg);
  } else if (type == "bool") {
    return yup.bool().typeError(boolMsg);
  } else if (type == "date") {
    return yup.date().typeError(dateMsg);
  } else {
    return yup.string();
  }
};

const getField = (param_data: {
  type: AllowedTypes;
  validators: Param["validators"];
  number_dims?: Param["number_dims"];
}) => {
  let yupObj = inspectType(param_data.type);
  if ("range" in param_data.validators && !(yupObj instanceof yup.boolean)) {
    let min_val = null;
    let max_val = null;
    if (param_data.validators?.range && "min" in param_data.validators.range) {
      min_val = param_data.validators?.range?.min;
      yupObj = yupObj.min(min_val, minMsg);
    }
    if (param_data.validators?.range && "max" in param_data.validators.range) {
      max_val = param_data.validators?.range?.max;
      yupObj = yupObj.max(max_val, maxMsg);
    }
  }
  if (param_data.validators.choice?.choices.length) {
    yupObj = yupObj.oneOf(param_data.validators?.choice?.choices, oneOfMsg);
  }
  if (param_data.number_dims === 1) {
    return yup.array().of<number | boolean | Date | string>(yupObj);
  } else {
    return yupObj;
  }
};

const ValidatorsSchema = () =>
  yup.object().shape({
    date_range: yup.object().shape({
      min: yup.date(),
      max: yup.date(),
      level: yup
        .string()
        .oneOf(["error", "warning"])
        .default("error"),
    }),
    range: yup.object().shape({
      min: yup.mixed(),
      max: yup.mixed(),
      level: yup
        .string()
        .oneOf(["error", "warning"])
        .default("error"),
    }),
    choice: yup.object().shape({
      choices: yup.array().of(yup.mixed()),
      level: yup
        .string()
        .oneOf(["error", "warning"])
        .default("error"),
    }),
  });

const SchemaValidator = (schema: Schema) => {
  const labelValidator = yup.object().shape({
    type: yup
      .mixed<AllowedTypes>()
      .oneOf(["str", "float", "int", "bool", "date"])
      .required(),
    number_dims: yup.number().default(0),
    validators: ValidatorsSchema(),
  });
  let labels: yup.ObjectSchema<Labels> = yup.object({});
  for (const [label] of Object.entries(schema.labels || {})) {
    labels.shape({ [label]: labelValidator });
  }

  const amValidator = yup.object().shape({
    type: yup
      .mixed<AllowedTypes>()
      .oneOf(["str", "float", "int", "bool", "date"])
      .required(),
    number_dims: yup
      .number()
      .integer()
      .default(0),
  });
  let am: yup.ObjectSchema<AdditionalMembers> = yup.object({});
  for (const [amName] of Object.entries(schema.labels || {})) {
    am.shape({ [amName]: amValidator });
  }

  return yup.object().shape<Schema>({
    labels: labels,
    operators: yup.object().shape({
      array_first: yup.boolean(),
      label_to_extend: yup.string(),
      uses_extend_func: yup.boolean(),
    }),
    additional_members: am,
  });
};

const BaseParamSchema: ParamSchemaObject = {
  title: yup.string().required(),
  description: yup.string().required(),
  type: yup
    .mixed<AllowedTypes>()
    .oneOf(["str", "float", "int", "bool", "date"])
    .required(),
  number_dims: yup
    .number()
    .integer()
    .default(0),
  value: yup.array<ValueObject>(),
  validators: ValidatorsSchema(),
};

const readDefaults = (defaults: Defaults): Params => {
  if (typeof defaults === "string") {
    return JSON.parse(defaults);
  } else {
    return defaults;
  }
};

const readSchema = (schema: Schema) => {
  let optionalFields: { [field: string]: yup.MixedSchema<any>; } = {};
  for (const [name, data] of Object.entries(schema.additional_members || {})) {
    let fieldType = inspectType(data.type);
    optionalFields[name] = fieldType;
  }
  const ParamSchema: ParamSchemaObject = { ...BaseParamSchema, ...optionalFields };

  let labelFields: { [field: string]: yup.MixedSchema<any>; } = {};
  for (const [label, data] of Object.entries(schema.labels || {})) {
    labelFields[label] = getField(data);
  }
  return { ParamSchema, labelFields };
};

export class SchemaFactory {
  defaults: Params;
  schema: Schema;
  ParamSchema: ParamSchemaObject;
  labelFields: { [label: string]: yup.Schema<any>; };

  constructor(defaults: Defaults) {
    defaults = readDefaults(defaults);
    this.defaults = {};
    for (const [param, data] of Object.entries(defaults)) {
      if (param !== "schema") this.defaults[param] = data;
    }

    const schema = ((defaults.schema || {}) as unknown) as Schema;

    // oneOf does not jive with typescript enum type.
    this.schema = SchemaValidator(schema).cast(defaults.schema || {}) as Schema;
    const { ParamSchema, labelFields } = readSchema(this.schema);
    this.ParamSchema = ParamSchema;
    this.labelFields = labelFields;
    this.schemas = this.schemas.bind(this);
  }

  schemas() {
    let defaultsschema: { [param: string]: yup.ObjectSchema<Param>; } = {};
    let validatorschema: { [param: string]: yup.ArraySchema<any>; } = {};
    for (const [param, param_data] of Object.entries(this.defaults)) {
      const field = getField(param_data);
      const valueObjectField = yup.array().of(
        yup.object().shape({
          ...this.labelFields,
          value: field,
        })
      );
      defaultsschema[param] = yup.object().shape({ ...this.ParamSchema, value: valueObjectField });
      validatorschema[param] = valueObjectField;
    }
    let DefaultsSchema = yup.object().shape<Params>(defaultsschema);
    let ValidatorSchema: yup.ObjectSchema<Adjustment> = yup.object().shape(validatorschema);

    return {
      DefaultsSchema,
      ValidatorSchema,
      schema: this.schema,
      data: DefaultsSchema.cast(this.defaults),
    };
  }
}
