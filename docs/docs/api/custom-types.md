# Custom Types

Often, the behavior for a field needs to be customized to support a particular shape or validation method that ParamTools does not support out of the box. In this case, you may use the `register_custom_type` function to add your new `type` to the ParamTools type registry. Each `type` has a corresponding `field` that is used for serialization and deserialization. ParamTools will then use this `field` any time it is handling a `value`, `label`, or `member` that is of this `type`.

ParamTools is built on top of [`marshmallow`](https://github.com/marshmallow-code/marshmallow), a general purpose validation library. This means that you must implement a custom `marshmallow` field to go along with your new type. Please refer to the `marshmallow` [docs](https://marshmallow.readthedocs.io/en/stable/) if you have questions about the use of `marshmallow` in the examples below.


## 32 Bit Integer Example

ParamTools's default integer field uses NumPy's `int64` type. This example shows you how to define an `int32` type and reference it in your `defaults`.

First, let's define the Marshmallow class:

```python
import marshmallow as ma
import numpy as np

class Int32(ma.fields.Field):
    """
    A custom type for np.int32.
    https://numpy.org/devdocs/reference/arrays.dtypes.html
    """
    # minor detail that makes this play nice with array_first
    np_type = np.int32

    def _serialize(self, value, *args, **kwargs):
        """Convert np.int32 to basic, serializable Python int."""
        return value.tolist()

    def _deserialize(self, value, *args, **kwargs):
        """Cast value from JSON to NumPy Int32."""
        converted = np.int32(value)
        return converted

```


Now, reference it in our defaults JSON/dict object:

```python
import paramtools as pt


# add int32 type to the paramtools type registry
pt.register_custom_type("int32", Int32())


class Params(pt.Parameters):
    defaults = {
        "small_int": {
            "title": "Small integer",
            "description": "Demonstrate how to define a custom type",
            "type": "int32",
            "value": 2
        }
    }


params = Params(array_first=True)


print(f"value: {params.small_int}, type: {type(params.small_int)}")

# value: 2, type: <class 'numpy.int32'>

```

One problem with this is that we could run into some deserialization issues. Due to integer overflow, our deserialized result is not the number that we passed in--it's negative!

```python
params.adjust(dict(
    # this number wasn't chosen randomly.
    small_int=2147483647 + 1
))

# OrderedDict([('small_int', [{'value': -2147483648}])])
```

### Marshmallow Validator

Fortunately, you can specify a custom validator with `marshmallow` or ParamTools. Making this works requires modifying the `_deserialize` method to check for overflow like this:

```python
    # check out the full example at the bottom of this page.
    def _deserialize(self, value, *args, **kwargs):
        """Cast value from JSON to NumPy Int32."""
        converted = np.int32(value)

        # check for overflow and let range validator
        # display the error message.
        if converted != int(value):
            return int(value)

        return converted
```

 Now, let's see how to use `marshmallow` to fix this problem:

```python
import marshmallow as ma
import paramtools as pt


# get the minimum and maxium values for 32 bit integers.
min_int32 = -2147483648  # = np.iinfo(np.int32).min
max_int32 = 2147483647  # = np.iinfo(np.int32).max

# add int32 type to the paramtools type registry
pt.register_custom_type(
    "int32",
    Int32(validate=[
        ma.validate.Range(min=min_int32, max=max_int32)
    ])
)


class Params(pt.Parameters):
    defaults = {
        "small_int": {
            "title": "Small integer",
            "description": "Demonstrate how to define a custom type",
            "type": "int32",
            "value": 2
        }
    }


params = Params(array_first=True)

params.adjust(dict(
    small_int=np.int64(max_int32) + 1
))

# ValidationError: {
#     "errors": {
#         "small_int": [
#             "Must be greater than or equal to -2147483648 and less than or equal to 2147483647."
#         ]
#     }
# }

```

### ParamTools Validator

Finally, we will use ParamTools to solve this problem. We need to modify how we create our custom `marshmallow` field so that it's wrapped by ParamTools's `PartialField`. This makes it clear that your field still needs to be initialized, and that your custom field is able to receive validation information from the `defaults` configuration:


```python
import paramtools as pt


# add int32 type to the paramtools type registry
pt.register_custom_type(
    "int32",
    pt.PartialField(Int32)
)


class Params(pt.Parameters):
    defaults = {
        "small_int": {
            "title": "Small integer",
            "description": "Demonstrate how to define a custom type",
            "type": "int32",
            "value": 2,
            "validators": {
                "range": {"min": -2147483648, "max": 2147483647}
            }
        }
    }


params = Params(array_first=True)

params.adjust(dict(
    small_int=2147483647 + 1
))

# ValidationError: {
#     "errors": {
#         "small_int": [
#             "small_int 2147483648 > max 2147483647 "
#         ]
#     }
# }

```


### Complete Int32 field

```python
import marshmallow as ma
import numpy as np

class Int32(ma.fields.Field):
    """
    A custom type for np.int32.
    https://numpy.org/devdocs/reference/arrays.dtypes.html
    """
    # minor detail that makes this play nice with array_first
    np_type = np.int32

    def _serialize(self, value, *args, **kwargs):
        """Convert np.int32 to basic Python int."""
        return value.tolist()

    def _deserialize(self, value, *args, **kwargs):
        """Cast value from JSON to NumPy Int32."""
        converted = np.int32(value)

        # check for overflow and let range validator
        # display the error message.
        if converted != int(value):
            return int(value)

        return converted

```