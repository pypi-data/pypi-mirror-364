from histpy import *

import numpy as np
from numpy import array_equal as arr_eq
from numpy import random

import pytest
from pytest import approx

from copy import deepcopy

import astropy.units as u

from histpy.feature import COPY_IF_NEEDED

def test_axis_init():

    # basic initialization
    x = [1.,2.,3.,4.,5.]
    a = Axis(x, label='Foo')

    assert len(a) == 5
    assert a.axis_scale == 'linear'
    assert arr_eq(a[:], np.array(x))

    # initialize with array; copies by default
    x = np.array(x)
    b = Axis(x, 'Foo')
    assert a == b and b.edges is not x

    # initialize with array, no copy
    x = np.array(x)
    b = Axis(x, 'Foo', copy=False)

    assert a == b and b.edges is x

    # initialize from another axis
    c = Axis(b)
    assert b == c

    # initialize with change of label
    c = Axis(b, label='Bar')
    assert c.label == 'Bar'

    # later change of label
    c.label = 'Baz'
    assert c.label == 'Baz'

    # initialize with change of scale
    c = Axis(b, scale='log')
    assert c.axis_scale == 'log'

    # change scale after init
    c = Axis(b, scale='linear')
    c.axis_scale = 'log'
    assert c.axis_scale == 'log'

    # initialize from Quantity array
    b = Axis(x * u.Unit("cm"))
    assert arr_eq(b[:], x)
    assert b.unit == u.cm

    # initialize with explicit unit
    c = Axis(x, unit="cm")
    assert b == c

    # initialize with change of unit
    c = Axis(10*x*u.Unit("mm"), unit="cm")
    assert b == c

    # initialize from axis with change of unit
    c = Axis(b, unit="mm")
    assert arr_eq(c.edges, x * 10 * u.mm)

    # test copy
    c = Axis(b, unit="mm", label='Foo', scale='log')
    d = c.copy()
    assert c == d and not np.shares_memory(c._edges, d._edges)

    # test replace_edges
    c = Axis([1,2,3,4,5])
    edges = np.array([2,4,6])

    d = c.replace_edges(edges)
    assert arr_eq(d.edges, edges) and d.edges is not edges

    d = c.replace_edges(list(edges)) # Handle lists
    assert arr_eq(d.edges, edges) and d.edges is not edges

    d = c.replace_edges(edges, copy=False)
    assert arr_eq(d.edges, edges) and np.shares_memory(d.edges, edges)

    with pytest.raises(ValueError): # checks for invalid edges
        edges = np.array([1, 0, 2])
        d = c.replace_edges(edges)

    # test replace_edges with units
    c = Axis([1, 2, 3, 4, 5]*u.s)
    edges = [2, 4, 6]*u.ms

    d = c.replace_edges(edges)
    assert arr_eq(d.edges, edges) and d.edges is not edges

    # test subclass copy with no override
    class MyAxis(Axis):
        def __init__(self, edges):
            super().__init__(edges)
            self.foo = [1,2,3]

    m = MyAxis([0,1,2])
    mc = m.copy()
    assert mc == m and mc.foo is not m.foo

    mc = deepcopy(m) # test deepcopy hook
    assert mc == m and mc.foo is not m.foo

    # deepcopy avoids duplication if
    # it is used on subclass fields
    v = (m.foo, m)
    vc = deepcopy(v)
    assert vc[0] is vc[1].foo

    # validation of edge array

    with pytest.raises(ValueError):
        a = Axis([[0, 1, 2], [0, 1, 2]]) # multi-dimensional array

    with pytest.raises(ValueError):
        a = Axis([0]) # need two edges for a bin

    with pytest.raises(ValueError):
        a = Axis([1, 2, 1]) # edges must be monotonically increasing

    # invalid scales
    with pytest.raises(ValueError):
        a = Axis(x, scale='crazy') # invalid scale type

    with pytest.raises(ArithmeticError):
        a = Axis([-1, 0, 1, 2, 3], scale='log') # log scale cannot be negative

