from histpy import *

import numpy as np
from numpy import array_equal as arr_eq
from numpy import random

import pytest
from pytest import approx

from copy import deepcopy

from sparse import DOK, COO, GCXS, SparseArray

import sparse
from packaging.version import Version
if Version(sparse.__version__) >= Version('0.16.0'):
    import sparse.numba_backend._settings as sps
else:
    import sparse._settings as sps

from scipy.sparse import csr_matrix, csr_array, csc_array

import astropy.units as u


nbinsx = 5
nbinsy = 4
nbinsz = 3

x = range(0,nbinsx+1)
y = list(np.linspace(10,20,nbinsy+1))
z = np.linspace(20,30,nbinsz+1)

def test_histogram_init():
    '''
    Check the various ways a histogram can be initialized
    '''

    # 1D from range
    h = Histogram(x, track_overflow=True)
    assert h.ndim == 1
    assert h.shape == (nbinsx,)
    assert arr_eq(h.axis.edges, np.array(x))
    assert arr_eq(h.axis.widths, np.ones(nbinsx))
    assert arr_eq(h.axis.centers, np.arange(0,nbinsx)+.5)
    assert arr_eq(h[...], np.zeros(nbinsx + 2))
    assert arr_eq(h[:], np.zeros(nbinsx))
    assert h.axis.nbins == nbinsx
    assert h.find_bin(0) == 0
    assert h.find_bin(.5) == 0
    assert arr_eq(h.find_bin([0,1]), [0,1])

    # 1D from list
    h = Histogram(y)
    assert h.ndim == 1
    assert arr_eq(h.axis.edges, np.array(y))

    # 1D from array
    h = Histogram(z)
    assert h.ndim == 1
    assert arr_eq(h.axis.edges, np.array(z))

    # 1D from list of list
    h = Histogram([y])
    assert h.ndim == 1
    assert arr_eq(h.axis.edges, np.array(y))

    # 1D from sparse array
    h = Histogram(x, sparse = True) # empty
    assert h.is_sparse

    h = Histogram(x, contents = DOK(len(x)-1)) # sparsity follows contents
    assert h.is_sparse and isinstance(h.full_contents, COO)

    h = Histogram(x, contents = GCXS.from_numpy(np.ones(len(x)-1)))
    assert h.is_sparse and isinstance(h.full_contents, COO)

    h = Histogram(x, contents=np.ones(len(x) - 1), sparse=True) # convert to sparse
    assert h.is_sparse and isinstance(h.full_contents, COO)

    # The implicit conversion of a sparse array into a dense one
    # fails by default, unless the user set a environtment variable
    # See https://sparse.pydata.org/en/0.11.0/operations.html?highlight=auto_densify#package-configuration
    # This sets, at import time, the variable sps.AUTO_DENSIFY
    # I couldn't find any other way to access it. It's possible this behavior would change in the future.

    if 'AUTO_DENSIFY' not in dir(sps):
        raise RuntimeError("Fix me. sparse package not longer using AUTO_DENSIFY")

    default_SPARSE_AUTO_DENSIFY = sps.AUTO_DENSIFY

    sps.AUTO_DENSIFY = False
    with pytest.raises(RuntimeError):
        h = Histogram(x, contents=DOK(len(x)-1), sparse=False) # won't automatically convert to dense

    sps.AUTO_DENSIFY = True
    h = Histogram(x, contents=DOK(len(x)-1), sparse=False) # convert to dense
    assert not h.is_sparse

    sps.AUTO_DENSIFY = default_SPARSE_AUTO_DENSIFY

    # 2D from SciPy sparse
    h = Histogram([y,y], contents = csr_matrix(np.ones((nbinsy, nbinsy))))
    assert h.ndim == 2
    assert h.shape == (nbinsy, nbinsy)
    assert h.is_sparse and np.all(h.contents == np.ones((nbinsy, nbinsy)))

    h = Histogram([y,y],
                  contents = csr_array(np.ones((nbinsy, nbinsy))),
                  sumw2 = csc_array(np.ones((nbinsy, nbinsy))))
    assert h.is_sparse and np.all(h.contents == np.ones((nbinsy, nbinsy)))
    assert h.sumw2.is_sparse and  np.all(h.sumw2.contents == np.ones((nbinsy, nbinsy)))

    # Multi-D from list of lists
    h = Histogram([y,y,y])
    assert h.ndim == 3
    assert h.shape == (nbinsy, nbinsy, nbinsy)
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes,[np.array(y),np.array(y),np.array(y)]))

    # Multi-D from list of arrays
    h = Histogram([z,z,z])
    assert h.ndim == 3
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes,[np.array(z),np.array(z),np.array(z)]))

    # Multi-D from list of arrays and lists
    h = Histogram(Axes([x,y,z], labels=['x','y','z']), track_overflow=True)
    assert h.ndim == 3
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes,[np.array(x),np.array(y),np.array(z)]))
    assert all(arr_eq(a.centers,axis2) for a,axis2 in zip(h.axes,[x[:-1]+np.diff(x)/2,y[:-1]+np.diff(y)/2,z[:-1]+np.diff(z)/2]))
    assert all(arr_eq(a.widths,axis2) for a,axis2 in zip(h.axes,[np.diff(x),np.diff(y),np.diff(z)]))
    assert arr_eq(h[:], np.zeros([nbinsx, nbinsy, nbinsz]))
    assert arr_eq(h[...], np.zeros([nbinsx+2, nbinsy+2, nbinsz+2]))
    assert arr_eq(h.nbins, [nbinsx, nbinsy, nbinsz])

    assert arr_eq(h.find_bin(0.5, 13, 27), [0,1,2])

    # Multi-D from array
    h = Histogram(np.reshape(np.linspace(0,100,30),[3,10]))
    assert h.ndim == 3
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes,list(np.reshape(np.linspace(0,100,30),[3,10]))))

    # 1D from sparse array
    h = Histogram((x,y,z), sparse=True)
    assert isinstance(h.full_contents, SparseArray)

    h = Histogram((x,y,z), contents = DOK((len(x)-1, len(y)-1, len(z)-1)))
    assert h.is_sparse

    # test track_overflow behavior default
    h = Histogram([x,y], sumw2=True)
    assert all(h.track_overflow() == False)
    assert all(h.sumw2.track_overflow() == False)

    h = Histogram([x,y], contents=np.ones((nbinsx, nbinsy)), sumw2=True)
    assert all(h.track_overflow() == False)
    assert all(h.sumw2.track_overflow() == False)

    h = Histogram([x,y], contents=np.ones((nbinsx, nbinsy + 2)), sumw2=True)
    assert all(h.track_overflow() == [False, True])
    assert all(h.sumw2.track_overflow() == [False, True])

    # test track_overflow behavior non-default
    h = Histogram([x,y], sumw2=True, track_overflow=False)
    assert all(h.track_overflow() == False)
    assert all(h.sumw2.track_overflow() == False)

    h = Histogram([x,y], contents=np.ones((nbinsx, nbinsy)),
                  sumw2=True, track_overflow=True)
    assert all(h.track_overflow() == True)
    assert all(h.sumw2.track_overflow() == True)

    h = Histogram([x,y], contents=np.ones((nbinsx, nbinsy + 2)),
                  sumw2=True, track_overflow=True)
    assert all(h.track_overflow() == [True, True])
    assert all(h.sumw2.track_overflow() == [True, True])

    h = Histogram([x,y], contents=np.ones((nbinsx, nbinsy)),
                  sumw2=True, track_overflow={ 0 : True } )
    assert all(h.track_overflow() == [True, False])
    assert all(h.sumw2.track_overflow() == [True, False])

    # sumw2 shape does not affect track_overflow default,
    # and sumw2 is coerced to match overflow tracking of
    # contents
    s = Histogram([x,y], track_overflow = True)
    h = Histogram([x,y], sumw2 = s)
    assert all(h.track_overflow() == False)
    assert all(h.sumw2.track_overflow() == False)

    s = np.ones((nbinsx, nbinsy))
    h = Histogram([x,y], sumw2 = s, track_overflow=True)
    assert all(h.track_overflow() == True)
    assert all(h.sumw2.track_overflow() == True)

    # test type-casting of contents
    h = Histogram((x,y), dtype=np.float32)
    assert h.contents.dtype == np.float32

    h = Histogram((x,y), contents = np.ones((nbinsx, nbinsy)), dtype=np.float32)
    assert h.contents.dtype == np.float32

    h = Histogram((x,y), contents = COO(np.ones((nbinsx, nbinsy))), dtype=np.float32)
    assert h.contents.dtype == np.float32

    h = Histogram((x,y), contents = np.ones((nbinsx, nbinsy)), sparse=True, dtype=np.float32)
    assert h.contents.dtype == np.float32

    h = Histogram((x,y), contents = list(np.ones((nbinsx, nbinsy))), dtype=np.float32)
    assert h.contents.dtype == np.float32

    # test type casting of sumw2 -- should always match contents
    h = Histogram((x,y), dtype=np.float32, sumw2=True)
    assert h.sumw2.dtype == np.float32

    h = Histogram((x,y), sumw2=np.ones((nbinsx, nbinsy), dtype=int))
    assert h.sumw2.dtype == np.float64

    h = Histogram((x,y), dtype=np.float32, sparse=True, sumw2=COO(np.ones((nbinsx, nbinsy))))
    assert h.sumw2.dtype == np.float32

    h = Histogram((x,y), dtype=np.float32, sumw2=np.ones((nbinsx, nbinsy)))
    assert h.sumw2.dtype == np.float32

    h = Histogram((x,y), dtype=np.float32, sumw2=list(np.ones((nbinsx, nbinsy))))
    assert h.sumw2.dtype == np.float32

    # test adding sumw2 after initialization
    h = Histogram([z,z,z])
    h.set_sumw2(True)
    assert arr_eq(h.sumw2.contents, np.zeros(h.contents.shape))

    h = Histogram([z,z,z])
    h.set_sumw2(h) # from Histogram
    assert arr_eq(h.sumw2.contents, h.contents)
    assert not np.shares_memory(h.sumw2.contents, h.contents)

    h = Histogram([z,z,z], track_overflow = False)
    v = np.ones(h.contents.shape)
    h.set_sumw2(v) # from array
    assert arr_eq(h.sumw2.contents, np.ones(h.contents.shape))
    assert not np.shares_memory(h.sumw2.contents, v)

    h = Histogram([z,z,z], track_overflow = False)
    v = np.ones(h.contents.shape)
    h.set_sumw2(v, copy=False) # from array, but don't copy
    assert arr_eq(h.sumw2.contents, np.ones(h.contents.shape))
    assert np.shares_memory(h.sumw2.contents, v)

    # test copy_contents
    a = np.ones((9,9))
    b = 2*np.ones((9,9))

    h = Histogram([range(10), range(10)], contents=a, sumw2=b, track_overflow=False)
    assert not np.shares_memory(h.contents, a) and not np.shares_memory(h.sumw2.contents, b)

    h = Histogram([range(10), range(10)], contents=a, sumw2=b,
                  track_overflow=False, copy_contents=False)
    assert np.shares_memory(h.contents, a) and np.shares_memory(h.sumw2.contents, b)

    # if sumw2 is a Histogram, we use it unchanged if copy_contents is False
    bh = Histogram([range(10), range(10)], contents=b, track_overflow=False)
    h = Histogram([range(10), range(10)], contents=a, sumw2=bh, track_overflow=False, copy_contents=False)
    assert np.shares_memory(h.contents, a) and np.shares_memory(h.sumw2.contents, bh.contents)

    # do not copy value is extracted from Quantity if copy_contents is False
    a *= u.cm
    b *= u.cm*u.cm
    h = Histogram([range(10), range(10)], contents=a, sumw2=b, track_overflow=False, copy_contents=False)
    assert np.shares_memory(h.contents, a) and np.shares_memory(h.sumw2.contents, b)

    # test astype
    h2 = h.astype(np.float32)
    assert h2.contents.dtype == np.float32 and h2.sumw2.dtype == np.float32

    h2 = h.astype(np.float64)
    assert h2 is not h

    h2 = h.astype(np.float64, copy=False)
    assert h2 is h

