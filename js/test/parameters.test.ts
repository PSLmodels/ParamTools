import Parameters from "../src";

describe("parameters", () => {
  it("loads", () => {
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
    const params = new Parameters(data);
    expect(params.data.test.value).toEqual([{ value: 1 }]);
  });
});