def test_axis_index():

    x = [1.,2.,3.,4.,5.]
    a = Axis(x, label='Foo')

    b = a[1:3]
    assert arr_eq(b.edges, x[1:4])

    b = a[1:100] # values past end of array are clipped when slicing
    assert arr_eq(b.edges, x[1:5])

    b = a[1:-1]
    assert arr_eq(b.edges, x[1:4])

    b = a[-2:-1]
    assert arr_eq(b.edges, x[2:4])

    b = a[2]
    assert arr_eq(b.edges, x[2:4])

    b = a[-1]
    assert arr_eq(b.edges, x[3:5])

    b = a[::2]
    assert arr_eq(b.edges, [1., 3., 5.])

    b = a[1::2]
    assert arr_eq(b.edges, [2., 4.])

    with pytest.raises(IndexError):
        a[0:0] # empty bin list

    with pytest.raises(IndexError):
        a[3:2] # reversed order

    with pytest.raises(IndexError):
        a[1:3:-1] # non-positive stride

    with pytest.raises(TypeError):
        # non-int, non-slice
        a[np.zeros(len(x) + 1, dtype=bool)]

def test_axis_units():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', unit="cm")

    assert a.unit == u.cm

    # convert axis with unit to compatible unit
    a = a.to(unit="mm")
    assert arr_eq(a.edges, x * 10 * u.mm)

    # change unit without updating values
    b = a.to(unit="cm", update=False)
    assert arr_eq(b.edges, x * 10 * u.cm)
    assert not np.shares_memory(b._edges, a._edges)

    # test disabling copy
    b = a.to(unit="cm", update=False, copy=False)
    assert arr_eq(b.edges, x * 10 * u.cm)
    assert np.shares_memory(b._edges, a._edges)

    # remove unit entirely
    a = a.to(unit=None)
    assert arr_eq(a.edges, x * 10)

    # test
    a = Axis(x, label='Foo') # no unit

    # convert axis without unit to compatible unit
    b = a.to(unit=u.dimensionless_unscaled)
    assert arr_eq(b.edges, x)

    with pytest.raises(TypeError):
        a.to(unit="cm") # cannot convert non-unit to unit

def test_axis_scale():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    assert(a.axis_scale == 'linear')

    a.axis_scale = 'log'

    assert(a.axis_scale == 'log')

    with pytest.raises(ValueError):
        a.axis_scale = 'foo' # unknown mode

    with pytest.raises(ArithmeticError):
        x = np.array([-1., 0.,1.])
        a = Axis(x, label='Foo', scale='log') # log mode with non-positive x

    with pytest.raises(ArithmeticError):
        x = np.array([-1., 0.,1.])
        a = Axis(x, label='Foo', scale='linear')
        a.axis_scale = 'log' # log mode with non-positive x

def test_axis_array():
    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    y = np.array(a, copy=COPY_IF_NEEDED)
    assert np.shares_memory(y, a.edges)

    # note that for numpy <= 2.0, __array__ is
    # not called with copy=True even in this case,
    # so we are forced to call it explicitly to test

    #y = np.array(h, copy=True)
    y = a.__array__(copy=True)

    assert arr_eq(y, a.edges)
    assert not np.shares_memory(y, a.edges)

    y = np.array(a, dtype=int)
    assert arr_eq(y, a.edges) and y.dtype == int

def test_axis_compare():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    b = Axis(x, label='Foo', scale='linear')
    assert a == b

    b = Axis(x[:-1], label='Foo', scale='linear')
    assert a != b

    b = Axis(x, label='Bar', scale='linear')
    assert a != b

    b = Axis(x, label='Foo', scale='log')
    assert a != b

    b = Axis(x*u.cm, label='Foo', scale='linear')
    assert a != b

def test_axis_findbin():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    b = a.find_bin(1.5)
    assert(b == 0)

    b = a.find_bin(4.5)
    assert(b == 3)

    b = a.find_bin(2)
    assert(b == 1)

    b = a.find_bin(2, right=True)
    assert(b == 0)

    b = a.find_bin(0) # underflow
    assert(b == -1)

    b = a.find_bin(6) # overflow
    assert(b == a.nbins)

    b = a.find_bin(1.5 * u.dimensionless_unscaled) # equal to no unit
    assert(b == 0)

    c = a.to(unit=u.cm, update=False)
    b = c.find_bin(1.5 * u.cm) # units are removed
    assert(b == 0)

    b = c.find_bin(u.cm) # units are removed; bare unit
    assert(b == 0)

    c = a.to(unit=u.mm, update=False)
    b = c.find_bin(1 * u.cm) # units are removed
    assert(b == a.nbins) # 10mm is off end of array

    # find_bin can take arrays
    b = a.find_bin(np.array([0.5, 1.5, 2.5, 3.5]))
    assert(arr_eq(b, [-1, 0, 1, 2]))

    # array of Quantities
    c = a.to(unit=u.cm, update=False)
    b = c.find_bin(np.array([0.5, 1.5, 2.5, 3.5]) * u.cm)
    assert(arr_eq(b, [-1, 0, 1, 2]))

    # cannot use bare value on Axis with units
    with pytest.raises(u.UnitConversionError):
        a = Axis(x, label='Foo', scale='linear', unit=u.cm)
        a.find_bin(3)

    # cannot use Quantity on axis without units
    with pytest.raises(u.UnitConversionError):
        a = Axis(x, label='Foo', scale='linear')
        a.find_bin(3 * u.cm)