def test_other_setters_getters():

    # Axis setter
    h = Histogram(x, sumw2 = True)

    h.axis = np.arange(len(x))

    assert h.axis == Axis(np.arange(len(x)))

    assert h.nbins == nbinsx

    # Axis only for 1D
    h = Histogram([y,y,y])

    with pytest.raises(ValueError):
        h.axis

def test_histogram_copy():

    class HLike(Histogram):
        def __init__(self, axes):
            super().__init__(axes)
            self.foo = [1,2,3]

    class HLike_Copy(Histogram):
        def __init__(self, axes):
            super().__init__(axes)
            self.foo = [1,2,3]

        def copy(self):
            new = super().copy()
            new.foo = self.foo # do not copy
            return new

    h = HLike([1,2,3,4,5])
    hc = h.copy()

    assert h == hc and h.foo is not hc.foo

    # test __deepcopy__ hook
    hc = deepcopy(h)

    assert h == hc and h.foo is not hc.foo

    # deepcopy avoids duplication if
    # it is used on subclass fields
    v = (h.foo, h)
    vc = deepcopy(v)
    assert vc[0] is vc[1].foo

    h = HLike_Copy([1,2,3,4,5])
    hc = h.copy()

    assert h == hc and h.foo is hc.foo

    # test __deepcopy__ hook
    hc = deepcopy(h)

    assert h == hc and h.foo is hc.foo

