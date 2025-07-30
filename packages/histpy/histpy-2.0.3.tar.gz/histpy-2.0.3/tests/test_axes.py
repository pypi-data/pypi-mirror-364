from histpy import *

import numpy as np
from numpy import array_equal as arr_eq
from numpy import random

import pytest
from pytest import approx

from copy import deepcopy

import astropy.units as u

import h5py as h5

nbinsx = 5
nbinsy = 4
nbinsz = 3

x = range(0,nbinsx+1)
y = list(np.linspace(10,20,nbinsy+1))
z = np.linspace(20,30,nbinsz+1)

def test_axes_init():

    # init with one axis, from data of various kinds
    a = Axes(x)
    assert arr_eq(a[0].edges, x)
    a = Axes(y)
    assert arr_eq(a[0].edges, y)
    a = Axes(z)
    assert arr_eq(a[0].edges, z)
    a = Axes(Axis(x, label='foo'))
    assert arr_eq(a[0].edges, x)
    assert a[0].label == 'foo'
    a = Axes(np.array(x))
    assert arr_eq(a[0].edges, x)

    a = Axes(np.array(x), labels='foo') # init single axis with single label
    assert arr_eq(a[0].edges, x) and a.labels == np.array(['foo'])

    # init with array with units -- units
    # are transferred to Axis
    a = Axes(np.array(x) * u.cm)
    assert arr_eq(a[0].edges.value, x)

    # init from lists and other iterables of axes
    a = Axes([x])
    assert arr_eq(a[0].edges, x)

    a = Axes([x, y, z])
    assert \
        arr_eq(a[0].edges, x) and \
        arr_eq(a[1].edges, y) and \
        arr_eq(a[2].edges, z)

    a = Axes(tuple([x, y, z]))
    assert \
        arr_eq(a[0].edges, x) and \
        arr_eq(a[1].edges, y) and \
        arr_eq(a[2].edges, z)

    # we can't just convert from list of Axis to array because
    # that triggers Axis.__array__ on elements.
    arr = np.empty(3, dtype='O')
    arr[0] = Axis(x, label='x')
    arr[1] = Axis(y, label='y')
    arr[2] = Axis(z, label='z')
    a = Axes(arr)
    assert \
        arr_eq(a[0].edges, x) and \
        arr_eq(a[1].edges, y) and \
        arr_eq(a[2].edges, z)

    with pytest.raises(TypeError): # cannot create empty Axes list
        Axes([])

    # init from other Axes object
    b = Axes(a)
    assert a == b

    # init from other Axes object with explicit new labels
    b = Axes(a, labels=['x', 'y', 'z'])
    assert a == b

    with pytest.raises(TypeError):
        Axes(3) # scalar as argument (*not* singleton list or 0-dim array)

    # verify that copy_axes=False does not copy Axes
    ax = [Axis(x), Axis(y), Axis(z)]

    a = Axes(ax)
    assert(ax[0] is not a[0]) # Axis objects are copied

    a = Axes(ax, copy_axes=False)
    assert(ax[0] is a[0]) # Axis objects are not copied

    a = Axes(ax, labels=['a', 'b', 'c'], copy_axes=False)
    assert(ax[0] is not a[0]) # changing labels forces copy

    a = Axes(ax, axis_scale='linear', copy_axes=False)
    assert(ax[0] is not a[0]) # overriding scale forces copy

    with pytest.raises(ValueError): # scales list does not match length of axis list
        a = Axes(ax, axis_scale=['linear', 'symmetric'])

    with pytest.raises(ValueError): # cannot repeat labels
        ar = [Axis(x, label='x'), Axis(y, label='y'), Axis(z, label='x')]
        Axes(ar)

    # copying performs shallow copy, because contents are copy-on-write
    a = Axes(ax)
    b = a.copy()
    assert a == b and all(axa is axb for axa, axb in zip(a, b))