def test_axis_interp():

    def clamp(v, lo, hi):
        v = np.atleast_1d(v)
        return np.clip(v, a_min=lo, a_max=hi)

    def res(b, w, c):
        return c[b[0]] * w[0] + c[b[1]] * w[1]

    def reslog(b, w, c):
        return np.exp(np.log(c[b[0]]) * w[0] + np.log(c[b[1]]) * w[1])

    x = np.array([1., 2., 4., 8., 16.])

    # linear interpolation
    a = Axis(x, scale='linear')
    c = a.centers

    # test interior values
    v = 5.
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 3.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test centers of boundary bins
    v = 1.5
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 12.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test exterior values
    v = 0.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 20.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 0-D array should behave like scalar
    v = np.array(5.)
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 1-D array should behave like array
    v = [5.]
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,1) and weights.shape == (2,1)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = np.arange(0., 20.)
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # interp_weights result should preserve shape of input values,
    # even if they have unit dimensions
    v = np.array([ [ [ 3., 5., 9.], [2., 7., 0.] ] ])
    bins, weights = a.interp_weights(v)
    assert bins.shape    == (2,) + v.shape
    assert weights.shape == (2,) + v.shape
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test with units
    a = a.to(u.cm, update=False)
    c = a.centers

    v = 5. * u.cm
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c).value == approx(clamp(v, c[0], c[-1]).value)

    v = np.arange(0., 20.) * u.cm
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c).value == approx(clamp(v, c[0], c[-1]).value)


    # linear interpolation with symmetric axis
    a = Axis(x, scale='symmetric')
    c = a.centers

    # test interior values
    v = 5.
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 3.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test centers of boundary bins
    v = 1.5
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 12.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test exterior values
    v = 0.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 20.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 0-D array should behave like scalar
    v = np.array(5.)
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 1-D array should behave like array
    v = [5.]
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,1) and weights.shape == (2,1)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = np.arange(0., 20.)
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # interp_weights result should preserve shape of input values,
    # even if they have unit dimensions
    v = np.array([ [ [ 3., 5., 9.], [2., 7., 0.] ] ])
    bins, weights = a.interp_weights(v)
    assert bins.shape    == (2,) + v.shape
    assert weights.shape == (2,) + v.shape
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test with units
    a = a.to(u.cm, update=False)
    c = a.centers

    v = 5. * u.cm
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c).value == approx(clamp(v, c[0], c[-1]).value)

    v = np.arange(0., 20.) * u.cm
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert res(bins, weights, c).value == approx(clamp(v, c[0], c[-1]).value)

    # log-linear interpolation with logarithmic axis
    a = Axis(x, scale='log')
    c = a.centers

    # test interior values
    v = 5.
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 3.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test centers of boundary bins
    v = 1.5
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 12.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # test exterior values
    v = 0.01
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = 20.
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 0-D array should behave like scalar
    v = np.array(5.)
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,) and weights.shape == (2,)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # 1-D array should behave like array
    v = [5.]
    bins, weights = a.interp_weights(v)
    assert bins.shape == (2,1) and weights.shape == (2,1)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    v = np.arange(0.01, 20.)
    bins, weights = a.interp_weights(v)
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

    # interp_weights result should preserve shape of input values,
    # even if they have unit dimensions
    v = np.array([ [ [ 3., 5., 9.], [2., 7., 0.01] ] ])
    bins, weights = a.interp_weights(v)
    assert bins.shape    == (2,) + v.shape
    assert weights.shape == (2,) + v.shape
    assert np.all(bins >= 0) and np.all(bins < len(c))
    assert np.all(weights >= 0.) and np.all(weights <= 1.)
    assert reslog(bins, weights, c) == approx(clamp(v, c[0], c[-1]))