def test_histogram_fill_and_index():
    """
    Check the fill() method

    Also check slicing by the [] operator. Note that this is different than
    the slice() method, which returns a histogram rather than just the contents.
    """

    # Check 1D filling and indexing
    h = Histogram(x, track_overflow=True)

    for i in range(-1,nbinsx+1):
        h.fill(i+0.5, weight = i)

    assert arr_eq(h[-1:h.end+1], h[-1:nbinsx+1])
    assert arr_eq(h[-1:nbinsx+1], range(-1,nbinsx+1))
    assert arr_eq(h[-1:h.end], h[-1:nbinsx])
    assert arr_eq(h[-1:h.end-1], h[-1:nbinsx-1])
    assert h[h.end] == nbinsx

    assert arr_eq(h[-1:h.end+1], h[h.all])
    assert arr_eq(h[:], range(0,nbinsx))
    assert arr_eq(h[-1:5], range(-1,5))
    assert arr_eq(h[:5], range(0,5))
    assert arr_eq(h[[0,2,3]], [0,2,3])

    # fill all at once
    h = Histogram(x, track_overflow=True)

    v = np.arange(-1, nbinsx + 1)
    h.fill(v + 0.5, weight = v)

    assert arr_eq(h[-1:h.end+1], h[-1:nbinsx+1])
    assert arr_eq(h[-1:nbinsx+1], range(-1,nbinsx+1))
    assert arr_eq(h[-1:h.end], h[-1:nbinsx])
    assert arr_eq(h[-1:h.end-1], h[-1:nbinsx-1])
    assert h[h.end] == nbinsx

    assert arr_eq(h[-1:h.end+1], h[h.all])
    assert arr_eq(h[:], range(0,nbinsx))
    assert arr_eq(h[-1:5], range(-1,5))
    assert arr_eq(h[:5], range(0,5))
    assert arr_eq(h[[0,2,3]], [0,2,3])

    # Filling without tracking under/overflow
    h = Histogram(x, track_overflow=False)

    for i in range(-1,nbinsx+1):
        h.fill(i+0.5, weight = i)

    assert arr_eq(h[:], range(0,nbinsx))

    # fill all at once
    h = Histogram(x, track_overflow=False)

    v = np.arange(-1, nbinsx + 1)
    h.fill(v + 0.5, weight = v)

    assert arr_eq(h[:], range(0,nbinsx))

    # filling should add together weights of repeat values
    h = Histogram(x, track_overflow=False)
    h.fill([0.5] * 100, weight=1)

    assert h[0] == 100
    assert h[np.asarray(0, dtype=int)] == 100

    # multidimensional fill should broadcast inputs
    h = Histogram([[1,2,3],[1,2,3],[1,2,3]])
    h.fill([1,1], 1, [[1,1],[1,1]])
    assert h[0,0,0] == 4

    # Check 3D filling and indexing
    h = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow=True)

    for ix,vx in enumerate(x[:-1]):
        for iy,vy in enumerate(y[:-1]):
            for iz,vz in enumerate(z[:-1]):

                h.fill(vx,vy,vz, weight = (ix*nbinsy + iy)*nbinsz + iz)

    assert arr_eq(h[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz)))
    first_xbin = np.zeros((nbinsy+2,nbinsz+2))
    first_xbin[1:-1,1:-1] = np.reshape(range(0, nbinsy*nbinsz), (nbinsy,nbinsz))
    assert arr_eq(h[0,...], first_xbin)
    assert arr_eq(h.sumw2[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz))**2)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [0])
    h.fill(x[0],y[0],z[nbinsz], weight = 10)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [10])

    assert np.sum(h[:]) == np.sum(range(0,nbinsx*nbinsy*nbinsz))
    assert np.sum(h[...]) == np.sum(h[:]) + 10

    # fill all at once
    h = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow=True)

    p = []
    w = []
    for ix,vx in enumerate(x[:-1]):
        for iy,vy in enumerate(y[:-1]):
            for iz,vz in enumerate(z[:-1]):
                p.append((vx, vy, vz))
                w.append((ix*nbinsy + iy)*nbinsz + iz)

    p = tuple(np.asarray(p).transpose())
    w = np.asarray(w)

    h.fill(*p, weight=w)

    assert arr_eq(h[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz)))
    first_xbin = np.zeros((nbinsy+2,nbinsz+2))
    first_xbin[1:-1,1:-1] = np.reshape(range(0, nbinsy*nbinsz), (nbinsy,nbinsz))
    assert arr_eq(h[0,...], first_xbin)
    assert arr_eq(h.sumw2[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz))**2)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [0])
    h.fill(x[0],y[0],z[nbinsz], weight = 10)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [10])

    assert np.sum(h[:]) == np.sum(range(0,nbinsx*nbinsy*nbinsz))
    assert np.sum(h[...]) == np.sum(h[:]) + 10

    # Check sparse 1D filling

    # filling should add together weights of repeat values
    h = Histogram(x, track_overflow=False, sparse=True)
    h.fill([0.5] * 100, weight=1)

    assert h[0] == 100

    # Check sparse 3D filling and indexing
    h = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, sparse=True, track_overflow=True)

    for ix,vx in enumerate(x[:-1]):
        for iy,vy in enumerate(y[:-1]):
            for iz,vz in enumerate(z[:-1]):

                h.fill(vx,vy,vz, weight = (ix*nbinsy + iy)*nbinsz + iz)

    h = h.to_dense()

    assert arr_eq(h[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz)))
    first_xbin = np.zeros((nbinsy+2,nbinsz+2))
    first_xbin[1:-1,1:-1] = np.reshape(range(0, nbinsy*nbinsz), (nbinsy,nbinsz))
    assert arr_eq(h[0,...], first_xbin)
    assert arr_eq(h.sumw2[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz))**2)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [0])
    h.fill(x[0],y[0],z[nbinsz], weight = 10)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [10])

    assert np.sum(h[:]) == np.sum(range(0,nbinsx*nbinsy*nbinsz))
    assert np.sum(h[...]) == np.sum(h[:]) + 10

    # all at once
    h = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, sparse=True, track_overflow=True)

    p = []
    w = []
    for ix,vx in enumerate(x[:-1]):
        for iy,vy in enumerate(y[:-1]):
            for iz,vz in enumerate(z[:-1]):
                p.append((vx, vy, vz))
                w.append((ix*nbinsy + iy)*nbinsz + iz)

    p = tuple(np.asarray(p).transpose())
    w = np.asarray(w)

    h.fill(*p, weight=w)

    h = h.to_dense()

    assert arr_eq(h[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz)))
    first_xbin = np.zeros((nbinsy+2,nbinsz+2))
    first_xbin[1:-1,1:-1] = np.reshape(range(0, nbinsy*nbinsz), (nbinsy,nbinsz))
    assert arr_eq(h[0,...], first_xbin)
    assert arr_eq(h.sumw2[:], np.reshape(range(0, nbinsx*nbinsy*nbinsz), (nbinsx,nbinsy,nbinsz))**2)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [0])
    h.fill(x[0],y[0],z[nbinsz], weight = 10)
    assert arr_eq(h[0,0,-1:h.end+1], [0] + list(range(0,nbinsz)) + [10])

    assert np.sum(h[:]) == np.sum(range(0,nbinsx*nbinsy*nbinsz))
    assert np.sum(h[...]) == np.sum(h[:]) + 10

    with pytest.raises(u.UnitConversionError):
        # cannot fill a histogram without units with Quantities
        h.fill(0,0,0, weight=1*u.cm)

    with pytest.raises(u.UnitConversionError):
        # cannot fill a histogram with units with scalars
        hz = h.to(unit="cm", update=False)
        hz.fill(0,0,0, weight=1)

    # sumw2 initialization with array
    h2 = Histogram(h.axes, h[...], h.sumw2[...])
    assert h == h2

    # sumw2 initialization with array-like
    h3 = Histogram(h.axes, h[...], sumw2 = [ [ list(r) for r in s ] for s in h.sumw2[...]])
    assert h == h3

    # initialization with units and setting units later
    hh = Histogram(h.axes, h[...], h.sumw2[...], unit="cm")
    assert hh.unit == u.Unit("cm")

    hh2 = deepcopy(h)
    hh2.to(unit="cm", update=False, copy=False)
    assert hh == hh2

    # changing units of existing Histogram
    hh2.to(unit="mm", copy=False)
    hh2.to(unit="cm", copy=False)
    np.testing.assert_allclose(hh.full_contents, hh2.full_contents, atol=1e-14) # floating-point double precision

    # initialization with units from value with a different unit type
    hh3 = Histogram(h.axes, u.Quantity(h[...]*10., unit="mm"), h.sumw2[...]*(10.*10.), unit="cm")
    np.testing.assert_allclose(hh.full_contents, hh3.full_contents, atol=1e-14) # floating-point double precision

    # histogram and sumw2 have mismatched axes
    with pytest.raises(ValueError):
        Histogram(h.axes, h[...], Histogram(h.axes[:-1]))

    # histogram and sumw2 have mismatched overflow tracking
    with pytest.raises(ValueError):
        Histogram(h.axes, h[...], Histogram(h.axes, h.sumw2[...], track_overflow = False), track_overflow=True)

    # histogram is sparse and sumw2 is dense -- will sparsify sumw2
    hhw = Histogram(h.axes, COO.from_numpy(h[...]), h.sumw2)
    assert hhw.sumw2.is_sparse

    # The implicit conversion of a sparse array into a dense one
    # fails by default, unless the user set a environtment variable
    # See https://sparse.pydata.org/en/0.11.0/operations.html?highlight=auto_densify#package-configuration
    # This sets, at import time, the variable sps.AUTO_DENSIFY
    # I couldn't find any other way to access it. It's possible this behavior would change in the future.

    if 'AUTO_DENSIFY' not in dir(sps):
        raise RuntimeError("Fix me. sparse package not longer using AUTO_DENSIFY")

    default_SPARSE_AUTO_DENSIFY = sps.AUTO_DENSIFY

    sps.AUTO_DENSIFY = False
    # histogram is dense and sumw2 is sparse -- will not automatically densify
    with pytest.raises(RuntimeError):
        Histogram(h.axes, h[...], Histogram(h.axes, COO.from_numpy(h.sumw2[...])))

    sps.AUTO_DENSIFY = True
    hhw = Histogram(h.axes, h[...], Histogram(h.axes, COO.from_numpy(h.sumw2[...])))
    assert not hhw.sumw2.is_sparse

    sps.AUTO_DENSIFY = default_SPARSE_AUTO_DENSIFY

    # indexing with a dictionary
    v = h[{'x': slice(1,3), 'y': 3}]

    assert arr_eq(v, h.contents[1:3,3,:])

    # indexing with a mask
    mask = np.zeros(h.contents.shape, dtype=bool)
    mask[1:3,0:2,1:2] = True
    v = h[mask]

    assert arr_eq(v, h.contents[np.array(mask)])

    # indexing with a mask presented as array-like
    mask = np.ones(h.contents.shape, dtype=bool)
    mask =  list(list(list(z) for z in y) for y in mask)
    v = h[mask]

    assert arr_eq(v, h.contents[np.array(mask)])

    # indexing with a partial mask
    mask = np.zeros(h.contents.shape[:-1], dtype=bool)
    mask[1:3,0:2] = True
    v = h[mask, 2]

    assert arr_eq(v, h.contents[mask, 2])

    # mask cannot be padded to match Histogram
    with pytest.raises(ValueError):
        mask = np.zeros((3,3), dtype=bool)
        h[mask]

    # bin error -- read with sum2
    v = h.bin_error[:]
    assert arr_eq(v, np.sqrt(h.sumw2.contents))

    v = h.bin_error.contents
    assert arr_eq(v, np.sqrt(h.sumw2.contents))

    v = np.asarray(h.bin_error)
    assert arr_eq(v, np.sqrt(h.sumw2.contents))

    v = h.bin_error.full_contents
    assert arr_eq(v, np.sqrt(h.sumw2.full_contents))

    # bin error -- write with sum2
    h0 = deepcopy(h)
    h0.bin_error[0,0,0] = 5.
    assert (5*5) == h0.sumw2.contents[0,0,0]

    # bin error -- read with sum2, with units
    h2 = h.to("cm", update=False)
    v = h2.bin_error[:]
    assert arr_eq(v, np.sqrt(np.abs(h.sumw2.contents)) * u.cm)

    # if h is sparse, returned bin error has no unit
    h3 = h2.to_sparse()
    v = h3.bin_error[:]
    assert np.all(v == np.sqrt(np.abs(h3.sumw2.contents)))

    # bin error -- write with sum2, with units
    h2 = h.to("cm", update=False)
    h2.bin_error[0,0,0] = 5. * u.cm
    assert (5*5) * u.cm**2 == h2.sumw2.contents[0,0,0]

    # bin error -- read without sum2
    h2 = Histogram(h.axes, h[...], sumw2 = None)
    v = h2.bin_error[:]
    assert arr_eq(v, np.sqrt(np.abs(h.contents)))

    # bin error -- write without sumw2 should fail
    with pytest.raises(ValueError):
        h2.bin_error[0,0,0] = 5

    # bin error -- read without sum2, with units
    h2 = h2.to("cm", update=False)
    v = h2.bin_error[:]
    assert arr_eq(v, np.sqrt(np.abs(h.contents)) * u.cm)

    # clear
    h0 = deepcopy(h)
    h0.clear()
    assert h0 == Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow=True)

    # clear overflow with unit
    hh0 = deepcopy(hh)
    hh0.clear()
    assert hh0 == Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, unit="cm", track_overflow=True)

    hs = h.to_sparse()
    hs.clear()
    assert hs == Histogram(Axes([x,y,z], labels = ['x','y','z']), sparse=True, sumw2 = True, track_overflow=True)

    # clear oflow/uflow
    h0.clear_overflow()
    h0.clear_overflow(0)
    h0.clear_underflow()
    h0.clear_underflow(2)
    h0.clear_underflow_and_overflow(1)

    # clear oflow/uflow with unit
    hh0.clear_overflow()
    hh0.clear_overflow(0)
    hh0.clear_underflow()
    hh0.clear_underflow(2)

    hs.clear_overflow()
    hs.clear_overflow(0)
    hs.clear_underflow()
    hs.clear_underflow(2)
    hs.clear_underflow_and_overflow(1)

    hhs = hh.to_sparse()
    hhs.clear_overflow()
    hhs.clear_overflow(0)
    hhs.clear_underflow()
    hhs.clear_underflow(2)

    # Sparse
    # Note: arr_eq only works with dense
    h = Histogram(x, sparse = True, track_overflow=True)

    for i in range(-1,nbinsx+1):
        h.fill(i+0.5, weight = i)

    assert arr_eq(h[-1:h.end+1].todense(), h[-1:nbinsx+1].todense())
    assert arr_eq(h[-1:nbinsx+1].todense(), range(-1,nbinsx+1))
    assert arr_eq(h[-1:h.end].todense(), h[-1:nbinsx].todense())
    assert arr_eq(h[-1:h.end-1].todense(), h[-1:nbinsx-1].todense())
    assert h[h.end] == nbinsx

    assert arr_eq(h[:].todense(), range(0,nbinsx))
    assert arr_eq(h[-1:5].todense(), range(-1,5))
    assert arr_eq(h[:5].todense(), range(0,5))
    assert arr_eq(h[[0,2,3]].todense(), [0,2,3])

    # sparse arrays do not support indexing with arrays of arbitrary
    # shape, either for reading or for writing.  1D arrays work fine.

    v = h[np.asarray([1,2,3,4])]
    assert all(v == h.contents[1:5])

    with pytest.raises(IndexError):
        h[np.asarray([[1,2],[3,4]])]

    hs = h.copy()
    hs[np.asarray([1,2,3,4])] = np.array([5,6,7,8])
    assert all(hs[1:5] == np.array([5,6,7,8]))

    with pytest.raises(IndexError):
        hs[np.asarray([[1,2],[3,4]])] = np.array([5,6,7,8])

    # dense/sparse conversion
    h = Histogram(x, sumw2 = True, sparse = True)
    hd = h.to_dense()
    hs = hd.to_sparse()
    assert h == hs
    hdd = hs.to_dense()
    assert hd == hdd

    # overflow tracking
    h  = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow=True)

    # setting track_overflow from array-like
    h2 = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow = [True, False, True])
    assert np.all(h2.track_overflow() == [True, False, True])

    # setting track_overflow from dict
    h3 = Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow = {'x': True, 'z': True})
    assert h3 == h2

    # setting track_overflow from invalid type
    with pytest.raises(TypeError):
        Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow = "invalid")

    # setting track_overflow from array-like of wrong size
    with pytest.raises(ValueError):
        Histogram(Axes([x,y,z], labels = ['x','y','z']), sumw2 = True, track_overflow = [True, False])

    # updating track_overflow after initialization
    h2.track_overflow([True, True, True])
    assert h == h2

    # stripping overflow from dense matrix should result in a contiguous array
    h2.track_overflow(False)
    assert h2.full_contents.data.contiguous and h2.sumw2.full_contents.data.contiguous

