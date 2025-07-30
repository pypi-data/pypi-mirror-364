from histpy import HealpixAxis

from astropy.coordinates import SkyCoord, UnitSphericalRepresentation
import astropy.units as u

from numpy import array_equal as arr_eq

import numpy as np

import pytest

def test_healpix_axis():

    def lonlat_to_thetaphi(lon, lat):
        if not (np.isscalar(lon) and np.isscalar(lat)):
            lon = np.asarray(lon)
            lat = np.asarray(lat)

        return np.deg2rad(90 - lat), np.deg2rad(lon)

    # initialization

    # init with nside, default edge list
    axis = HealpixAxis(nside = 4, label='Foo')
    assert len(axis.edges) == 12*(4**2) + 1
    assert axis.label == 'Foo'

    # init with edge list, infer nside
    axis = HealpixAxis(edges = np.arange(12*(4**2) + 1))
    assert axis.nside == 4

    # initi with both nside and edges -- latter may
    # be a subset of all pixels
    axis = HealpixAxis(nside = 4, edges=[5,6,7,8])
    assert len(axis.edges) == 4

    with pytest.raises(ValueError):
        # must specify nside or edges
        HealpixAxis(coordsys = 'icrs',
                    label='Foo')

    with pytest.raises(ValueError):
        # edge array without nside must be of a
        # size corresponding to valid nside
        HealpixAxis(edges = [0, 1, 2, 3],
                    coordsys = 'icrs',
                    label='Foo')

    with pytest.raises(ValueError):
        # edges must be integers
        HealpixAxis(edges = np.arange(12+1, dtype=np.float64),
                    coordsys = 'icrs',
                    label='Foo')

    with pytest.raises(ValueError):
        # edges must be within range of pixels
        HealpixAxis(nside=1,
                    edges = np.arange(13+1),
                    coordsys = 'icrs',
                    label='Foo')

    # find_bin, single input
    axis = HealpixAxis(nside = 128,
                       coordsys = 'icrs')

    assert axis.find_bin(SkyCoord(ra = 1*u.deg, dec = 89.999*u.deg)) == 0
    assert axis.find_bin(UnitSphericalRepresentation(lon=1*u.deg,lat=89.999*u.deg)) == 0
    assert axis.find_bin(1, 89.999, lonlat=True) == 0 # (lon, lat) in degrees
    assert axis.find_bin(*lonlat_to_thetaphi(1, 89.999)) == 0 # (co-lat, long) in radians
    assert axis.find_bin(0) == 0 # HEALPix pixel
    assert axis.find_bin(np.array(0)) == 0 # strip zero-dim array

    # find_bin with arrays of length 1
    assert arr_eq(axis.find_bin(SkyCoord(ra=[1]*u.deg, dec=[89.999]*u.deg)),
                  [0])
    assert axis.find_bin(UnitSphericalRepresentation(lon=[1]*u.deg,lat=[89.999]*u.deg)) == 0
    assert arr_eq(axis.find_bin([SkyCoord(ra=1*u.deg, dec=89.999*u.deg)]),
                  [0])
    assert arr_eq(axis.find_bin(*lonlat_to_thetaphi([1], [89.999])), # lonlat defaults False
                  [0])
    assert arr_eq(axis.find_bin([1], [89.999], lonlat=True),
                  [0])
    assert arr_eq(axis.find_bin([0]), [0])

    # find_bin with arrays of length > 1
    assert arr_eq(axis.find_bin(SkyCoord(ra=[1,-1]*u.deg, dec=89.999*u.deg)),
                  [0,3])
    assert arr_eq(axis.find_bin(UnitSphericalRepresentation(lon=[1,-1]*u.deg, lat=89.999*u.deg)),
                  [0,3])
    assert arr_eq(axis.find_bin([SkyCoord(ra = 1*u.deg, dec = 89.999*u.deg),
                                 SkyCoord(ra = -1*u.deg, dec = 89.999*u.deg)]),
                  [0, 3])
    assert arr_eq(axis.find_bin([UnitSphericalRepresentation(lon=1*u.deg, lat=89.999*u.deg),
                                 UnitSphericalRepresentation(lon=-1*u.deg, lat=89.999*u.deg)]),
                  [0, 3])
    assert arr_eq(axis.find_bin(*lonlat_to_thetaphi([1,-1], [89.999, 89.999])), # lonlat defaults False
                  [0,3])
    assert arr_eq(axis.find_bin([1,-1], [89.999, 89.999], lonlat=True),
                  [0,3])
    assert arr_eq(axis.find_bin([0,3]), [0,3])

    # interpolate with single SkyCoord
    pos0 = SkyCoord(ra=0 * u.deg, dec=90 * u.deg)
    pix, weights = axis.interp_weights(pos0)
    assert np.array_equal(np.sort(pix), [0,1,2,3])
    assert np.allclose(weights, 0.25)

    # interpolate with single theta/phi
    pos0 = lonlat_to_thetaphi(0, 90)
    pix, weights = axis.interp_weights(*pos0) # lonlat defaults False
    assert np.array_equal(np.sort(pix), [0,1,2,3])
    assert np.allclose(weights, 0.25)

    # interpolate with single lon/lat
    pos0 = (0, 90)
    pix, weights = axis.interp_weights(*pos0, lonlat=True)
    assert np.array_equal(np.sort(pix), [0,1,2,3])
    assert np.allclose(weights, 0.25)

    # interpolate with single pixel
    pix, weights = axis.interp_weights(0)
    assert np.sort(pix)[0] == 0
    np.allclose(weights, [1, 0, 0, 0])

    # interpolate with multiple SkyCoords
    pos0 = SkyCoord(ra=0 * u.deg, dec=90 * u.deg)
    pos1 = SkyCoord(ra=0 * u.deg, dec=-90 * u.deg)
    pix, weights = axis.interp_weights([pos0,pos1])
    assert np.array_equal(pix, [[1, 196607], [2, 196604], [3, 196605], [0, 196606]])
    assert np.allclose(weights, 0.25)
    assert pix.shape == (4,2)
    assert weights.shape == (4,2)

    # interpolate with multiple theta/phi
    pos0 = [0, 0]
    pos1 = [90, -90]
    pix, weights = axis.interp_weights(*lonlat_to_thetaphi(pos0, pos1)) # lonlat defaults False
    assert np.array_equal(pix, [[1, 196607], [2, 196604], [3, 196605], [0, 196606]])
    assert np.allclose(weights, 0.25)
    assert pix.shape == (4,2)
    assert weights.shape == (4,2)

    # interpolate with multiple lon/lat
    pos0 = [0, 0]
    pos1 = [90, -90]
    pix, weights = axis.interp_weights(pos0, pos1, lonlat=True)
    assert np.array_equal(pix, [[1, 196607], [2, 196604], [3, 196605], [0, 196606]])
    assert np.allclose(weights, 0.25)
    assert pix.shape == (4,2)
    assert weights.shape == (4,2)

    # interpolate with multiple pixels
    pos0 = [0, 196607]
    pix, weights = axis.interp_weights(pos0, lonlat=True)
    assert np.allclose(weights, (pos0 == pix).astype(float))
    assert pix.shape == (4,2)
    assert weights.shape == (4,2)

    # interpolate with multiple pixels, no axis coord system
    axis2 = HealpixAxis(nside = 128, # no coordinate system
                        label='Foo')
    pos0 = [0, 196607]
    pix, weights = axis2.interp_weights(pos0, lonlat=True)
    assert np.allclose(weights, (pos0 == pix).astype(float))
    assert pix.shape == (4,2)
    assert weights.shape == (4,2)


    # verify that copy() preserves subclass data
    b = axis.copy()
    assert axis == b

    # verify that replace_edges() preserves subclass data
    old_edges = axis.edges
    new_edges = old_edges[::2]
    b = axis.replace_edges(new_edges)
    b = b.replace_edges(old_edges)
    assert axis == b

    # HealpixAxis does not permit arithmetic
    with pytest.raises(AttributeError):
        c = b * 2

    # HealpixAxis does not permit arithmetic
    with pytest.raises(AttributeError):
        b *= 2

    b = axis[10:20] # specifies *bins*
    assert np.array_equiv(b.edges, axis.edges[10:21]) # one more edge than bins
    # not sure how to test that HealpixMap part is same
