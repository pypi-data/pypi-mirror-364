import logging
logger = logging.getLogger(__name__)

import numpy as np

from sparse import SparseArray

import astropy.units as u

from .axis import Axis

class Axes:
    """
    Holds a list of axes.

    The operator :code:`Axes[key]` return a subset of these. Key can be either the
    index or the label. If the key is a single index, a single Axis object
    will be returned

    Args:
      edges (array or list of arrays or Axis):
        Definition of bin edges.
      labels (array of str equal to # of axes):
        Optionally label the axes for easier indexing.  Will override
        any existing labels on passed-in Axis objects
      axis_scale (str or array):
        Bin center mode e.g. `"linear"` or `"log"`.  See
        Axis.axis_scale. If not an array, all axes will have this
        mode.  Will override any existing mode on passed-in Axis
        objects
      copy_axes (bool):
        If True (default), Axis objects that are passed in as part of
        the 'axes' parameter will be copid unless axes is an Axes
        object that contains them.  If False, they will be used
        without copying. But we *always* copy Axis objects if __init__
        may change their labels or scales, regardless of how copy is
        set.
    """

    def __init__(self, axes, labels = None, axis_scale = None, copy_axes = True):

        # are we planning to mutate the Axis objects of this Axes object?
        mutate_axes = labels is not None or axis_scale is not None

        if isinstance(axes, Axes): # an existing Axes object

            if mutate_axes:
                # copy-on-write demands that we copy before mutating
                new_axes = [ a.copy() for a in axes._axes ]
            else:
                new_axes = axes._axes.copy() # shallow copy -- new list, same objects

        elif isinstance(axes, Axis): # a single Axis object

            # copy if user requests, or if we plan to mutate
            new_axes = [ axes.copy() if (copy_axes or mutate_axes) else axes ]

        elif np.isscalar(axes): # scalar, including strings and buffers

            raise TypeError("Input to Axes must be Axes, Axis, edge list, or iterable")

        else:
            # attempt to parse input as an iterable

            if len(axes) == 0:
                raise TypeError("Cannot create Axes object with zero axes")

            if isinstance(axes, u.Quantity) or all(np.isscalar(a) for a in axes):
                # an iterable of edges defining one Axis
                new_axes = [ Axis(axes) ]
            else:
                # iterable containing Axis objects or things we can convert to them
                new_axes = []
                for a in axes:
                    if isinstance(a, Axis):
                        # copy if user requests, or if we plan to mutate
                        new_axes.append( a.copy() if (copy_axes or mutate_axes) else a )
                    else:
                        new_axes.append(Axis(a))

        # override labels if nedeed
        if labels is not None:

            if np.isscalar(labels):
                labels = [ labels ]

            if len(labels) != len(new_axes):
                raise ValueError("Labels list must match number of axes")

            for a, label in zip(new_axes, labels):
                a.label = label

        # Override scales if nedeed
        if axis_scale is not None:

            if np.isscalar(axis_scale):
                axis_scale = len(new_axes) * [ axis_scale ]

            if len(axis_scale) != len(new_axes):
                raise ValueError("Scale list must match number of axes")

            for a, mode in zip(new_axes, axis_scale):
                a.axis_scale = mode

        self._axes = new_axes
        self._update_labels_index()

    def _update_labels_index(self):
        """
        Create an index mapping axis labels to indices in the axis list.
        In the process, validate that no label is repeated.
        """

        self._labels = {}

        for i, a in enumerate(self._axes):
            if a.label is not None: # skip axis with no label
                if self._labels.get(a.label) is not None:
                    raise ValueError("Axis labels can't repeat")
                self._labels[a.label] = i

    def copy(self):
        """
        Make a 'deep' copy of an Axes object.  We assume that Axis objects
        held by an Axes object are not mutable outside the class and
        are copy-on-write within it, so we are permitted to make a shallow
        copy of its axis list.
        """
        new = Axes.__new__(Axes)

        new._axes = self._axes.copy() # shallow copy
        new._labels = self._labels.copy()

        return new

    def __len__(self):
        return self.ndim

    def __iter__(self):
        return iter(self._axes)

    @property
    def ndim(self):
        """
        Number of axes
        """
        return len(self._axes)

    @property
    def shape(self):
        """
        Tuple with length of each axis
        """
        return tuple(a.nbins for a in self._axes)

    def label_to_index(self, key):
        """
        Map a key or list-like of keys to indices in the axis list.
        key may be an integer or label; labels are mapped to their
        corresponding integer indices.

        Args:
          key: integer, label string, list-like of same, or slice
               (the latter is mapped to a tuple of integers)

        Return:
          integer if key is scalar; otherwise, tuple of
          mapping results for each element of key
        """

        def map_item(key):
            if isinstance(key, (int, np.integer)):
                if key < 0 or key >= self.ndim:
                    raise KeyError(f"Index {key} >= "
                                   f"number of dims {self.ndim}")
                return key
            else:
                idx = self._labels.get(key) # assume it's a label
                if idx is None:
                    raise KeyError(f"Axis with label {key} not found")
                return idx

        if np.isscalar(key):
            return map_item(key)
        elif isinstance(key, slice):
            return tuple(range(*key.indices(self.ndim)))
        elif isinstance(key, (np.ndarray, list, tuple, range)):
              return tuple( map_item(k) for k in key )
        else:
              raise TypeError("Index list must be list-like of integers or labels")

    def __getitem__(self, key):
        """
        Get one or more axes by key.  Uses label_to_index() to determine
        which axes to return.

        Returns:
          single axis if key is scalar, or a new Axes object that is
          a view of the subset of requested Axis objects otherwise

        NB: the Axis objects returned by this function MUST NOT BE MODIFIED;
        they are potentially shared by other Axes objects.  Make a copy and
        write back the Axes objects if you need to modify them.
        """

        indices = self.label_to_index(key)

        if np.isscalar(indices):
            return self._axes[indices] # single axis
        else:
            # return a new Axes object that reuses component Axis objects
            return Axes([self._axes[i] for i in indices], copy_axes=False)

    def set(self, key, new, copy=True):
        """
        Replace one Axis of a Axes object. The new Axis must have the
        same number of bins as the axis it replaces, and it may not
        have the same label as an existing Axis other than the one
        we are replacing.

        Args:
          key: axis to replace (must be a SINGLE scalar index or label)
          new: an Axis object or something that can be converted to it
          copy: if True, always copy the new axis Axis; otherwise, copy
                only if needed.
        """
        key = self.label_to_index(key)

        if not np.isscalar(key):
            raise TypeError("can assign to only a single element of Axes at a time")

        if isinstance(new, Axis):
            new = new.copy() if copy else new
        else:
            new = Axis(new) # always copies

        old = self._axes[key]

        if new.nbins != old.nbins:
            raise ValueError("Can't assign new axis with different number of bins")
        elif new.label is not None:
            idx = self._labels.get(new.label)
            if idx is not None and idx != key:
                # some axis other than the one being replaced has the same key as new
                raise ValueError("New axis cannot have same label as existing axis")

        if old.label is not None:
            del self._labels[old.label]

        self._axes[key] = new

        if new.label is not None:
            self._labels[new.label] = key

    def __setitem__(self, key, new):
        """
        Call set() to set an entry of an Axes object to a given
        Axis (or Axis-like) "new". We don't know where this Axis came from,
        so always copy it.
        """
        self.set(key, new, copy=True)

    def __eq__(self, other):
        return (self.ndim == other.ndim
                and
                all(a1 == a2 for a1, a2 in zip(self._axes, other._axes)))

    def _get_property_all_axes(prop):
        """
        Retrieve a property from all axes at once

        Args:
          prop -- string naming a property of the Axes object

        Returns:
          a function that returns an ndarray containing the
          value of the specified property for every axis
        """

        @property
        def wrapper(self):

            return np.array([getattr(axis, prop) for axis in self._axes])

        return wrapper

    # following functions return an array of the named
    # property for all axes
    nbins = _get_property_all_axes('nbins')
    units = _get_property_all_axes('unit')
    labels = _get_property_all_axes('label')
    scales = _get_property_all_axes('axis_scale')
    lo_lims = _get_property_all_axes('lo_lim')
    hi_lims = _get_property_all_axes('hi_lim')

    @labels.setter
    def labels(self, new_labels):

        if len(new_labels) != self.ndim:
            raise ValueError("Number of labels does not correspond to "
                             "number of dimensions.")

        # force a copy of our Axis objects beacause we are
        # mutating them.
        new_axes = [ a.copy() for a in self._axes ]

        for axis, label in zip(new_axes, new_labels):
            axis.label = label

        self._axes = new_axes
        self._update_labels_index()

    def _normalize_values(self, values):
        """
        Normalize an input to find_bin or interp_weights, which needs
        somewhat complex processing to distinguish scalars and
        array-likes, depending on the number of axes.

        Args:
            values (scalar or array-like): value(s) to process
               If single value, may be ndim coordinates
                 as separate arguments or a single array-like
               if multiple values, may be ndim array-likes
                 of coordinates as separate arguments or
                 a single array-like containing same

        Returns:
            a tuple whose ith member corresponds to the ith axis.
            The tuple elements are either
                - single scalar coordinates or Quantities
                - arrays of scalar coordinates or Quantities
        """

        if self.ndim == 1: # 1-D

            # input must be a tuple of args which contains either
            #  - a single scalar (a coordinate value), or
            #  - a 1-D array-like of coordinate values

            if len(values) != 1: # multiple arguments implies > 1-D point
                raise ValueError("Mismatch between values shape and number of axes")

            values = values[0]

            # convert non-scalar, non-array array-like
            # so that output will be an array
            if not np.isscalar(values) and \
               not isinstance(values, u.Quantity):
                values = np.asarray(values)

            values = (values,)

        else: # multi-D

            # input must be EITHER
            #  + a tuple of args which is either
            #    - a single point (ndims scalar coords), or
            #    - ndims 1-D array-likes of coords
            # OR
            #  + tuple containing a single array-like, which
            #    itself contains one of the above two cases

            # standardize input to tuple of args
            if len(values) == 1:
                # third case -- array-like holding actual inputs
                # extract value and convert it to a tuple
                try:
                    values = tuple(values[0])
                except TypeError:
                    raise ValueError("Input cannot be single scalar")

            if len(values) != self.ndim:
                raise ValueError("Mismatch between values shape and number of axes")

        return values

    def find_bin(self, *values):

        """
        Return the indices of the bins that would contain the specified values.

        For one-dimensional arrays, :code:`values` may be a scalar
        (one value) or an array-like of values.  For multi-dimensional
        arrays, a single value's components may be passed as an
        array-like of scalar values or as separate scalar argument;
        multiple values may be passed as an array-like of arra-likes
        or as separate array-like arguments. Hence, for 2D Axes, the
        following are all acceptable:

        Single value:
        :code:`h.find_bin(x, y)`
        :code:`h.find_bin([x, y])`

        Multiple values:
        :code:`h.find_bin([x0, x1],[y0, y1],[z0, z1])`,
        :code:`h.find_bin([[x0, x1],[y0, y1],[z0, z1]])`

        Args:
            values (scalar or array-like): value(s) to find
                 If single value, may be ndim coordinates
                 as separate arguments or a single array-like
                 if multiple values, may be ndim array-likes
                 of coordinates as separate arguments or
                 a single array-like containing same
        Returns:
            bin indices
               For 1-D, returns scalar int if input was scalar,
                 or ndarray of int if it was array-like
               For multi-D, returns tuple of ndim ints if input
                 was scalars or tuple of ndim ndarrays of ints if it
                 was array-likes

        Note: value array-likes for each dimension are not
        required to have same shape or size.

        """

        values = self._normalize_values(values)

        res = tuple(axis.find_bin(val)
                    for val,axis in zip(values, self._axes))

        if self.ndim == 1:
            return res[0]
        else:
            return res

    def interp_weights(self, *values):
        """
        Get the bins and weights to linearly interpolate between bins.  The
        bin contents are assigned to the center of the bin.

        .. note::
            The output format changed with respect to version <2.x.
            Previously, the bins and weights outputs had a shape
            (2^ndim, ndim, N) and (2^ndim, N), respectively, while now
            both have shape (ndim, N). This is which is more
            efficient. It is left to the user to compute all neccesary
            bins combinations and weight products. This can be done by
            e.g.

            .. code-block:: python

                bins_expanded = np.asarray(list(itertools.product(*bins)))
                weights_expanded = np.prod(np.array(list(itertools.product(*weights))), axis = 1)


        Args:
            values (float or array): Coordinates within the axes to
            interpolate.

        Returns:
            Bins and weights to use. Each is a tuple of size (ndim,
            N), where N is the shape of the input values. Each element
            of the bins and weights tuples contains an array
            specifying the bins (integers) and weights (floats) needed
            for the interpolation along that particular dimension.

        """

        values = self._normalize_values(values)

        # get interpolating bins, weights for each value in each dimension
        res = ( a.interp_weights(vals) for a, vals in zip(self._axes, values) )
        bins, weights = zip(*((r[0], r[1]) for r in res))

        return (bins, weights)

    def expand_dims(self, a, axis):
        """
        Given an array `a` of dimension n, and a list of n axes
        from this Axes object, expand `a` to have a total of
        self.ndims dimensions, and move the original dimensions
        of `a` to be at the the offsets corresponding to `axes`.
        This rearrangement permits `a` to be broadcast against
        a Histogram that uses this Axes object.

        Note that for expansion to be well-defined, `a` must have
        at most self.ndim dimensions, and `axes` must specify a
        target offset for every dimension of `a`.

        Args:
          a -- array-like
            array to be expanded
          axis -- a.ndim axes in any form accepted by label_to_index()
            axes of self onto which the dimensions of `a` will be
            mapped after expansion.

        Returns:
           expanded, reorganized version of `a`

        """

        # standardize inputs to arrays
        if not isinstance(a, (np.ndarray, SparseArray)):
            a = np.array(a)

        axes = np.atleast_1d(self.label_to_index(axis))

        # sanity checks
        if a.ndim != len(axes):
            raise ValueError(f"Number of input axes ({len(axes)}) "
                             "does not match number of "
                             f"dimensions ({a.ndim}) of the "
                             "input array")

        if a.ndim > self.ndim:
            raise ValueError(f"Number of dimensions of the input array ({a.ndim}) "
                             "cannot be greater than the "
                             f"number of axes ({self.ndim})")

        # append enough new axes to make `a` match the dimension of self.
        # cannot use np.expand_dims() because it fails for sparse `a`
        orig_ndim = a.ndim
        a = a[(slice(None),)*a.ndim + (None,)*(self.ndim - a.ndim)]

        # permute a's original axes into positions specified by `axes`
        a = np.moveaxis(a, tuple(range(orig_ndim)), axes)

        return a

    def broadcast(self, a, axis):
        """
        Expand the dimensions of array `a` and broadcast it so that
        it has the same shape as self.  Preserve any padding in `a`
        that may be used for under/overflow when combining it with
        a Histogram with the same axes as self.

        Args:
            a: array-like
              array to broadcast
            axis: a.ndim axes in any form accepted by label_to_index()
              axes of self onto which the dimensions of `a` will be
              mapped after expansion.

        Returns:
            expanded, reorganized version of `a`
        """

        # add singleton dims
        a = self.expand_dims(a, axis)

        # if `a` is padded to allow for underflow/overflow in some
        # dimensions, preserve this padding in the shape of the
        # returned array.

        new_shape = tuple(axis.nbins + (2 if a_nbins == axis.nbins + 2 else 0) for
                          a_nbins, axis in zip(a.shape, self._axes))

        # subok=True makes output a Quantity if `a` is, preserving unit.
        # Unfortunately, it doesn't work for sparse arrays, but those
        # can't carry units anyway, so just omit subok for them.

        kwargs = {} if isinstance(a, SparseArray) else { 'subok' : True }
        return np.broadcast_to(a, new_shape, *kwargs)

    def expand_dict(self, axis_value, default = None):
        """
        Convert pairs of axis:value to a tuple of length `ndim`.

        Args:
            axis_value (dict): Dictionary with axis-value pairs (can be labels)
            default: Default filling value for unspecified axes

        Returns:
            tuple
        """

        val_list = [default] * self.ndim

        for axis,value in axis_value.items():

            axis = self.label_to_index(axis)

            val_list[axis] = value

        return tuple(val_list)

    def write(self, axes_group):
        """
        Write the component axes of this Axes objet
        into an HDF5 group.

        Parameters
        ----------
        axes_group: HDF5 group to write to

        """
        # Axes. Each one is a data set with attributes
        for i,axis in enumerate(self._axes):
            axis._write(axes_group, str(i))

    @staticmethod
    def open(axes_group):
        """
        Read a set of Axis objects from an HDF5 group
        and return as an Axes object.  If an axis
        is a subclass (e.g., a HealpixAxis), the class
        name is stored as a group attribute, and we
        read an object of the appropriate subtype.

        Parameters
        ----------
        axes_group: HDF5 group object containing Axes data

        Returns
        -------
        Axes object containing all axes in the group
        """

        import sys

        # read the axes in numerical order; don't rely on
        # HDF5 order tracking to maintain it.
        axis_ids = list(axes_group.keys())
        axis_ids.sort(key = int)

        axes = []
        for id in axis_ids:

            axis = axes_group[id]

            # Get subclass if any; else, use base Axis class.
            # Backwards compatible with old versions that only
            # used plain Axis objects and did not store class names.
            axis_cls = Axis

            if '__class__' in axis.attrs:
                class_module, class_name = axis.attrs['__class__']
                axis_cls = getattr(sys.modules[class_module], class_name)

            axes += [axis_cls._open(axis)]

        return Axes(axes, copy_axes=False)
