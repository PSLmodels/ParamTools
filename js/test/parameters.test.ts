import Parameters from "../src";
import { Param } from 'schemafactory';

const data = {
  test: {
    title: "Hello world",
    description: "",
    type: "int" as "int" | "str",
    number_dims: 0,
    value: [{ value: 1 }],
    validators: { range: { min: 0 } },
  },
};

describe("parameters", () => {
  it("simple load", () => {
    const params = new Parameters(data);
    expect((params.data.test as Param).value).toEqual([{ value: 1 }]);
  });

  it("simple adjust", () => {
    const params = new Parameters(data);
    expect((params.data.test as Param).value === [{ value: 1 }]);

    params.adjust({ test: [{ value: 2 }] });
    expect((params.data.test as Param).value === [{ value: 2 }]);
  });
});