def test_axes_get_and_set():

    ax = [Axis(x, label='x'), Axis(y, label='y'), Axis(z, label='z')]

    a = Axes(ax)

    # label translation
    r = a.label_to_index('z')
    assert r == 2

    r = a.label_to_index(['z', 0, 'y'])
    assert r == (2, 0, 1)

    r = a.label_to_index(('z', 0, 'y'))
    assert r == (2, 0, 1)

    r = a.label_to_index(np.array([2, 0, 1]))
    assert r == (2, 0, 1)

    r = a.label_to_index(slice(0,2))
    assert r == (0,1)

    r = a.label_to_index(slice(None,None))
    assert r == (0,1,2)

    with pytest.raises(KeyError): # missing label
        a.label_to_index(['q'])

    with pytest.raises(KeyError):
        a.label_to_index(3) # out of bounds

    # __getitem__
    assert a[0] == ax[0]
    assert a['x'] == ax[0]

    b = a[0:2]
    assert len(b) == 2 and b[0] == ax[0] and b[1] == ax[1]

    b = a[(0,2)]
    assert len(b) == 2 and b[0] == ax[0] and b[1] == ax[2]

    b = a[[0,2]]
    assert len(b) == 2 and b[0] == ax[0] and b[1] == ax[2]

    b = a[np.array([0,2])]
    assert len(b) == 2 and b[0] == ax[0] and b[1] == ax[2]

    with pytest.raises(KeyError):
        a['w'] # label does not exist

    with pytest.raises(TypeError):
        a[{'w'}] #cannot use a non-list-like

    # labels retrieval
    assert arr_eq(a.labels, np.array(['x', 'y', 'z']))

    # units retrieval
    assert arr_eq(a.units, np.array([None, None, None]))

    # other property retrieval
    assert arr_eq(a.lo_lims, np.array([axis.lo_lim for axis in ax]))
    assert arr_eq(a.hi_lims, np.array([axis.hi_lim for axis in ax]))
    assert arr_eq(a.nbins,   np.array([axis.nbins for axis in ax]))
    assert arr_eq(a.scales,  np.array([axis.axis_scale for axis in ax]))
    assert a.shape == tuple(axis.nbins for axis in ax)

    # __setitem__
    c = a.copy()
    anew = Axis(x, label='new')
    c[0] = anew
    assert c[0] == anew     # list update
    assert c[0] is not anew # Axis is copied
    assert c['new'] == anew # index update

    # explicit set() is equivalent to using __setitem__
    c = a.copy()
    c.set(0, anew)
    assert(c[0] == anew and c[0] is not anew) # copies by default

    # explicit set() with copy=False
    c = a.copy()
    c.set(0, anew, copy=False)
    assert(c[0] == anew and c[0] is anew) # no copy

    c = a.copy()
    c[0] = x # assign from non-Axis that can be converted to Axis
    assert c[0] == Axis(x)

    # extracting, mutating, and replacing a axis without
    # changing the label should work
    c = a.copy()
    anew = c['x'].copy()
    anew.axis_scale = 'symmetric'
    c.set(anew.label, anew, copy=False)
    assert c['x'] is anew

    # assigning multiple elements at once is not allowed
    # (but maybe it should be?)
    with pytest.raises(TypeError):
        c = a.copy()
        c[0:2] = ( Axis([1,2,3]), Axis([4,5,6]) )

    with pytest.raises(ValueError):
        c = a.copy()
        c[0] = Axis([1,2,3]) # changes length of axis

    with pytest.raises(ValueError):
        c = a.copy()
        c[0] = Axis(x, label='y') # repeats axis label

    with pytest.raises(KeyError):
        c = a.copy()
        c[1] = Axis(y) # drops label
        c['y'] # index lookup should fail

    # labels update
    c = a.copy()
    c.labels = ['a', 'b', 'c']
    assert \
        arr_eq(c['a'].edges, ax[0].edges) and \
        arr_eq(c['b'].edges, ax[1].edges) and \
        arr_eq(c['c'].edges, ax[2].edges) and \
        c[0] is not ax[0] # Axis objects were copied

    with pytest.raises(ValueError):
        c.labels = ['a', 'b'] # new label list must have same length

    with pytest.raises(ValueError):
        c.labels = ['a', 'b', 'a'] # new label list must not repeat

def test_axes_findbin():

    A = Axes([[1,2,3]])

    # 1D single finds
    assert A.find_bin(1.5) ==  0
    assert A.find_bin(2)   ==  1
    assert A.find_bin(2.5) ==  1
    assert A.find_bin(0.5) == -1
    assert A.find_bin(3.5) ==  2

    # 1D multiple finds
    assert A.find_bin((0,)) == -1

    r = A.find_bin([0,1,2,3,4])
    assert isinstance(r, np.ndarray) and arr_eq(r, [-1, 0, 1, 2, 2])

    r = A.find_bin(np.array([0,1,2,3,4]))
    assert isinstance(r, np.ndarray) and arr_eq(r, [-1, 0, 1, 2, 2])

    # in 1D, multiple arguments are interpreted
    # as a multidimensional value, which is an error
    with pytest.raises(ValueError):
        A.find_bin(0,1)

    # multi-D finds
    A = Axes([[1,2,3], [1,2,3], [1,2,3]])

    # single find
    assert A.find_bin(0.5, 2, 3.5) == (-1, 1, 2)

    # single find
    assert A.find_bin((0.5, 2, 3.5)) == (-1, 1, 2)

    with pytest.raises(ValueError):
        A.find_bin(0,1) # wrong number of dims

    with pytest.raises(ValueError):
        A.find_bin(0,1,2,3) # wrong number of dims

    with pytest.raises(ValueError):
        A.find_bin(0) # wrong number of dims, special case in find_bin

    vs = [0, 1, 2, 3, 4]
    rs0 = [-1, 0, 1, 2, 2]

    # each coord as separate argument
    rs = A.find_bin(vs, vs, vs)
    assert isinstance(rs, tuple) and \
        isinstance(rs[0], np.ndarray) and \
        arr_eq(rs, [rs0, rs0, rs0])

    # all coords as array-like
    rs = A.find_bin([vs, vs, vs])
    assert isinstance(rs, tuple) and \
        isinstance(rs[0], np.ndarray) and \
        arr_eq(rs, [rs0, rs0, rs0])

    # all coords as array
    rs = A.find_bin(np.array([vs, vs, vs]))
    assert isinstance(rs, tuple) and \
        isinstance(rs[0], np.ndarray) and \
        arr_eq(rs, [rs0, rs0, rs0])

    # value array for each axis may have
    # a different shape and size
    A.find_bin([1,2,3], [1,2,3,4], [[1,2],[3,4],[0,-1]])

def test_axes_readwrite(tmp_path):

    # verify that Axes returns axes from a file in the order they were
    # written

    labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    a = Axes([(1,2)] * len(labels), labels=labels)

    f = h5.File(tmp_path / "garbage_file", "w")
    g = f.create_group("axes") # *not* tracking order

    a.write(g)

    aa = Axes.open(g)

    assert aa == a

def test_axes_sanity():

    A = Axes([[1,2,3], [1,2,3], [1,2,3]])
    a = np.array([1, 2, 3])

    with pytest.raises(ValueError):
        A.expand_dims(a,[1,2]) # number of axes should match a

    a = np.ones((2,2,2,2))
    with pytest.raises(ValueError):
        A.expand_dims(a,[0,1,2,2]) # number of can't be bigger than |A|