def test_histogram_fill_and_index_units():
    """
    Check the fill() method with units

    Also check slicing by the [] operator. Not that this is different than
    the slice() method, which returns a histogram rather than just the contents.
    """

    # Check 1D filling and indexing
    axes_unit = u.cm
    contents_unit = u.s
    h = Histogram(x*axes_unit, unit = contents_unit, track_overflow=True)

    for i in range(-1,nbinsx+1):
        h.fill((i+0.5)*axes_unit, weight = i*contents_unit)

    assert arr_eq(h[2], 2*contents_unit)
    assert arr_eq(h[:], range(0,nbinsx)*contents_unit)
    assert arr_eq(h[-1:5], range(-1,5)*contents_unit)
    assert arr_eq(h[:5], range(0,5)*contents_unit)
    assert arr_eq(h[[0,2,3]], [0,2,3]*contents_unit)

    h = Histogram(x*axes_unit,
                  contents = COO.from_numpy(np.ones((nbinsx))))

    # The implicit conversion of a sparse array into a dense one
    # fails by default, unless the user set a environtment variable
    # See https://sparse.pydata.org/en/0.11.0/operations.html?highlight=auto_densify#package-configuration
    # This sets, at import time, the variable sps.AUTO_DENSIFY
    # I couldn't find any other way to access it. It's possible this behavior would change in the future.

    if 'AUTO_DENSIFY' not in dir(sps):
        raise RuntimeError("Fix me. sparse package not longer using AUTO_DENSIFY")

    default_SPARSE_AUTO_DENSIFY = sps.AUTO_DENSIFY

    sps.AUTO_DENSIFY = False
    with pytest.raises(RuntimeError):
        arr = np.array(h)

    sps.AUTO_DENSIFY = True

    arr = np.array(h)

    assert arr_eq(arr, h.contents.todense())

    sps.AUTO_DENSIFY = default_SPARSE_AUTO_DENSIFY

def test_histogram_concatenate():

    h1 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx, nbinsy),
                   track_overflow = True)
    h2 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx+2, nbinsy+2),
                   sumw2 = random.rand(nbinsx+2, nbinsy+2))


    # Without under/overflow
    hc = Histogram.concatenate(z, [h2,h2,h1], label = 'z')

    hc_contents = np.zeros([nbinsz, nbinsx+2, nbinsy+2])
    hc_contents[0] = h2[...]
    hc_contents[1] = h2[...]
    hc_contents[2] = h1[...]

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents)

    assert hc == hc_check

    # With under/overflow
    hc = Histogram.concatenate(z, [h1,h2,h2,h1,h2], label = 'z')

    hc_contents = np.zeros([nbinsz+2, nbinsx+2, nbinsy+2])
    hc_contents[0] = h1[...]
    hc_contents[1] = h2[...]
    hc_contents[2] = h2[...]
    hc_contents[3] = h1[...]
    hc_contents[4] = h2[...]

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents)

    assert hc == hc_check

    # With sumw2
    hc = Histogram.concatenate(z, [h2,h2,h2], label = 'z')

    hc_contents = np.zeros([nbinsz, nbinsx+2, nbinsy+2])
    hc_contents[0] = h2[...]
    hc_contents[1] = h2[...]
    hc_contents[2] = h2[...]

    hc_sumw2 = np.zeros([nbinsz, nbinsx+2, nbinsy+2])
    hc_sumw2[0] = h2.sumw2[...]
    hc_sumw2[1] = h2.sumw2[...]
    hc_sumw2[2] = h2.sumw2[...]

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents,
                         sumw2 = hc_sumw2)

    assert hc == hc_check

    # overflow tracking default
    hc = Histogram.concatenate(z, [h2, h2, h2])
    assert hc.track_overflow()[0] == False

    hc = Histogram.concatenate(z, [h2, h2, h2, h2, h2])
    assert hc.track_overflow()[0] == True

    # overflow tracking non-default
    hc = Histogram.concatenate(z, [h2, h2, h2], track_overflow = True)
    assert hc.track_overflow()[0] == True


    # cannot concatenate empty list
    with pytest.raises(ValueError):
        Histogram.concatenate(z, [], label='z')

    # Axes mismatch
    h3 = Histogram([y,x], labels=['y','x'],
                   contents = random.rand(nbinsy, nbinsx))

    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h3,h1], label = 'z')

    # overflow tracking mismatch
    h3 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx, nbinsy), track_overflow=False)

    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h3,h1], label = 'z')

    # sparsity mismatch
    h3 = h1.to_sparse()

    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h3,h1], label = 'z')

    # Size mismatch
    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h2,h1], label = 'z')

    # unit mismatch
    h3 = h1.to(unit="cm", update=False)

    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h3,h1], label = 'z')

    # subclass mismatch
    class MyHist(Histogram):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.foo = 3

    h3 = MyHist([x,y], labels=['x','y'],
                contents = random.rand(nbinsx, nbinsy))

    with pytest.raises(ValueError):
        Histogram.concatenate(z, [h3,h1], label = 'z')

    # Sparse
    h2 = h2.to_sparse()

    hc = Histogram.concatenate(z, [h2,h2,h2], label = 'z')

    hc_contents = np.zeros([nbinsz, nbinsx+2, nbinsy+2])
    hc_contents[0] = h2[...].todense()
    hc_contents[1] = h2[...].todense()
    hc_contents[2] = h2[...].todense()

    hc_sumw2 = np.zeros([nbinsz, nbinsx+2, nbinsy+2])
    hc_sumw2[0] = h2.sumw2[...].todense()
    hc_sumw2[1] = h2.sumw2[...].todense()
    hc_sumw2[2] = h2.sumw2[...].todense()

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents,
                         sumw2 = hc_sumw2)

    assert hc == hc_check

    # With units
    h1 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx, nbinsy),
                   unit="cm", track_overflow=True)
    h2 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx+2, nbinsy+2),
                   sumw2 = random.rand(nbinsx+2, nbinsy+2),
                   unit="cm")

    hc = Histogram.concatenate(z, [h2,h2,h1], label = 'z')

    hc_contents = u.Quantity(np.zeros([nbinsz, nbinsx+2, nbinsy+2]), unit="cm")
    hc_contents[0] = h2[...]
    hc_contents[1] = h2[...]
    hc_contents[2] = h1[...]

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents)

    assert hc == hc_check

    # With mixed units and sumw2
    h1 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx, nbinsy),
                   sumw2 = True,
                   unit="cm", track_overflow=True)
    h2 = Histogram([x,y], labels=['x','y'],
                   contents = random.rand(nbinsx+2, nbinsy+2),
                   sumw2 = random.rand(nbinsx+2, nbinsy+2),
                   unit="mm")

    hc = Histogram.concatenate(z, [h2,h2,h1], label = 'z')

    # assigning to hc_contents converts the units to mm and applies the faactor
    hc_contents = u.Quantity(np.zeros([nbinsz, nbinsx+2, nbinsy+2]), unit="mm")
    hc_contents[0] = h2[...]
    hc_contents[1] = h2[...]
    hc_contents[2] = h1[...]

    hc_sumw2 = u.Quantity(np.zeros([nbinsz, nbinsx+2, nbinsy+2]), unit="mm^2")
    hc_sumw2[0] = h2.sumw2[...]
    hc_sumw2[1] = h2.sumw2[...]
    hc_sumw2[2] = h1.sumw2[...]

    hc_check = Histogram([z,x,y], labels=['z','x','y'],
                         contents = hc_contents,
                         sumw2 = hc_sumw2)

    assert hc == hc_check

