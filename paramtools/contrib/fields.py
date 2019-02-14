import numpy as np
import datetime

from marshmallow import fields as marshmallow_fields


class Float64(marshmallow_fields.Number):
    """
    Define field to match up with numpy float64 type
    """

    num_type = np_type = np.float64


class Int64(marshmallow_fields.Number):
    """
    Define field to match up with numpy int64 type
    """

    num_type = np_type = np.int64


class Bool_(marshmallow_fields.Boolean):
    """
    Define field to match up with numpy bool_ type
    """

    num_type = np_type = np.bool_

    def _deserialize(self, value, attr, obj, **kwargs):
        return np.bool_(super()._deserialize(value, attr, obj, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(bool(value), attr, obj, **kwargs)


class MeshFieldMixin:
    """
    Provides method for accessing contrib.validate
    validators' mesh methods
    """

    def mesh(self):
        if not self.validators:
            return []
        assert len(self.validators) == 1
        return self.validators[0].mesh()


class Str(MeshFieldMixin, marshmallow_fields.Str):
    np_type = object


class Integer(MeshFieldMixin, marshmallow_fields.Integer):
    np_type = int


class Float(MeshFieldMixin, marshmallow_fields.Float):
    np_type = float


class Boolean(MeshFieldMixin, marshmallow_fields.Boolean):
    np_type = bool


class Date(MeshFieldMixin, marshmallow_fields.Date):
    np_type = datetime.date
