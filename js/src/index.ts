import * as yup from "yup";

import {
  Defaults,
  Params,
  SchemaFactory,
  Schema,
  Adjustment,
  ValueObject,
  Param,
} from "./schemafactory";

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

    this.updateParam = this.updateParam.bind(this);
  }

  adjust(params: Adjustment | string) {
    if (typeof params === "string") {
      params = JSON.parse(params) as Adjustment;
    }
    const parsedParams = this.ValidatorSchema.cast(params);
    for (const [param, vos] of Object.entries(parsedParams)) {
      this.updateParam(param, vos);
    }
    return parsedParams;
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

  private updateParam(param: string, newValues: Array<ValueObject>) {
    for (let i = 0; i < newValues.length; i++) {
      const currVals = (this.data[param] as Param).value;
      let matchedAtLeastOnce = false;
      const labelsToCheck = Object.keys(newValues[i]).filter(k => k !== "value");
      let toDelete = [];
      for (let j = 0; j < currVals.length; j++) {
        const match = labelsToCheck.every(label => currVals[j][label] === newValues[i][label]);
        if (match) {
          matchedAtLeastOnce = true;
          if (newValues[i].value === null) {
            toDelete.push(j);
          } else {
            currVals[j].value = newValues[i].value;
          }
        }
      }
      if (toDelete.length > 0) {
        toDelete.sort(item => -item);
        for (const ix of toDelete) {
          currVals.splice(ix, 1);
        }
      }
      if (!matchedAtLeastOnce && newValues[i].value !== null) {
        currVals.push(newValues[i]);
      }
    }
  }
}
