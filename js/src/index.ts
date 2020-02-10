import * as yup from "yup";

import { Defaults, Params, SchemaFactory, Schema, Adjustment } from "./schemafactory";

export default class Parameters {
  defaults: Defaults;
  DefaultsSchema: yup.ObjectSchema<Params>;
  ValidatorSchema: yup.ObjectSchema<Adjustment>;
  schema: Schema;
  data: Params;

  // TODO:
  // labelToExtend: string;
  // arrayFirst: string;
  // usesExtendFunc: boolean;
  // state: { [label: string]: Array<any> };
  // labelGrid: { [label: string]: Array<any> };

  constructor(defaults: Defaults) {
    const { DefaultsSchema, ValidatorSchema, schema, data } = new SchemaFactory(defaults).schemas();
    this.defaults = defaults;
    this.DefaultsSchema = DefaultsSchema;
    this.ValidatorSchema = ValidatorSchema;
    this.schema = schema;
    this.data = data;
  }

  adjust() {
    // todo
  }

  errors() {
    // todo
  }

  specification() {
    // todo
  }

  extend() {
    // todo
  }

  selectEq() {
    // todo
  }

  toArray() {
    // todo
  }

  fromArray() {
    // todo
  }
}