def test_axis_properties():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    assert arr_eq(a.lower_bounds, [1, 2, 3, 4])
    assert arr_eq(a.upper_bounds, [2, 3, 4, 5])
    assert arr_eq(a.bounds, [[1,2], [2,3], [3,4], [4,5]])
    assert arr_eq(a.lo_lim, 1)
    assert arr_eq(a.hi_lim, 5)
    assert arr_eq(a.widths, [1, 1, 1, 1])
    assert a.label_with_unit == 'Foo'

    a = a.to(unit=u.cm, update=False)

    assert arr_eq(a.lower_bounds, np.array([1, 2, 3, 4]) * u.cm)
    assert arr_eq(a.upper_bounds, np.array([2, 3, 4, 5]) * u.cm)
    assert arr_eq(a.bounds, np.array([[1,2], [2,3], [3,4], [4,5]]) * u.cm)
    assert arr_eq(a.lo_lim, 1 * u.cm)
    assert arr_eq(a.hi_lim, 5 * u.cm)
    assert arr_eq(a.widths, np.array([1, 1, 1, 1]) * u.cm)

    assert a.label_with_unit == 'Foo [cm]'

    a.label = None

    assert a.label_with_unit == '[cm]'

def test_axis_centers():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    c = a.centers
    assert arr_eq(c, [1.5, 2.5, 3.5, 4.5])

    a.axis_scale = 'symmetric'
    c = a.centers
    assert arr_eq(c, [1, 2.5, 3.5, 4.5])

    a.axis_scale = 'log'
    c = a.centers
    v = np.log2(x)
    r = 2**(0.5*(v[:-1] + v[1:]))
    assert c == approx(r)

    # test with units

    a = a.to(unit="cm", update=False)
    a.axis_scale = 'linear'

    c = a.centers
    assert arr_eq(c, np.array([1.5, 2.5, 3.5, 4.5])*u.cm)

def test_axis_math():

    x = np.array([1.,2.,3.,4.,5.])
    a = Axis(x, label='Foo', scale='linear')

    # out of place ops

    b = a * 2
    assert arr_eq(b.edges, x * 2)

    b = 2 * a
    assert arr_eq(b.edges, x * 2)

    b = a / 2
    assert arr_eq(b.edges, x / 2)

    b = a + 2
    assert arr_eq(b.edges, x + 2)

    b = 2 + a
    assert arr_eq(b.edges, x + 2)

    b = a - 2
    assert arr_eq(b.edges, x - 2)

    # adding vectors is OK if result is monotonic
    b = a + x
    assert arr_eq(b.edges, x + x)

    b = a * x
    assert arr_eq(b.edges, x * x)

    # in place ops
    b = a.copy()
    b *= 2
    assert arr_eq(b.edges, x * 2)

    b = a.copy()
    b /= 2
    assert arr_eq(b.edges, x / 2)

    b = a.copy()
    b += 2
    assert arr_eq(b.edges, x + 2)

    b = a.copy()
    b -= 2
    assert arr_eq(b.edges, x - 2)

    # adding vectors is OK if result is monotonic
    b = a.copy()
    b += x
    assert arr_eq(b.edges, x + x)

    b = a.copy()
    b *= x
    assert arr_eq(b.edges, x * x)

    with pytest.raises(ValueError):
        # makes bins non-monotonic
        b = a * -1

    # test with units

    b = a * (2 * u.dimensionless_unscaled)
    assert arr_eq(b.edges, x * 2)

    with pytest.raises(TypeError):
        # non-dimensionless units not allowed
        b = a * (2 * u.cm)
        assert arr_eq(b.edges, x * 2)

    with pytest.raises(TypeError):
        # non-dimensionless units not allowed; bare unit
        b = a * u.cm
        assert arr_eq(b.edges, x * 2)

    # test with axis units
    x = x*u.cm
    a = Axis(x, label='Foo', scale='linear')

    b = a * 2
    assert arr_eq(b.edges, x * 2)

    b = a + 2*u.cm
    assert arr_eq(b.edges, x + 2*u.cm)

    b = a + 0.02*u.m
    assert arr_eq(b.edges, x + 2*u.cm)

    with pytest.raises(TypeError):
        # Scaling factor must be unitless
        b = a * 1*u.cm

    with pytest.raises(u.UnitConversionError):
        # Shift value must have the same units
        b = a + 1.

# reading and writing functions are tested by Histogram read/write tests
