import numpy as np
import datetime

from marshmallow import fields as marshmallow_fields


class Float64(marshmallow_fields.Number):
    """
    Implements "float" :ref:`spec:Type property` for parameter values.
    Defined as
    `numpy.float64 <https://docs.scipy.org/doc/numpy-1.15.0/user/basics.types.html>`__ type
    """

    num_type = np_type = np.float64


class Int64(marshmallow_fields.Number):
    """
    Implements "int" :ref:`spec:Type property` for parameter values.
    Defined as `numpy.int64 <https://docs.scipy.org/doc/numpy-1.15.0/user/basics.types.html>`__ type
    """

    num_type = np_type = np.int64


class Bool_(marshmallow_fields.Boolean):
    """
    Implements "bool" :ref:`spec:Type property` for parameter values.
    Defined as `numpy.bool_ <https://docs.scipy.org/doc/numpy-1.15.0/user/basics.types.html>`__ type
    """

    num_type = np_type = np.bool_

    def _deserialize(self, value, attr, obj, **kwargs):
        return np.bool_(super()._deserialize(value, attr, obj, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(bool(value), attr, obj, **kwargs)


class MeshFieldMixin:
    """
    Provides method for accessing ``contrib.validate``
    validators' grid methods
    """

    def grid(self):
        if not self.validators:
            return []
        assert len(self.validators) == 1
        return self.validators[0].grid()


class Str(MeshFieldMixin, marshmallow_fields.Str):
    """
    Implements "str" :ref:`spec:Type property`.
    """

    np_type = object


class Integer(MeshFieldMixin, marshmallow_fields.Integer):
    """
    Implements "int" :ref:`spec:Type property` for properties
    except for parameter values.
    """

    np_type = int


class Float(MeshFieldMixin, marshmallow_fields.Float):
    """
    Implements "float" :ref:`spec:Type property` for properties
    except for parameter values.
    """

    np_type = float


class Boolean(MeshFieldMixin, marshmallow_fields.Boolean):
    """
    Implements "bool" :ref:`spec:Type property` for properties
    except for parameter values.
    """

    np_type = bool


class Date(MeshFieldMixin, marshmallow_fields.Date):
    """
    Implements "date" :ref:`spec:Type property`.
    """

    np_type = datetime.date