def test_histogram_project_slice():
    """
    Check the project and slice methods
    """

    # Project
    h = Histogram([x,y,z],
                  np.ones([nbinsx,nbinsy,nbinsz]), np.ones([nbinsx,nbinsy,nbinsz]),
                  labels=['x','y','z'], track_overflow = True)

    xproj = h.project('x')

    assert arr_eq(xproj[:], nbinsy*nbinsz*np.ones(nbinsx))
    assert arr_eq(h.axes['x'].edges, xproj.axis.edges)
    assert xproj != h

    xzproj = h.project('x','z')
    assert arr_eq(xzproj[:], nbinsy*np.ones([nbinsx,nbinsz]))
    assert arr_eq(xzproj.sumw2[:], nbinsy*np.ones([nbinsx,nbinsz]))
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes[['x','z']], xzproj.axes))

    #Project can be used to transpose
    yzx_transpose = h.project('y','z','x')
    assert arr_eq(yzx_transpose[:], np.ones([nbinsy, nbinsz, nbinsx]))
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in
               zip(yzx_transpose.axes, [y,z,x]))
    assert h.full_contents.flags.contiguous # projection yields contiguous result

    noxproj = h.project_out('x')
    assert arr_eq(noxproj[:], nbinsx*np.ones([nbinsy, nbinsz]))
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in zip(h.axes[['y','z']], noxproj.axes))

    noxzproj = h.project_out('x','z')
    assert arr_eq(noxzproj[:], nbinsx*nbinsz**np.ones([nbinsy]))
    assert arr_eq(noxzproj.sumw2[:], nbinsx*nbinsz*np.ones([nbinsy]))
    assert arr_eq(h.axes['y'].edges, noxzproj.axis.edges)
    assert noxzproj != h

    # projecting out nothing makes a copy of the Histogram
    noproj = h.project_out()
    assert arr_eq(noproj.contents, h.contents)
    assert noproj.full_contents is not h.full_contents

    #Slice
    hslice = h.slice[:]
    assert arr_eq(h.contents, hslice.contents)
    assert arr_eq(h.sumw2.contents, hslice.sumw2.contents)

    hn = h.copy()
    hn.set_sumw2(None)
    hslice = hn.slice[:]
    assert arr_eq(hn.contents, hslice.contents)

    hslice = h.slice[...]
    assert h == hslice

    hslice = h.slice[h.all, h.all, ...]
    assert h == hslice

    hslice = h.slice[h.all,h.all,1:2].slice[h.all, 0:1, ...].slice[3:4, ...]
    goodslice = np.pad([[[1]]], 1)
    assert arr_eq(hslice[...], goodslice)
    assert arr_eq(hslice.sumw2[...], goodslice)

    # slicing does not squeeze single-bin dimensions
    hslice = h.slice[:,2,:]
    assert arr_eq(hslice.contents, h.contents[:,2:3,:])
    assert arr_eq(hslice.sumw2.contents, h.sumw2.contents[:,2:3,:])

    # test preservation of overflow/underflow when slicing
    h2 = Histogram([x,y,z],
                   np.ones([nbinsx,nbinsy+2,nbinsz]), np.ones([nbinsx,nbinsy+2,nbinsz]),
                   labels=['x','y','z'], track_overflow = [True, True, False])

    h2[-1,-1,0] = 3
    h2[h2.end,h2.end,h2.end-1] = 3

    # neither uflow nor oflow copied
    hslice = h2.slice[1:3,1:3,1:3]
    res = np.pad(h2.contents[1:3,1:3,1:3], ((1,1), (1,1), (0,0)))
    assert arr_eq(hslice.full_contents, res)

    # uflow copied
    hslice = h2.slice[-1:2,-1:2,0:2]
    res = np.pad(h2.contents[:2,:2,:2], ((1,1), (1,1), (0,0)))
    res[1:-1,0,:] = 1 # explicit uflow in Y
    res[0,0,0] = 3
    assert arr_eq(hslice.full_contents, res)

    # oflow copied
    hslice = h2.slice[1:h2.end+1,1:h2.end+1,1:h2.end]
    res = np.pad(h2.contents[1:,1:,1:], ((1,1), (1,1), (0,0)))
    res[1:-1,-1,:] = 1 # explicit oflow in Y
    res[-1,-1,-1] = 3
    assert arr_eq(hslice.full_contents, res)

    # Sparse project
    h = Histogram([x,y,z],
                  labels=['x','y','z'],
                  sparse = True,
                  sumw2 = True,
                  track_overflow=True)

    h[:,0,:] = 1
    h.sumw2[:,0,:] = 1

    xproj = h.project('x')

    assert arr_eq(xproj[:].todense(), nbinsz*np.ones(nbinsx))

    xzproj = h.project('x','z')
    assert arr_eq(xzproj[:].todense(), np.ones([nbinsx,nbinsz]))
    assert arr_eq(xzproj.sumw2[:].todense(), np.ones([nbinsx,nbinsz]))

    xyzproj = h.project('x','y','z')
    assert xyzproj == h

    #Project can be used to transpose
    hs = Histogram([x,y,z],
                   np.ones([nbinsx,nbinsy,nbinsz]), sparse=True,
                   labels=['x','y','z'], track_overflow = True)

    yzx_transpose = hs.project('y','z','x')
    assert arr_eq(yzx_transpose[:].todense(),
                  np.ones([nbinsy, nbinsz, nbinsx]))
    assert all(arr_eq(axis1,axis2) for axis1,axis2 in
               zip(yzx_transpose.axes, [y,z,x]))

    # Sparse slice
    hslice = h.slice[...]
    assert h == hslice

    hslice = h.slice[h.all, h.all, ...]
    assert h == hslice

    hslice = h.slice[h.all,h.all,1:2].slice[h.all, 0:1, ...].slice[3:4, ...]
    goodslice = np.pad([[[1]]], 1)
    assert arr_eq(hslice[...].todense(), goodslice)
    assert arr_eq(hslice.sumw2[...].todense(), goodslice)

