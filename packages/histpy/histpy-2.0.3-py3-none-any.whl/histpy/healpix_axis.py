from .axis import Axis

from mhealpy import HealpixBase

import numpy as np

from astropy.coordinates import (SkyCoord,
                                 BaseRepresentation,
                                 UnitSphericalRepresentation)
from astropy.coordinates import concatenate_representations
from astropy.coordinates import concatenate as concatenate_coords

import astropy.units as u

class HealpixAxis(Axis, HealpixBase):
    """
    2D spherical axis using a HEALPix grid

    Args:
        nside (int):
          nside for grid. If not specified, inferred from length of `edges',
          which must then be the consecutive integers [0 .. 12*(nside**2)].
        scheme (str):
          Healpix scheme. One of 'RING' (default) or 'NESTED'.
        edges (array):
          List of bin edges in terms of HEALPix pixels. Must be integers;
          may be subset of grid if nside was specified.  Defaults to
          [0 .. 12*(nside**2)], i.e., one bin per pixel in the grid.
        coordsys (BaseFrameRepresentation or str):
          Instrinsic coordinates of the map. One of ‘G’ (Galactic), ‘E’ (Ecliptic) ,
          ‘C’ (Celestial = Equatorial) or any other coordinate frame recognized
          by astropy.
    """

    def __init__(self,
                 nside = None,
                 scheme='ring',
                 edges=None,
                 coordsys = None,
                 *args, **kwargs):

        if nside is None and edges is not None:

            edges = np.asarray(edges)

            npix = len(edges)-1

            if not np.array_equal(edges, np.arange(npix + 1)):
                raise ValueError("If you don't specify nside, edges must include all pixels. Use integers.")

            HealpixBase.__init__(self,
                                 npix = npix,
                                 scheme = scheme,
                                 coordsys = coordsys)

        else:

            if nside is None:
                raise ValueError("Specify either nside or edges")

            HealpixBase.__init__(self,
                                 nside = nside,
                                 scheme = scheme,
                                 coordsys = coordsys)

            if edges is None:
                # Default to full map
                edges = np.arange(self.npix + 1)

        super().__init__(edges, *args, **kwargs)

        # additional sanity checks specific to HealpixAxis edges
        self._validate_healpix_edges(self.edges)

    def _copy(self, edges=None, copy_edges=True):
        """Make a deep copy of a HealpixAxis, optionally
        replacing edge array. (The superclass's _copy
        method handles edge replacement.)
        """

        new = super()._copy(edges, copy_edges)

        if edges is not None: # extra sanity checks
            self._validate_healpix_edges(new._edges)

        HealpixBase.__init__(new,
                             nside = self.nside,
                             scheme = self.scheme,
                             coordsys = self.coordsys)

        return new

    def _validate_healpix_edges(self, edges):

        super()._validate_edges(edges)

        # Check it corresponds to pixels
        if edges.dtype.kind not in 'ui':
            raise ValueError("HeapixAxis needs integer edges")

        if edges[0] < 0 or edges[-1] > self.npix:
            raise ValueError("Edges must lie between 0 and total number of pixels")

    def __eq__(self, other):
        return super().__eq__(other) and self.conformable(other)

    def __getitem__(self, key):

        new = super().__getitem__(key)

        HealpixBase.__init__(new,
                             nside = self.nside,
                             scheme = self.scheme,
                             coordsys = self.coordsys)

        return new

    def find_bin(self, theta, phi=None, lonlat=False):
        """
        Find bin number on axis that corresponds to a given HEALPix pixel
        or set of coordinates.

        Args:
            If phi is None,
              + theta is one of
                - int or array-like of int
                    HEALPix pixel ID(s) (in scheme of axis)
                - SkyCoord, BaseRepresentation, or array-like of same
                    coordinates to be mapped onto HEALPix grid
              + lonlat is ignored
            If phi is not None,
              + theta, phi are both float or array-like of float,
                specifying raw coordinates to be mapped onto HEALPix grid
              + if lonlat is True, theta, phi are (lon, lat) in degrees;
                otherwise, they are (co-lat, lon) in radians

        Returns:
            int or array of int -- bins for each input value
        """

        if phi is None:
            value = self._standardize_skycoord_array(theta)

            if isinstance(value, (SkyCoord, BaseRepresentation)):
                # Transform first from coordinates to pixel
                value = self.ang2pix(value)

        else:
            value = self.ang2pix(theta=theta, phi=phi, lonlat=lonlat)

        return super().find_bin(value)

    def interp_weights(self, theta, phi=None, lonlat=False):
        """
        Return the 4 closest pixels on the two rings above and below
        the location and corresponding weights. Weights are provided
        for bilinear interpolation along latitude and longitude

        Find bin number on axis that corresponds to a given HEALPix pixel
        or set of coordinates.

        Args:
            If phi is None,
              + theta is one of
                - int or array-like of int
                    HEALPix pixel ID(s) (in scheme of axis); interpolation
                    coordinates correspond to pixel center(s)
                - SkyCoord, BaseRepresentation, or array-like of same
                    coordinates to interpolate.  When
              + lonlat is ignored
            If phi is not None,
              + theta, phi are both float or array-like of float,
                specifying raw coordinates to be interpolated onto HEALPix grid
              + if lonlat is True, theta, phi are (lon, lat) in degrees;
                otherwise, they are (co-lat, lon) in radians

        Returns:
          bins (int array):
              Array of bins to be interpolated
          weights (float array):
              Corresponding weights
        """

        if phi is None:
            value = self._standardize_skycoord_array(theta)

            if not isinstance(value, (SkyCoord, BaseRepresentation)):
                # input is HEALPix pixel(s) -- translate
                # to coords of pixel centers
                if self.coordsys is None:
                    lon, lat = self.pix2ang(value, lonlat = True)

                    value = UnitSphericalRepresentation(lon = lon*u.deg,
                                                        lat = lat*u.deg)

                else:
                    value = self.pix2skycoord(value)

            # interpolate provided coordinates onto HEALPix grid
            pixels, weights = self.get_interp_weights(value)

            return self.find_bin(pixels), weights

        else:
            # input is raw coordinates
            return self.get_interp_weights(theta=theta,
                                           phi=phi,
                                           lonlat=lonlat)

    def _standardize_skycoord_array(self, value):
        """
        Transform array-like of astropy's SkyCoords or
        BaseRepresentation to a single object with an array
        inside. Otherwise, leave value unchanged, except that we
        convert any zero-dimensional array to a scalar.
        """

        if isinstance(value, (np.ndarray, tuple, list)):

            if isinstance(value, np.ndarray) and value.ndim == 0:
                # zero-dimensional array -- extract single value
                value = value.item()

            elif isinstance(value[0], (SkyCoord, BaseRepresentation)):
                if len(value) == 1:
                    # cannot call concatenate() on array of length 1;
                    # instead, directly create a SkyCoord with an
                    # internal array of length 1.
                    value = np.atleast_1d(value[0])
                elif isinstance(value[0], SkyCoord):
                    value = concatenate_coords(value)
                else: # BaseRepresetnation
                    value = concatenate_representations(value)

        return value

    def _operation(self, other, operation):
        raise AttributeError("HealpixAxis doesn't support operations")

    def _ioperation(self, other, operation):
        raise AttributeError("HealpixAxis doesn't support operations")

    def _write(self, axes_group, name):

        """
        Save all needed information to recreate Axis into
        a HDF5 group.  Subclasses may override

        Returns: dataset holding axis
        """

        axis_set = super()._write(axes_group, name)

        axis_set.attrs['nside'] = self.nside
        axis_set.attrs['scheme'] = self.scheme

        if self.coordsys is not None:
            axis_set.attrs['coordsys'] = str(self.coordsys.name)

        return axis_set

    @classmethod
    def _open(cls, dataset):
        """
        Create HealpixAxis from HDF5 dataset
        """

        new = super()._open(dataset)

        nside = dataset.attrs['nside']
        scheme = dataset.attrs['scheme']

        coordsys = None
        if 'coordsys' in dataset.attrs:
            coordsys = dataset.attrs['coordsys']

        HealpixBase.__init__(new,
                             nside = nside,
                             scheme = scheme,
                             coordsys = coordsys)

        return new