def test_histogram_rebin():

    nbinsx = 100
    nbinsy = 100

    # rebinning without overflow

    ones = np.ones((nbinsx,nbinsy))

    h = Histogram([range(nbinsx + 1), range(nbinsy + 1)],
                  ones, sumw2=2*ones)

    h2 = h.rebin(2)
    assert arr_eq(h2.contents, (2*2) * np.ones((nbinsx//2, nbinsy//2)))
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin((3,))
    assert arr_eq(h2.contents, (3*3) * np.ones((nbinsx//3, nbinsy//3)))
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(4,7)
    assert arr_eq(h2.contents, (4*7) * np.ones((nbinsx//4, nbinsy//7)))
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin([4,7])
    assert arr_eq(h2.contents, (4*7) * np.ones((nbinsx//4, nbinsy//7)))
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    # rebinning with no sumw2
    hn = h.copy()
    hn.set_sumw2(None)

    h2 = hn.rebin(2)
    assert arr_eq(h2.contents, (2*2) * np.ones((nbinsx//2, nbinsy//2)))

    # rebinning with overflow

    ones = np.zeros((nbinsx + 2, nbinsy + 2))
    ones[1:-1,1:-1] = 1. # actual contents

    # add some preexisting content to uflow, oflow bins
    ones[0, 0] = 100
    ones[-1,-1] = 100

    h = Histogram([range(nbinsx + 1), range(nbinsy + 1)],
                  ones, sumw2=2*ones)

    h2 = h.rebin(2)

    # expected result
    res = np.zeros((nbinsx//2 + 2, nbinsy//2 + 2))
    res[1:-1,1:-1] = 2*2
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow
    print(h2.full_contents)
    print(h2.sumw2.full_contents)
    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(3)

    # expected result
    res = np.zeros((nbinsx//3 + 2, nbinsy//3 + 2))
    res[1:-1,1:-1] = 3*3
    res[-1,1:] = 3 # overflow from border bins
    res[1:,-1] = 3 # overflow from border bins
    res[-1,-1] = 1 # overflow from last border in each dim
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(-3)

    # expected result
    res = np.zeros((nbinsx//3 + 2, nbinsy//3 + 2))
    res[1:-1,1:-1] = 9
    res[0,:-1] = 3 # underflow from border bins
    res[:-1,0] = 3 # underflow from border bins
    res[0,0] = 1   # underflow from last border in each dim
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(7,3)

    # expected result
    res = np.zeros((nbinsx//7 + 2, nbinsy//3 + 2))
    res[1:-1, 1:-1] = 7*3
    res[1:-1, -1] = 1*7 # overflow from border bins
    res[-1, 1:-1] = 2*3 # overflow from border bins
    res[-1,-1] = 2 # excess from last border bins
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(7,-3)

    # expected result
    res = np.zeros((nbinsx//7 + 2, nbinsy//3 + 2))
    res[1:-1, 1:-1] = 7*3
    res[1:-1,  0] = 1*7 # overflow from border bins
    res[-1, 1:-1] = 2*3 # underflow from border bins
    res[-1,0] = 2 # excess from last/first border bin
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    # rebinning with partial overflow

    ones = np.zeros((nbinsx, nbinsy + 2))
    ones[:,1:nbinsy+1] = 1. # actual contents

    # add some preexisting content to uflow, oflow bins
    ones[0, 0] = 100
    ones[0,-1] = 100

    h = Histogram([range(nbinsx + 1), range(nbinsy + 1)],
                  ones, sumw2=2*ones)

    h2 = h.rebin(7,7)

    # expected result
    res = np.zeros((nbinsx//7, nbinsy//7 + 2))
    res[:, 1:-1] = 7*7
    res[:,-1] = 2*7 # overflow from border bins (last partial in x discarded)
    res[0,0]  += 100  # preexisting underflow
    res[0,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    h2 = h.rebin(7,-3)

    # expected result
    res = np.zeros((nbinsx//7, nbinsy//3 + 2))
    res[:, 1:-1] = 7*3
    res[:,0] = 7   # underflow from border bins (first partial in x discarded)
    res[0,0]  += 100  # preexisting underflow
    res[0,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    # test with sparse contents

    ones = np.zeros((nbinsx + 2, nbinsy + 2))
    ones[1:-1,1:-1] = 1. # actual contents

    # add some preexisting content to uflow, oflow bins
    ones[0, 0] = 100
    ones[-1,-1] = 100

    h = Histogram([range(nbinsx + 1), range(nbinsy + 1)],
                  ones, sumw2=2*ones, sparse=True)

    h2 = h.rebin(7,-3).to_dense()

    # expected result
    res = np.zeros((nbinsx//7 + 2, nbinsy//3 + 2))
    res[1:-1, 1:-1] = 7*3
    res[1:-1,  0] = 1*7 # overflow from border bins
    res[-1, 1:-1] = 2*3 # underflow from border bins
    res[-1,0] = 2 # excess from last/first border bin
    res[0,0]   += 100  # preexisting underflow
    res[-1,-1] += 100  # preexisting overflow

    assert arr_eq(h2.full_contents, res)
    assert arr_eq(h2.sumw2.full_contents, 2*h2.full_contents)

    # arguments must be scalars
    with pytest.raises(ValueError):
        h.rebin([1,2],[3,4])

    # cannot rebin away an axis
    with pytest.raises(ValueError):
        h.rebin(3,0)

def test_histogram_operator():

    ones = np.ones([nbinsx+2, nbinsy+2])
    h0 = Histogram([x,y], ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h *= 2

    assert h == Histogram([x,y], 2*ones, 4*ones, labels = ['x','y'])

    h = deepcopy(h0)
    h /= 2

    assert h == Histogram([x,y], ones/2, ones/(2*2), labels = ['x','y'])

    h = deepcopy(h0)
    h = h * 2

    assert h == Histogram([x,y], 2*ones, 4*ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = h / 2

    assert h == Histogram([x,y], ones/2, ones/(2*2), labels = ['x','y'])

    h = deepcopy(h0)
    h = 2 / h

    assert h == Histogram([x,y], 2/ones, (2*2)/ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = h.to("cm", update=False, copy=False)
    h = 2 / h

    assert h == Histogram([x,y], 2/ones, (2*2)/ones, labels = ['x','y'], unit="1/cm")

    h = deepcopy(h0)
    h = h + ones

    assert h == Histogram([x,y], 2*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = 1 + h

    assert h == Histogram([x,y], 2*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = 1 - h

    assert h == Histogram([x,y], 0*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = h + list(list(z) for z in ones)

    assert h == Histogram([x,y], 2*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = h + COO.from_numpy(ones)

    assert h == Histogram([x,y], 2*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = h * u.Quantity(2*ones, unit="cm")

    assert h == Histogram([x,y], 2*ones * u.Unit("cm"), 4 * ones * u.Unit("cm^2"), labels = ['x','y'])

    h = deepcopy(h0)
    h = h * u.Unit("cm")

    assert h == Histogram([x,y], ones * u.Unit("cm"), ones * u.Unit("cm^2"), labels = ['x','y'])

    h = deepcopy(h0)
    h += h0

    assert h == Histogram([x,y], 2*ones, 2*ones, labels = ['x','y'])

    h = deepcopy(h0)
    h *= 2*h0

    assert h == Histogram([x,y], 2*ones, 8*ones, labels = ['x','y'])

    hz = Histogram([x,y], ones, labels = ['x','y']) # no sumw2

    h = deepcopy(h0)
    h = h + hz

    assert h == Histogram([x,y], 2*ones, ones, labels = ['x','y'])

    h = deepcopy(h0)
    hz = hz + h
    assert hz == Histogram([x,y], 2*ones, labels = ['x','y'])

    h = deepcopy(h0)
    h += h0
    h -= h0

    # Errors grow since histograms are assumed independent
    assert h == Histogram([x,y], ones, 3*ones, labels = ['x','y'])

    h = h + h0
    assert h == Histogram([x,y], 2*ones, 4*ones, labels = ['x','y'])

    h = h - h0
    assert h == Histogram([x,y], ones, 5*ones, labels = ['x','y'])

    h = deepcopy(h0)
    h = -h0

    assert h == Histogram([x,y], -ones, ones, labels = ['x','y'])

    # type changes -- ensure that types combine as expected, and that
    # sumw2 type always follows contents type
    h0 = Histogram([x,y], ones, ones, dtype=np.float32, labels = ['x','y'])

    h = deepcopy(h0)
    h += ones
    assert h.dtype == np.float32 and h.sumw2.dtype == np.float32

    h = deepcopy(h0)
    h *= ones
    assert h.dtype == np.float32 and h.sumw2.dtype == np.float32

    h = h0 + ones # promotes result to 64-bit
    assert h.dtype == np.float64 and h.sumw2.dtype == np.float64

    h = h0 * ones # promotes result to 64-bit
    assert h.dtype == np.float64 and h.sumw2.dtype == np.float64

    h1 = h0.astype(np.float64)

    h = deepcopy(h0)
    h += h1
    assert h.dtype == np.float32 and h.sumw2.dtype == np.float32

    h = deepcopy(h0)
    h *= h1
    assert h.dtype == np.float32 and h.sumw2.dtype == np.float32

    h = h0 + h1 # promotes result to 64-bit
    assert h.dtype == np.float64 and h.sumw2.dtype == np.float64

    h = h0 * h1 # promotes result to 64-bit
    assert h.dtype == np.float64 and h.sumw2.dtype == np.float64

    h = 2./h0 # rtruediv w/scalar does not promote result
    assert h.dtype == np.float32 and h.sumw2.dtype == np.float32

    # Sparse
    h0 = Histogram(np.linspace(0,10,30), sparse = True)
    h1 = Histogram(np.linspace(0,10,30), sparse = True)

    h0.fill(np.random.uniform(0,10,1000))
    h1.fill(np.random.normal(5,1,1000))

    h = h0*h1

    assert Histogram(np.linspace(0,10,30),
                     h0.full_contents*h1.full_contents) == h

    # DOK format operand does not pollute a sparse Histogram
    other = h1.contents.asformat('dok')
    h = h0 * other
    assert isinstance(h.contents, COO)

    # comparison of dense Histogram
    h = Histogram(np.linspace(0, 10, 30))
    h += 1

    assert np.all(h >  0)
    assert np.all(h >= 1)
    assert np.all(h <  2)
    assert np.all(h <= 1)

    # comparison of non-unit-bearing histogram
    # with dimensionless, unscaled Quantity should
    # not fail
    assert np.all(h <= 1*u.dimensionless_unscaled)

    # comparison of unit-bearing histogram
    # with Quantity should honor latter's units
    h = h.to(unit="cm", update=False)
    assert np.all(h <= 1*u.Unit("cm"))

    h = h.to(unit="mm")
    assert np.all(h <= 1*u.Unit("cm"))

    with pytest.raises(ValueError):
        np.all(h > 1*u.Unit("g")) # non-conformable units

    with pytest.raises(ValueError):
        np.all(h > 1) # cannot compare units to non-units

    # comparison of sparse Histogram
    h = Histogram(np.linspace(0, 10, 30), sparse=True)
    h += 1

    assert np.all(h >  0)
    assert np.all(h >= 1)
    assert np.all(h <  2)
    assert np.all(h <= 1)

    # comparison of non-unit-bearing histogram
    # with dimensionless, unscaled Quantity should
    # not fail
    assert np.all(h <= 1*u.dimensionless_unscaled)

    # comparison of unit-bearing histogram
    # with Quantity should honor latter's units
    h = h.to(unit="cm", update=False)
    assert np.all(h <= 1*u.Unit("cm"))

    h = h.to(unit="mm")
    assert np.all(h <= 1*u.Unit("cm"))

    with pytest.raises(ValueError):
        np.all(h > 1*u.Unit("g")) # non-conformable units

    with pytest.raises(ValueError):
        np.all(h > 1) # cannot compare units to non-units

def test_histogram_operator_units():

    ones = np.ones([nbinsx+2, nbinsy+2])

    h0 = Histogram([x,y], ones*u.cm, labels = ['x','y'])

    h1 = Histogram([x,y], ones*u.m, labels = ['x','y'])

    h2 = h0 + h1

    assert np.all(h2.full_contents == ones*u.cm + 100*ones*u.cm)

    h2 = h0 * h1

    assert np.all(h2.full_contents == ones*u.cm * 100*ones*u.cm)

    # neg should preserve units
    hu = Histogram([x,y], ones, ones, unit="cm", labels = ['x','y'])
    h = -hu

    assert h == Histogram([x,y], -ones, ones, unit="cm", labels = ['x','y'])

    # compare a dimensionless bare unit to a unitless Histogram
    hd = Histogram([x,y], 2*ones, labels = ['x','y'])
    d = hd > u.dimensionless_unscaled

    assert np.all(d)

    # compare a dimensionless quantity to a unitless Histogram
    d = hd >  1 * u.dimensionless_unscaled

    assert np.all(d)

def test_histogram_broadcasting():

    h = Histogram([x, y, z])

    assert h.expand_dims(x, 0).shape == (len(x), 1, 1)

    assert h.broadcast(x[1:], 0).shape == (nbinsx, nbinsy, nbinsz)

    xs = COO.from_numpy(x)

    assert h.expand_dims(xs, 0).shape == (len(xs), 1, 1)

    assert h.broadcast(xs[1:], 0).shape == (nbinsx, nbinsy, nbinsz)

def test_histogram_interpolation():

    def regular_test_case(ndims, size):
        """Compute a test case consisting of a Histogram, a set of values
        to interpolate, and the expected result.  The Histogram has
        dimension ndims and has size bins on each axis.  It's a
        regularly-spaced grid, where each bin's value is the sum of
        its coordinates.  We interpolate halfway between each two bins
        in every dimension (so, at (size-1)^ndims points), and at
        and beyond the upper and lower extreme corners of the Histogram.

        The returned arrays of values and results are themselves
        multidimensional (even for 1D case, which adds a single
        length-1 axis), which tests the ability of interp() to handle
        complex shapes for the input values.

        This is not a particularly complex interpolation task, as
        the grid is regular, and the interpolation points are halfway
        between the bin centers, but it does test basic functionality,
        corner cases, and values shape support.

        Note that values MUST be a single array if 1D or a tuple of
        arrays if >= 2D; we cannot return a unituple with a single array
        for the 1D case. interp() on a 1D histogram interprets a unituple
        containing only one array A to be a single 2D array-like of shape
        (1,) + A.shape.  This is the price we pay for trying to accept
        values in many different forms (scalars, array-likes of any shape,
        etc.).

        """

        # size regularly-spaced bins on an axis
        edges = np.linspace(0 - 0.5, size - 0.5, size+1)
        A = np.arange(0, size, dtype=np.float64) # bin centers

        # each entry of H is equal to the sum of its coordinates
        axes = (A,)*ndims
        contents = np.add.reduce(np.broadcast_arrays(*np.ix_(*axes)))

        H = Histogram((edges,)*ndims, contents=contents)

        # generate values halfway between each two centers on each axis
        C = A[:-1]
        values = np.meshgrid(*(C+0.5,)*ndims)

        # interpolating at points C should yield the values in contents
        # (i.e., the sum of coordinates of the lower-corner bin)
        # plus 0.5 times the number of dimensions.
        results = contents[(slice(0,-1),)*ndims] + 0.5*ndims

        # corner values in each dim are either at or beyond the center
        # of the lowest and highest bins on each axis.  They should
        # be clamped to that lowest/highest center.
        corner_values = (np.array([-1, 0, size - 1, size]),) * ndims
        corner_results = np.array([0, 0, ndims*(size-1), ndims*(size-1)])

        if ndims == 1:
            values  = np.asarray(values)  # extra length-1 axis
            results = np.asarray([results])
            corner_values = np.asarray(corner_values)
            corner_results = np.asarray([corner_results])

        return (H, values, results, corner_values, corner_results)


    h, v, r, cv, cr = regular_test_case(1, 10) # 1D case
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)
    h = h.to_sparse()
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)

    h, v, r, cv, cr = regular_test_case(2, 10) # 2D case
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)
    h = h.to_sparse()
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)

    h, v, r, cv, cr = regular_test_case(3, 10) # 3D case
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)
    h = h.to_sparse()
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)

    h, v, r, cv, cr = regular_test_case(4, 10) # 4D case
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)
    h = h.to_sparse()
    assert h.interp(v) == approx(r)
    assert h.interp(cv) == approx(cr)

    # remaining tests exercise scalar input, different axis scales,
    # nonuniform grids, and values not halfway between centers -- but
    # only for one and two dimensions and simple values shapes.

    h = Histogram([np.linspace(-0.5,5.5,7),
                   np.linspace(-0.5,3.5,5)],
                  np.repeat([range(0,4)],6, axis=0))

    assert h.interp(5,2.6) == 2.6

    h = Histogram([np.linspace(-0.5,3.5,5),
                   np.linspace(-0.5,5.5,7)],
                  np.repeat(np.transpose([range(0,4)]), 6, axis=1))

    assert h.interp(2.6, 5) == 2.6

    h = Histogram([np.linspace(-0.5,3.5,5),
                   np.linspace(-0.5,5.5,7)],
                  (np.repeat(np.transpose([range(0,4)]), 6, axis=1)
                   * np.repeat([range(0,6)],4, axis=0)),
                  dtype = float)

    assert h.interp(2,3) == 6
    assert h.interp(2,2.5) == 5
    assert h.interp(1.5,2.5) == 3.75

    assert arr_eq(h.interp([2.,2.,1.5],[3.,2.5,2.5]), [6.  , 5.  , 3.75])

    contents = (np.repeat(np.transpose([range(0,4)]), 6, axis=1)
                * np.repeat([range(0,6)],4, axis=0))
    contents[contents == 0] = 1 # don't allow zeros in contents for log

    h = Histogram([10**np.linspace(-0.5,3.5,5),
                   10**np.linspace(-0.5,5.5,7)],
                  contents,
                  axis_scale='log')

    # log-domain interpolation should return geometric mean when
    # interpolated point is halfway between two bin centers
    assert h.interp(10**2, 10**3, kind="log") == approx(6)
    assert h.interp(10**2, 10**2.5, kind="log") == approx(np.sqrt(4*6))
    assert h.interp(10**1.5, 10**2.5, kind="log") == approx(np.power(2*4*3*6, 0.25))

    # test same, but with units
    h = h.to(unit=u.cm, update=False)

    r = h.interp(10**2, 10**3, kind="log")
    assert r.value == approx(6) and r.unit == u.cm
    r = h.interp(10**2, 10**2.5, kind="log")
    assert r.value == approx(np.sqrt(4*6)) and r.unit == u.cm
    r = h.interp(10**1.5, 10**2.5, kind="log")
    assert r.value == approx(np.power(2*4*3*6, 0.25)) and r.unit == u.cm

    c = np.linspace(0.5,9.5,10)
    c[0] = 0
    h = Histogram(np.linspace(0,10,11), c)
    h.axes[0].axis_scale = 'symmetric'

    assert h.interp(0.5) == 0.5

    # test interpolation on sparse matrices in the presence of units.
    # The interpolated results should have the same unit as the
    # Histogram.

    h = Histogram([np.linspace(-0.5,5.5,7),
                   np.linspace(-0.5,3.5,5)],
                  np.repeat([range(0,4)],6, axis=0),
                  sparse=True, unit=u.cm)

    assert h.interp(5,2.6) == 2.6*u.cm

    h = Histogram([np.linspace(-0.5,3.5,5),
                   np.linspace(-0.5,5.5,7)],
                  np.repeat(np.transpose([range(0,4)]), 6, axis=1),
                  sparse=True, unit=u.cm)

    assert h.interp(2.6, 5) == 2.6*u.cm

    h = Histogram([np.linspace(-0.5,3.5,5),
                   np.linspace(-0.5,5.5,7)],
                  (np.repeat(np.transpose([range(0,4)]), 6, axis=1)
                   * np.repeat([range(0,6)],4, axis=0)),
                  sparse=True, unit=u.cm)

    assert h.interp(2,3) == 6*u.cm
    assert h.interp(2,2.5) == 5*u.cm
    assert h.interp(1.5,2.5) == 3.75*u.cm

    c = np.linspace(0.5,9.5,10)
    c[0] = 0
    h = Histogram(np.linspace(0,10,11), c,
                  sparse=True, unit=u.cm)
    h.axes[0].axis_scale = 'symmetric'

    assert h.interp(0.5) == 0.5*u.cm

def test_histogram_interpolation_healpix():

    from astropy.coordinates import UnitSphericalRepresentation

    h = Histogram([np.arange(0, 10), HealpixAxis(nside=128)])

    # Fill with product of bin center of first axis times longitude
    # (radians) of bin center of second axis
    h[:] = h.axes[0].centers[:, None] * \
        h.axes[1].pix2ang(range(h.axes[1].npix))[1][None, :]

    x_value = 4
    y_pos = UnitSphericalRepresentation(lat=30 * u.deg, lon=20 * u.deg)

    assert h.interp(x_value, y_pos) == approx(x_value *
                                              y_pos.lon.to_value(u.rad))

def test_histogram_numpy_functions():

    contents = np.arange(nbinsx)

    h = Histogram(x, contents)

    # __array__
    arr = np.array(h)
    assert arr_eq(arr, h.contents)

    # note that for numpy <= 2.0, __array__ is
    # not called with copy=True even in this case,
    # so we are forced to call it explicitly to test

    #arr = np.array(h, copy=True)
    arr == h.__array__(copy=True)
    assert arr_eq(arr, h.contents)

    arr = np.array(h, dtype=int)
    assert arr_eq(arr, h.contents.astype(int))

    # __array_ufunc__
    assert arr_eq(np.sin(h), np.sin(contents))

    # Remove if a general ufunc is implemented
    with pytest.raises(NotImplementedError):
        np.maximum(h, 5)

    # __array_function__
    assert arr_eq(np.sum(h), np.sum(contents))

    # Remove if a general func is implemented
    with pytest.raises(NotImplementedError):
        np.dot(h, 5)

    # __array_function__
    d = np.ndim(h)

    assert d == 1

    s = np.sum(h)

    assert s == np.sum(contents)


    h = Histogram(x, contents, unit=u.cm)

    # __array__ with units
    arr = np.array(h, subok=True) # unit preserved

    assert arr_eq(arr, h.contents)

    # note that for numpy <= 2.0, __array__ is
    # not called with copy=True even in this case,
    # so we are forced to call it explicitly to test

    #arr = np.array(h, subok=True, copy=True)
    arr == h.__array__(copy=True)
    assert arr_eq(arr, h.contents)

    arr = np.array(h, dtype=int, subok=True)
    assert arr_eq(arr, h.contents.astype(int))

    # __array_ufunc__ with units
    assert arr_eq(np.floor(h + 2.5*u.cm), np.floor((contents + 2.5)*u.cm))

    # __array_function__ with units
    d = np.ndim(h)

    assert d == 1

    s = np.sum(h)

    # assumes unit is *preserved*
    assert s == np.sum(contents) * u.cm

def test_histogram_sanity_checks():
    """
    Check expected exceptions
    """

    # Bad axes shape
    with pytest.raises(Exception):
        Histogram(edges = np.array([[[1,2,3,4],[1,2,3,4]]]))

    with pytest.raises(Exception):
        Histogram(edges = 5)

    with pytest.raises(Exception):
        Histogram(edges = [])

    with pytest.raises(Exception):
        Histogram(edges = [5])

    with pytest.raises(Exception):
        Histogram(edges = [[5,6],[5]])

    # Bad labels
    with pytest.raises(Exception):
        Axes([1,2,3,4], labels=['x','y'])

    with pytest.raises(Exception):
        Axes([range(10), range(20)], labels=['x','x'])

    # Axes - contents dimension mismatch
    with pytest.raises(ValueError):
        Histogram(edges = [0,1,2,3], contents = np.ones((2,2)))

    # Axes - sumw2 dimension mismatch
    with pytest.raises(ValueError):
        Histogram(edges = [0,1,2,3], sumw2 = np.ones((2,2)))

    # Axes - contents size mismatch
    with pytest.raises(Exception):
        Histogram(edges = [0,1,2,3], contents = [0,0])

    # Not strictly monotically increasing axes
    with pytest.raises(Exception):
        Histogram(edges = [0,1,2,3,3,4,5])

    with pytest.raises(Exception):
        Histogram(edges = [0,1,2,3,4,3,5])

    # Out of bounds
    h = Histogram(edges = [0,1,2,3], labels=['x'])
    with pytest.raises(Exception):
        h[-2]

    with pytest.raises(Exception):
        h[h]

    with pytest.raises(Exception):
        h[h.end+2]

    with pytest.raises(Exception):
        h[-2:h.end+2]

    with pytest.raises(Exception):
        h[:h.end+2]

    with pytest.raises(Exception):
        h[[-2,-1,1]]

    with pytest.raises(Exception):
        h[[-1,1,6]]

    with pytest.raises(IndexError):
        h[1,2] # too many indices

    with pytest.raises(Exception):
        h.axes[1]

    with pytest.raises(Exception):
        h.axes['y']


    h = Histogram(edges = [0,1,2,3])

    # Filling and find bin dimensions
    with pytest.raises(Exception):
        h.find_bin(1,2) # 2 inputs, 1 dim

    h.fill(1, weight = 2) # Correst, weight by key
    with pytest.raises(Exception):
        h.fill(1,2) # 2 inputs, 1 dim.

    # Project
    h = Histogram(edges = [0,1,2,3])
    with pytest.raises(ValueError):
        h.project_out(0) # Can't project away all dimensions

    h = Histogram(edges = [range(0,10), range(0,20)])
    with pytest.raises(ValueError):
        h.project([0,0]) # Axes repeat

    h = Histogram(edges = [range(0,10), range(0,20)])
    with pytest.raises(KeyError):
        h.project(2) # Axis out of bounds

    # Slicing
    h = Histogram(edges = [range(0,10+1), range(0,20+1)], track_overflow=True)

    with pytest.raises(IndexError):
        h.slice[-1] # Slice returning only underflow

    with pytest.raises(IndexError):
        h.slice[10] # Slice returning only overflow

    with pytest.raises(TypeError):
        h.slice[[1,3,5],[2,4,6]] # Slice with an invalid index type

    with pytest.raises(IndexError):
        h.slice[6:3] # Backward slice not supported

    with pytest.raises(IndexError):
        h.slice[::2,:]   # slicing with a stride

    with pytest.raises(IndexError):
        h.slice[0:0,:]  # slicing with an empty dimension

    # indexing with an ellipsis not at the end
    with pytest.raises(IndexError):
        h[1,...,2]

    # invalid unit conversions
    h = Histogram(edges = [range(0,10+1), range(0,20+1)], unit=None)

    with pytest.raises(TypeError):
        h.to(unit="cm") # cannot add unit to unitless Histogram without update=False

    # Operators
    h = Histogram(edges = [range(0,10+1), range(0,20+1)])
    h2 = Histogram(edges = [range(0,10), range(0,20)])
    h3 = Histogram(edges = [range(0,10)])

    with pytest.raises(Exception):
        h *= [1,2]

    with pytest.raises(ValueError):
        h += h2 # axes mismatch

    with pytest.raises(ValueError):
        h += h3 # number of axes mismatch

    with pytest.raises(ValueError):
        h = [[1,2],[3,4]] / h # rtruediv with non-scalar

def test_histogram_fit():

    # 1D
    fit_fun = lambda x, N, x0: N * np.exp(-(x - x0) ** 2 / 2)

    h = Histogram(np.linspace(-5, 5))

    h[:] = fit_fun(h.axes[0].centers, 1, 1.5)

    popt, pcov = h.fit(fit_fun)

    assert arr_eq(popt, [1, 1.5])

    # 2D
    fit_fun = lambda x, N, x0, y0: N * np.exp(-((x[0] - x0) ** 2 + (x[1] - y0) ** 2) / 2)

    h = Histogram([np.linspace(-5, 5), np.linspace(-5, 5)])

    x = np.meshgrid(h.axes[0].centers, h.axes[1].centers,
                    indexing='ij')

    h[:] = fit_fun(x, 1, 1.5, 2)

    popt, pcov = h.fit(fit_fun)

    assert arr_eq(popt, [1, 1.5, 2])

    # Units
    fit_fun = lambda x, N, x0: N * np.exp(-(x - x0) ** 2 / 2)

    h = Histogram(np.linspace(-5, 5), unit = u.s)

    h[:] = fit_fun(h.axes[0].centers, 1, 1.5) * u.s

    popt, pcov = h.fit(fit_fun)

    assert arr_eq(popt, [1, 1.5])

    # Sparse
    fit_fun = lambda x, N, x0: N * np.exp(-(x - x0) ** 2 / 2)

    h = Histogram(np.linspace(-5, 5), sparse = True)

    h[:] = np.random.poisson(fit_fun(h.axes[0].centers, 100, 1.5))

    popt, pcov = h.fit(fit_fun)

    assert  popt[0] == approx(100, abs = 5*2.5)  # 5sigma
    assert  popt[1] == approx(1.5, abs = 5*0.025) # 5sigma

    # Errors
    with pytest.raises(ValueError):
        h.fit(fit_fun, lo_lim=-6)

    with pytest.raises(ValueError):
        h.fit(fit_fun, hi_lim=6)

    fit_fun = lambda x, N, x0: N * np.exp(-(x - x0) ** 2 / 2)

    h = Histogram([-5,5], sparse=True)

    h[:] = fit_fun(h.axes[0].centers, 100, 1.5)

    with pytest.raises(RuntimeError):
        h.fit(fit_fun)

def test_histogram_readwrite(tmp_path):

    import hashlib
    import time

    h = Histogram([1,2,3,4,5], unit=u.cm, sumw2=True)
    h.write(tmp_path / "garbage_file", overwrite=True)

    with pytest.raises(ValueError):
        h.write(tmp_path / "garbage_file", overwrite=False) # cannot overwrite

    hh = Histogram.open(tmp_path / "garbage_file")
    assert(h == hh)

    h = Histogram(Axis([1,2,3,4,5], unit=u.g, label='Foo'),
                  unit=u.cm, sumw2=True, sparse=True)
    h.write(tmp_path / "garbage_file", overwrite=True)

    hh = Histogram.open(tmp_path / "garbage_file")
    assert(h == hh)

    axis = HealpixAxis(nside = 128, coordsys = 'icrs')
    h = Histogram(axis, unit=u.cm, sumw2=True, sparse=True)
    h.write(tmp_path / "garbage_file", overwrite=True)

    hh = Histogram.open(tmp_path / "garbage_file")
    assert(h == hh)

    # verify that writing a Hsitogram twice yields a reproducible result
    # (i.e., no hidden HDF5 timestamps)

    h = Histogram([axis, [1,2,3]], unit=u.g, labels=['Foo', 'Bar'], sumw2=True)
    h.write(tmp_path / "garbage_file1", overwrite=True)
    time.sleep(1)
    h.write(tmp_path / "garbage_file2", overwrite=True)

    d1 = hashlib.sha256(open(tmp_path / "garbage_file1", "rb").read())
    d2 = hashlib.sha256(open(tmp_path / "garbage_file2", "rb").read())

    assert d1.hexdigest() == d2.hexdigest()

    # writing and reading subclass of Histogram

    class MyHist(Histogram):

        def __init__(self, edges):
            super().__init__(edges)
            self.foo = 3

        def _write(self, file, group_name):

            group = super()._write(file, group_name)

            extra_group = group.create_group('extra')
            extra_group.attrs['foo'] = self.foo

            return group

        @classmethod
        def _open(cls, group):

            new = super()._open(group)

            extra_group = group['extra']
            foo = extra_group.attrs['foo']

            new.foo = foo

            return new

        def __eq__(self, other):
            return self.foo == other.foo and super().__eq__(other)

    h = MyHist([1,2,3,4,5])
    h.write(tmp_path / "garbage_file", overwrite=True)

    hh = MyHist.open(tmp_path / "garbage_file")
    assert h == hh
