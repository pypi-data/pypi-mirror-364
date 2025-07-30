import logging
logger = logging.getLogger(__name__)

from enum import Enum

import operator

from copy import deepcopy

import numpy as np

from sparse import DOK, COO, GCXS, SparseArray

# This is an ugly way to get the value
# of AUTO_DENSIFY. There doesn't seem to be
# any public-facing API to get it.
import sparse
from packaging.version import Version
if Version(sparse.__version__) >= Version('0.16.0'):
    import sparse.numba_backend._settings as sps
else:
    import sparse._settings as sps

import astropy.units as u

from .axes import Axes, Axis

from .feature import COPY_IF_NEEDED

# Invariants that hold for Histogram objects:
#
# At the beginning of each call to a method,
#  if Histogram is sparse, it is in COO format
#
# If a Histogram has sparse contents and has sumw2,
# its sumw2 is also sparse.

class Histogram(object):
    """This is a wrapper of a numpy array with axes and a fill
    method. Sparse array from pydata's sparse package are also
    supported.

    Like an array, the histogram can have an arbitrary number of
    dimensions.

    Standard numpy array indexing is supported to get the contents
    --i.e. :code:`h[:]`, :code:`h[4]`, :code:`h[[1,3,4]]`,
    :code:`h[:,5:50:2]]`, etc.--. However, the meaning of the
    :code:`-1` index is different. Instead of counting from the end,
    :code:`-1` corresponds to the underflow bin. Similarly, an index
    equal to the number of bins corresponds to the overflow bin.

    You can however give relative position with respect to
    :code:`h.end` --e.g. :code:`h[0:h.end]` result in all regular
    bins, :code:`h[-1:h.end+1]` includes also the underflow/overflow
    bins and :code:`h[h.end]` gives you the contents of the overflow
    bin. The convenient aliases :code:`h.uf = -1`, :code:`h.of =
    e.end` and :code:`h.all = slice(-1,h.end+1)` --or
    :code:`slice(0,h.end)` if the under/overflow are not tracked-- are
    provided.

    You can also use an :code:`Ellipsis` object (:code:`...`) at the
    end to specify that the contents from the rest of the dimension
    are to have the under and overflow bins included. e.g. for a 3D
    histogram :code:`h[1,-1:h.end+1,-1:h.end+1] =
    h[1,...]`. :code:`h[:]` returns all contents without
    under/overflow bins and h[...] returns everything, including those
    special bins.

    If no initial contents are provided, axes do *not* track
    under/overflow by default.  If contents are provided, an axis
    tracks under/overflow by default if the provided contents has two
    more bins in that dimension than axis.nbins. You can specify that
    certain axes will/will not track under/overflow with the
    :code:`track_overflow` keyword. Note that attempting to access an
    underflow/overflow bin on an axis that is not tracked will result
    in an IndexError.

    If :code:`sumw2` is not :code:`None`, then the histogram will keep
    track of the sum of the weights squared. You should use this
    feature if you are using weighted data and are concerned about
    error propagation. You can access the sum of squared wieghts with
    :code:`h.sumw2[item]`, where `item` is interpreted the same way as
    in :code:`h[item]`.  :code:`h.bin_error[item]` return the
    :code:`sqrt(sumw2)` (or :code:`sqrt(contents)` is :code:`sumw2 was
    not specified`).

    The binary operators :code:`+`, :code:`-`, :code:`*` and :code:`/`
    are supported for Histograms and correctly propagate error if
    sumw2 is present.  The other operand can be a Histogram, a scalar
    or an array of appropiate size.  Note that :code:`h += h0` is more
    efficient than :code:`h = h + h0` since latter involves the
    instantiation of a new histogram. Unary negation of a Histogram is
    supported, as is dividing a scalar by a Histogram.

    Args:
        edges (Axes or array): Definition of bin edges, as anything
            that can be processes by Axes. Lower edge value is
            included in the bin, upper edge value is excluded.
        contents (array-like or SparseArray): Initialization of
            histogram contents. May include overflow/underflow bins if
            overflow is being tracked; if tracking is enabled and
            contents does not have these bins, they will be
            initialized to zeros. If omitted, creates an array of
            zeros.
        sumw2 (None, bool or array): If not None, the histogram will
            maintain squared weights associated with the elements of
            contents.  These weights are initially zero if sumw2 =
            True but may instead be initialized explicitly with an
            array.  Arithmetic between two histograms with squared
            weights propagates these weights to the result according
            to propagation-of-error theory.
        labels (array of str): Optionally label the axes for easier indexing
        axis_scale (str or array): Bin center mode e.g. `"linear"` or
            `"log"`.  See ``Axis.axis_scale``.
        sparse (bool): indicate if contents and sumw2 should be
            maintained as dense or sparse arrays.  If specified,
            contents and sumw2 will be converted to the specified
            sparsity if needed (but attempting to densify a sparse
            matrix will fail to avoid unexpected memory blowups).  If
            not specified, the Histogram's sparsity follows that of
            the provided contents, or is dense if no contents are
            provided.
        unit (Unit-like): unit of contents; if not specified, inferred
            from contents if u.Quantity or None otherwise
        track_overflow (bool, array-like, or dict): Whether to
            allocate space to track the underflow and overflow
            bins. Acceptable forms include
              - a single boolean value (applies to all axes)
              - a 1-D array-like with a boolean value per axis
              - a dictionary specifying boolean values for a set
                of named/numbered axes.  For axes not in the dict,
                the default is True.
            If this parameter is not provided, the default behavior
            depends on the value of the `contents` argument.
              - if `contents` is not provided, overflow is not tracked
                on any axis.
              - if `contents` is provided, each axis tracks overflow
                if contents includes overflow/underflow bins for that
                axis, i.e., if its size along that axis is two more
                than the axis' number of bins.
        dtype: Numpy datatype or None type of contents array; if None,
            use type of provided contents, or default (float64) if
            none provided.
        copy_contents (bool): if True (default), numpy arrays or
            Quantity arrays passed as contents and sumw2 will *not* be
            copied unless necessary; hence, the Histogram's memory may
            alias these values.

    """
    def __init__(self, edges, contents = None, sumw2 = None,
                 labels = None, axis_scale = None,
                 sparse = None, unit = None, track_overflow = None,
                 dtype = None, copy_contents = True):

        from scipy.sparse import sparray, spmatrix

        self._axes = Axes(edges, labels = labels, axis_scale = axis_scale)

        # set unit of Histogram, if any
        if unit is None:
            if isinstance(contents, u.Quantity):
                self._unit = contents.unit # derive unit from contents
            else:
                self._unit = None
        else:
            self._unit = u.Unit(unit)

        # Standardize contents (with under/overflow) or initialize them to zero.
        # Track operations that might make a copy, so we know if we still need
        # to copy the contents array at the end.  We don't want an unconditional
        # copy because contents might be very large.
        if contents is not None:

            is_copied = False

            # convert Quantity to bare value, after adjusting it to
            # histogram's unit (if any).
            if isinstance(contents, u.Quantity):
                cnew = contents.to_value(self._unit)
                if cnew is not contents.value:
                    is_copied = True
                contents = cnew

            # convert SciPy arrays to COO
            if isinstance(contents, (sparray, spmatrix)):
                is_copied = True
                contents = COO.from_scipy_sparse(contents)

            # make sure contents is a dense or sparse array
            if not isinstance(contents, (np.ndarray, SparseArray)):
                is_copied = True
                contents = np.asarray(contents, dtype=dtype)
                contents = np.atleast_1d(contents)

            if contents.ndim != self._axes.ndim:
                raise ValueError(f"cannot use contents of dimension {contents.ndim} for "
                                 f"Histogram of dimension {self._axes.ndim}")

            if isinstance(contents, (GCXS, DOK)):
                # sparse arrays are initially stored as COO.  Slicing
                # does not work well with GCXS, so we use COO instead;
                # See https://github.com/pydata/sparse/issues/550.
                is_copied = True
                contents = contents.asformat('coo')

            if dtype is not None:
                # make sure contents' dtype matches given dtype
                is_copied |= (contents.dtype != dtype)
                contents = contents.astype(dtype, copy=False)

            if sparse is not None:
                if sparse and not isinstance(contents, SparseArray):
                    is_copied = True
                    contents = COO.from_numpy(contents)
                elif not sparse and isinstance(contents, SparseArray):
                    if not sps.AUTO_DENSIFY:
                        raise RuntimeError("Cannot convert sparse contents to dense automatically. "
                                           "To manually densify, use the todense method.")

                    is_copied = True
                    contents = contents.todense()

            if track_overflow is None:
                # by default, overflow tracking follows contents shape
                track_overflow = (contents.shape == self._axes.nbins + 2)

            # convert track_overflow argument to standard format
            self._track_overflow = self._standardize_track_overflow(track_overflow)

            # determine if contents must be padded to match overflow tracking settings
            padding = self._get_padding_for_overflow(self._track_overflow, self._axes.nbins, contents.shape)
            self._contents = self._pad(contents, padding)
            if self._contents is not contents:
                is_copied = True

            if copy_contents and not is_copied:
                self._contents = self._contents.copy()
        else:

            if track_overflow is None:
                # by default, overflow tracking is *off* for empty contents
                track_overflow = False

            # convert track_overflow argument to standard format
            self._track_overflow = self._standardize_track_overflow(track_overflow)

            # initialize contents to array of all zeros
            contents_shape = tuple( self._axes.nbins + 2 * self._track_overflow )

            if sparse:
                self._contents = DOK(shape = contents_shape,
                                     dtype = dtype,
                                     fill_value = 0).asformat('coo')
            else:
                self._contents = np.zeros(contents_shape, dtype=dtype)

        self._init_specials()

        # create sumw2 histogram if requested
        self.set_sumw2(sumw2, copy = copy_contents)

    def _init_specials(self):
        """
        Create objects for special access methods on Histogram's contents
        """
        self.bin_error = self._get_bin_error(self)
        self.slice = self._slice(self)

    def set_sumw2(self, sumw2, copy = True):
        """
        Set the sumw2 matrix to a Histogram to track the sum of error
        weights. If not None/False, sumw2 must be either an array-like
        with the same shape as contents or a Histogram with the same axes
        as contents. It will be coerced to have the same units,
        sparsity, dtype, and overflow tracking as the base Histogram.

        Args:
           sumw2
             values for weights: True for all zeros, or a Histogram, or an
             array-like; None or False to remove any existing sumw2
           copy: bool
             if True (default), copy the object passed as sumw2; otherwise,
             create a view into the object if possible.

        """

        if sumw2 is None or sumw2 is False:
            self._sumw2 = None
        else:
            # derive unit of sumw2 from that of main histogram
            if self._unit is not None:
                w2unit = self._unit**2
            else:
                w2unit = None

            if isinstance(sumw2, Histogram):
                if sumw2._axes != self._axes:
                    raise ValueError("Histogram sumw2 must have same axes as contents")

                is_copied = False

                # match dtype of sumw2 to that of contents
                is_copied |= (sumw2._contents.dtype != self._contents.dtype)
                sumw2 = sumw2.astype(self._contents.dtype, copy=False)

                # match sparsity of sumw2 to that of contents
                if not sumw2.is_sparse and self.is_sparse:
                    is_copied = True
                    sumw2 = sumw2.to_sparse()
                elif sumw2.is_sparse and not self.is_sparse:
                    if not sps.AUTO_DENSIFY:
                        raise RuntimeError("Cannot convert a sparse histogram to dense automatically. "
                                           "To manually densify, use the todense method.")

                    is_copied = True
                    sumw2 = sumw2.to_dense()

                # match overflow tracking of sumw2 to that of contents
                if not np.array_equal(sumw2._track_overflow, self._track_overflow):
                    is_copied = True
                    sumw2.track_overflow(self._track_overflow)

                # adjust unit of sumw2 and copy it if needed
                self._sumw2 = sumw2.to(w2unit, copy = copy and not is_copied)

            else:
                sumw2_contents = None if sumw2 is True else sumw2

                # for zero init, bare value, or Quantity, let __init__ do coercion of contents
                self._sumw2 = Histogram(self._axes,
                                        contents = sumw2_contents,
                                        dtype = self._contents.dtype,
                                        sparse = self.is_sparse,
                                        unit = w2unit,
                                        track_overflow = self._track_overflow,
                                        copy_contents = copy)

    def copy(self):
        """
        Make a deep copy of a Histogram.  The copy shares no
        *writable* members with the original; the only shared
        members are those that will never be mutated.

        This function preserves subclass types if called from a
        derived class.  Subclasses with additional data members
        may override this function; if they do not, their
        data members will be deepcopied.
        """

        # short-circuit if we are in the middle of _replace
        if hasattr(self, '_new_instance'):
            return self._new_instance
        else:
            return self._replace() # no replacements

    def __deepcopy__(self, memo):
        """
        Hook for deepcopy()
        """

        self._memo = memo # cache memo dict in case we need it
        new = self._replace() # no replacements
        del self._memo

        return new

    # all recognized data members of Histogram.
    # CHANGE THIS and the _replace() function if
    # we add or remove data members.
    _data_members = frozenset([
        '_axes',
        '_contents',
        '_sumw2',
        '_unit',
        '_track_overflow',
    ])

    def _replace(self, **kwargs):
        """
        Make a deep copy of a Histogram as defined for copy(), but
        optionally specify one or more key-value pairs naming a data
        member of Histogram and a value to use for it in the new
        object instead of performing the default copy operation.

        """
        cls = self.__class__
        new = cls.__new__(cls)

        # set any members specified by kwargs
        for member in kwargs:

            assert member in Histogram._data_members, \
                f"Histogram has no data member {member}"

            setattr(new, member, kwargs[member])

        if not hasattr(new, '_axes'):
            new._axes = self._axes.copy()

        if not hasattr(new, '_contents'):
            new._contents = self._contents.copy()

        if not hasattr(new, '_unit'):
            new._unit = self._unit  # no need to copy unit

        if not hasattr(new, '_track_overflow'):
            new._track_overflow = self._track_overflow  # no need to copy track_overflow

        new._init_specials()

        if not hasattr(new, '_sumw2'):
            if self._sumw2 is not None:
                new._sumw2 = self._sumw2.copy()
            else:
                new._sumw2 = None

        if cls != Histogram:
            if cls.copy == Histogram.copy: # copy not overridden
                self_dict = vars(self)
                new_dict = vars(new)

                # if we were called from __deepcopy__(), pass along
                # the supplied memo object to recursive deepcopy calls.
                kwargs = {}
                if hasattr(self, '_memo'):
                    kwargs['memo'] = self._memo

                # don't copy the temporary _memo field recursively
                for member in self_dict.keys() - new_dict.keys() - { '_memo' }:
                    setattr(new, member, deepcopy(self_dict[member], **kwargs))

            else:
                self._new_instance = new # copy() will return this
                self.copy()
                del self._new_instance

        return new

    def astype(self, dtype, copy=True):
        """
        Cast the contents and, if present, the sumw2 of a Histogram to
        a different data type.  If the new type differs from the old
        type, we always return a copy; otherwise, we return a copy
        if copy=True or the original if copy=False.
        """

        if self._contents.dtype == dtype and not copy:
            return self
        else:

            new_contents = self._contents.astype(dtype) # makes a copy

            if self._sumw2 is not None:
                new_sumw2 = self._sumw2.astype(dtype) # makes a copy
            else:
                new_sumw2 = None

            return self._replace(_contents=new_contents,
                                 _sumw2=new_sumw2)

    @staticmethod
    def _compute_padding(needs_padding):
        """
        Given a Boolean array indicating whether overflow padding is
        needed in each dimension of an array, compute an argument to
        np.pad that adds padding where needed.

        Args:
          needs_padding: np.ndarray of bool [axes.ndims]
          ith entry is True iff ith dimension needs padding
        Returns:
          np.ndarray *view* of size |needs_padding| x 2 with
          padding values for each dimension of the array.

        NB: return value is not writable!
        """
        padlen = needs_padding.astype(int) # 1 if needed, 0 if not
        return np.broadcast_to(padlen[:,None], (needs_padding.size, 2)) # ints -> pairs

    @staticmethod
    def _get_padding_for_overflow(track_overflow, hshape, oshape,
                                  mask=None, check_sanity=True,
                                  first_dim = 0):
        """
        Compute the padding necessary to convert an array of shape oshape to
        match the contents shape of a Histogram with shape hshape and
        specified track_overflow settings.

        Args:
         track_overflow: np.ndarray of bool
            Should overflow be tracked for each dimension of this Histogram?
         hshape: array-like of int
            Shape of Histogram, not including overflow/underflow bins
        oshape: array-like of int
            Shape of array being padded to match Histogram
        mask: np.ndarray (optional)
            If not None, mask of length == hshape indicating which
            dimensions should be checked for padding. Unchecked dimensions
            always receive zero padding.
        check_sanity: bool
            If True, make sure each dimension of oshape either conforms to
            hshape given its tracking requirement or can be padded to conform.
            Raise an exception if this test fails.
        first_dim: int
            The dimension of the Histogram corresponding to the first entry
            in track_overflow (used only for error printing)
        Returns:
          np.ndarray *view* of size |needs_padding| x 2 with
          padding values for each dimension of the array.

        NB: return value is not writable!
        """

        hshape = np.asarray(hshape) # make sure at least one of oshape, hshape is array

        if check_sanity:
            # First, check that oshape can be transformed to hshape via padding
            invalid_padding   = track_overflow & ~np.isin(oshape - hshape, (0,2))
            invalid_nopadding = ~track_overflow & ~(oshape == hshape)

            if mask is not None:
                invalid_padding   &= mask
                invalid_nopadding &= mask

            if np.any(invalid_padding):
                bad_axes = np.nonzero(invalid_padding)[0]
                first_bad = bad_axes[0]
                hlen = hshape[first_bad]
                olen = oshape[first_bad]
                raise ValueError(f"Array axis {first_dim + first_bad} has size {olen}; "
                                 f"must be {hlen} or {hlen+2} to use with track_overflow = True")

            if np.any(invalid_nopadding):
                bad_axes = np.nonzero(invalid_nopadding)[0]
                first_bad = bad_axes[0]
                hlen = hshape[first_bad]
                olen = oshape[first_bad]
                raise ValueError(f"Array axis {first_dim + first_bad} has size {olen}; "
                                 f"must be {hlen} to use with track_overflow = False")

        # Next, identify which dimensions need to be padded
        needs_padding = track_overflow & (oshape == hshape)
        if mask is not None:
            needs_padding &= mask

        # Finally, return the padding argument to np.pad
        return Histogram._compute_padding(needs_padding)

    @staticmethod
    def _pad(arr, padding, value=0):
        """
        Pad array arr as needed with value.

        Args:
          arr     -- np.ndarray
          padding -- array-like of size [arr.ndim x 2]
                     giving padding values for each dim of arr
          value   -- value to use for padding cells (default 0)

        Returns:
          padded array, which may be the original (if no padding is
          needed) or a copy
        """

        padding = np.asarray(padding)

        if not padding.any():
            return arr
        else:
            return np.pad(arr, padding, constant_values=value)

    def _standardize_track_overflow(self, track_overflow):
        """
        Convert any valid form of track_overflow to an array of
        Boolean values per axis.

        Args:
          track_overflow (bool, array-like, or dict): Whether to
          allocate space to track the underflow and overflow
          bins. Acceptable forms include
            - a single boolean value (applies to all axes)
            - a 1-D array-like with a boolean value per axis
            - a dictionary specifying boolean values for a set
              of named/numbered axes.  For axes not in the dict,
              the default is False.

        """
        if isinstance(track_overflow, (bool, np.bool_)):
            track_overflow = np.full(self.ndim, track_overflow)
        elif isinstance(track_overflow, (np.ndarray, list, tuple)):
            track_overflow = np.atleast_1d(track_overflow)
            if track_overflow.size != self.ndim:
                raise ValueError("track_overflow size doesn't match the number of dimensions")
        elif isinstance(track_overflow, dict):
            track_overflow = np.asarray(self._axes.expand_dict(track_overflow, default = False))
        else:
            raise TypeError("Track overflow can only be bool, array, or dictionary.")

        return track_overflow

    def _match_track_overflow(self, old_track_overflow, new_track_overflow):
        """
        Compute slices and padding needed to go from old to new overflow settings.

        Args:
          old_track_overflow -- np.ndarray of bool
                                old track_overflow settings
          new_track_overflow -- np.ndarray of bool
                                new track_overflow settings

        Returns:
          tuple (slices, padding)
          slices -- tuple of slices to reduce each dimension from
                    which overflow is removed
          padding --  np.ndarray *view* with padding values for
                     each dimension

        NB: padding is not writable!
        """

        needs_padding = ~old_track_overflow & new_track_overflow
        padding = self._compute_padding(needs_padding)

        needs_slicing = old_track_overflow & ~new_track_overflow
        slices = tuple( slice(1,-1) if b else slice(None) for b in needs_slicing )

        return slices, padding

    def _update_track_overflow(self, new_track_overflow):
        """
        Update the contents and sumw2 of this Histogram to reflect
        a specified set of overflow tracking settings.

        Args:
          new_track_overflow -- bool, array-like, or dict
             specifying track-overflow settings per dimension
        """

        new_track_overflow = self._standardize_track_overflow(new_track_overflow)

        slices, padding = self._match_track_overflow(self._track_overflow,
                                                     new_track_overflow)

        self._track_overflow = new_track_overflow

        self._contents = self._pad(self._contents[slices], padding)

        # if we are possibly no longer padding a dense array that was
        # padded, make sure array is contiguous in memory after any slicing
        if not self.is_sparse and not padding.any():
            self._contents = np.ascontiguousarray(self._contents)

        if self._sumw2 is not None:
            self._sumw2._update_track_overflow(new_track_overflow)

    def track_overflow(self, track_overflow = None):
        """
        Obtain an array specifying whether each axis is tracking underflows and overflows.
        If input is not None, adjust the track_overflow settings to those provided.

        Args:
            track_overflow (bool, array-like, or dict): Optional. New overflow tracking settings

        Returns:
            np.ndarray with *copy* of current overflow tracking settings

        We return a copy to external callers because it is unsafe to modify a live
        track_overflow array in place; any updates *must* be fed back to track_overflow
        (internally, to _update_track_overflow) to take effect.
        """

        if track_overflow is not None:
            self._update_track_overflow(track_overflow)

        # return a copy to avoid letting caller mutate the
        # track_overflow array, which will not work.
        return self._track_overflow.copy()

    @property
    def unit(self):
        return self._unit

    def to(self, unit, equivalencies=[], update=True, copy=True):
        """
        Convert a Histogram to a different unit.

        Args:
            unit (unit-like): Unit to convert to.
            equivalencies (list or tuple): A list of equivalence pairs to try if the units are not
                directly convertible.
            update (bool): If ``update`` is ``False``, only the units will be changed without
                updating the contents accordingly
            copy (bool): If True (default), then the value is copied. Otherwise, a copy
                will only be made if necessary.
        """

        old_unit = self._unit
        new_unit = None if unit is None else u.Unit(unit)

        if copy:
            new = self.copy()
        else:
            new = self

        if update:
            # Apply factor needed to convert to new unit to contents and sumw2
            if old_unit is None:
                if new_unit is not None and new_unit != u.dimensionless_unscaled:
                    raise TypeError("Assigning unit to Histogram without units")
            elif new_unit is not None:
                factor = old_unit.to(new_unit, equivalencies = equivalencies)
                if factor != 1.0:
                    new *= factor

        # Update units
        new._unit = new_unit

        if new._sumw2 is not None:
            new._sumw2._unit = None if new_unit is None else new_unit**2

        return new

    def _with_units(self, value):
        """
        Add unit to value if histogram has one and value is dense,
        creating a Quantity array.

        Ideally, we would add a unit whether value is dense or sparse.
        Unfortunately, SparseArray is not compatible with Quantity, so
        if we want to return a sparse array value, we cannot set the
        unit.  We do not want to pay to densify a potentially large
        matrix, so we just return the raw value.

        """

        if self._unit is not None and not isinstance(value, SparseArray):
            # prevent copy when adding unit
            return u.Quantity(value, unit=self._unit, copy=COPY_IF_NEEDED)
        else:
            return value

    @property
    def is_sparse(self):
        """
        Return True if the underlyying histogram contents array is sparse, or False if dense.
        """
        return isinstance(self._contents, SparseArray)

    def to_dense(self):
        """
        Return a dense copy of a histogram
        """

        h_dense = self.copy()

        if h_dense.is_sparse:
            h_dense._contents = self._contents.todense()

            if h_dense._sumw2 is not None:
                h_dense._sumw2 = h_dense._sumw2.to_dense()

        return h_dense

    # alias pydata sparse style
    todense = to_dense

    def to_sparse(self):
        """
        Return a sparse copy of a histogram.
        """

        h_sparse = self.copy()

        if not h_sparse.is_sparse:
            h_sparse._contents = COO.from_numpy(self._contents)

            if h_sparse._sumw2 is not None:
                h_sparse._sumw2 = self._sumw2.to_sparse()

        return h_sparse

    # pydata sparse style
    tosparse = to_sparse

    @property
    def sumw2(self):
        return self._sumw2

    @property
    def ndim(self):
        return self._axes.ndim

    def __eq__(self, other):
        """
        Check whether two Histograms are equal.  Sparse
        and dense histograms with the same axes, unit, and
        contents/sumw2, including under/overflow bins if
        present, are considered equal.
        """

        return (self._axes == other._axes
                and
                np.array_equal(self._track_overflow, other._track_overflow)
                and
                self._unit == other._unit
                and
                np.all(self._contents == other._contents) # sparse does not support array_equal
                and
                self._sumw2 == other._sumw2)

    def __array__(self, dtype=None, copy=None):
        """
        Return a view or copy of our contents as a dense ndarray.
        If histogram has units, return a Quantity array to preserve
        them.

        """

        if self.is_sparse:

            if not sps.AUTO_DENSIFY:
                raise RuntimeError("Cannot convert a sparse histogram to dense automatically. "
                                    "To manually densify, use the todense method.")

            arr = self._get_contents().todense()
        else:
            arr = self._get_contents()

        if dtype is not None and arr.dtype != dtype:
            arr = arr.astype(dtype) # makes a copy
        elif copy and not self.is_sparse: # todense copies
            arr = arr.copy()

        return self._with_units(arr)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):

        if len(inputs) != 1 or inputs[0] is not self:
            raise NotImplementedError(
                "Only numpy functions with a single operand are supported "
                "e.g. np.sin(h). Call h.contents explicitly to "
                "get the corresponding array e.g. np.maximum(h.contents, a)")

        # units are *not* dropped for dense contents (but are for sparse)
        arr = self._with_units(self._get_contents())

        return ufunc(arr, *inputs[1:], **kwargs)

    def __array_function__(self, func, types, args, kwargs):

        if len(args) != 1 or args[0] is not self:
            raise NotImplementedError(
                "Only numpy functions with a single operand are supported "
                "e.g. np.sum(h). Call h.contents explicitly to "
                "get the corresponding array e.g. np.dot(h.contents, a)")

        # units are *not* dropped for dense contents (but are for sparse)
        arr = self._with_units(self._get_contents())

        return func(arr, *args[1:], **kwargs)

    class _NBINS():
        '''
        Convenience class that will expand to the number of bins of a
        given dimension.

        The trick is to overload the -/+ operators so that h.end +/-
        offset (h being an instance of Histogram and 'end' an static
        instance of Histogram._NBINS) returns an instance of _NBINS
        itself, which stores the offset. The [] operator can then
        detect that the input is an instance of _NBINS and convert it
        into an integer with respect to the size of the appropriate
        axis.

        '''

        def __init__(self, offset = 0):
            self.offset = offset

        def __add__(self, offset):
            return self.__class__(offset)

        def __sub__(self, offset):
            return self + (-offset)

    end = _NBINS()

    # Convenient aliases
    uf = -1
    of = end

    class _ALL():
        """
        Expands to slice(-1, end+1) if the axis tracks under/overflow,
        or slice(0, end) otherwise
        """

    all = _ALL()

    def _prepare_indices(self, indices):
        """
        Adjust a multi-dimensional index expression into the
        contents of a Histogram to properly index ._contents.
        """

        def _prepare_index(index, dim):
            """
            Adjust an index expressed as a scalar value (integer or
            'end' expression), a slice, or a multi-D array of scalar
            indices to account for overflow padding.  As a special
            case, handle an index that is Boolean mask, which may
            index one or more dimensions of the Histogram starting
            with dim.
            """

            overflow_offset = int(self._track_overflow[dim])

            def _adjust_scalar_index(index):
                """
                adjust a scalar index expression and make sure it
                is valid for the Histogram's contents
                """
                if isinstance(index, self._NBINS): # expand 'end' expression
                    index = self._axes[dim].nbins + index.offset

                index += overflow_offset

                if index < 0 or index > self._contents.shape[dim]:
                    raise IndexError("Bin index out of bounds")

                return index

            if isinstance(index, slice):
                start = 0 if index.start is None else index.start
                stop  = self._axes[dim].nbins if index.stop is None else index.stop

                index = slice(_adjust_scalar_index(start),
                              _adjust_scalar_index(stop),
                              index.step)

            elif isinstance(index, self._ALL):
                # convert 'all' to slice for whole of dim, including oflow/uflow
                # (no need to check bounds)
                index = slice(0, self._axes[dim].nbins + 2*overflow_offset)

            elif isinstance(index, np.ndarray):

                if index.dtype in (bool, np.bool_):
                    # Boolean mask array -- pad to match overflow
                    # settings for its dimension range
                    end_dim = dim + index.ndim
                    padding = self._get_padding_for_overflow(self._track_overflow[dim:end_dim],
                                                             self._axes.nbins[dim:end_dim],
                                                             index.shape, first_dim = dim)
                    index = self._pad(index, padding, value=False)

                else:
                    # (possibly multi-D) array of scalar indices (ints or _NBINS)
                    adjindex = [_adjust_scalar_index(i) for i in index.ravel()]
                    index = np.reshape(adjindex, index.shape)

            else: # scalar index (could be _NBINS)
                index = _adjust_scalar_index(index)

            return index

        def normalize(index):
            """
            If index is a slice or a scalar value, return it as-is.
            If it is array-like, convert to a proper ndarray.
            If none of the above, fail.

            For each index we return, we also return the number of dimension
            it refers to in the array (usually 1, but Boolean masks can refer
            to several consecutive dimensions).
            """
            if isinstance(index, (slice, int, np.integer, self._NBINS, self._ALL)):
                return (index, 1)
            elif isinstance(index, (np.ndarray, list, tuple, range)):
                arr = np.asarray(index)
                if arr.ndim > 0:
                    return (arr, arr.ndim if arr.dtype in (bool, np.bool_) else 1)
                else:
                    return (arr.item(), 1)
            elif index is Ellipsis:
                raise IndexError("Ellipsis is supported only at end of index tuple")
            else:
                raise TypeError("Index can only be slice, scalar, or array-like")

        if isinstance(indices, dict):
            # expand dict of per-axis indices into tuple
            indices = self._axes.expand_dict(indices, default = slice(None))
        elif not isinstance(indices, tuple):
            indices = (indices,)

        # strip Ellipsis from end of index tuple; it is not supported elsewhere
        has_ellipsis = (indices[-1] is Ellipsis)
        if has_ellipsis:
            indices = indices[:-1]

        indices = tuple( normalize(i) for i in indices )
        has_multi_dim = any( i[1] > 1 for i in indices ) # does any index cover multiple dims?

        if not has_multi_dim:
            # easy case -- each index describes exactly one dimension
            adjusted_indices = tuple(_prepare_index(index, dim) for
                                     dim, (index, _) in enumerate(indices))
            nSpecifiedDims = len(indices)
        else:
            # hard case -- some mask index describes > 1 dimension
            adjusted_indices = []
            dim = 0

            for index, ndim in indices:
                adjusted_indices.append(_prepare_index(index, dim))
                dim += ndim

            adjusted_indices = tuple(adjusted_indices)
            nSpecifiedDims = dim

        track = self._track_overflow
        if has_ellipsis:
            # unspecified dimensions at end refer to all of .full_contents
            rest_indices = tuple(slice(0, self._axes[dim].nbins + 2*int(track[dim]))
                                 for dim in range(nSpecifiedDims, self.ndim))
        else:
            # unspecified dimensions at end refer to all of .contents
            rest_indices = tuple(slice(int(track[dim]), self._axes[dim].nbins + int(track[dim]))
                                 for dim in range(nSpecifiedDims, self.ndim))

        return adjusted_indices + rest_indices

    """
    Access methods

    The following code defines two kinds of access methods: *internal*
    methods, which should be used by the methods of the Histogram
    class, and *external* methods, which should be used by users of
    the class and by subclasses.

    Both internal and external accessors understand the special
    indexing rules associated with overflow tracking, as well as the
    special values 'all' and 'end'.  They also manipulate the format
    of a sparse contents array to ensure that writes to it will
    succeed.

    External accessors also understand unit conformity and will return
    a Quantity for dense histograms with associated units, whereas
    internal accessors always return a bare value.

    CAUTION: external users should *never* directly read or write a
    Histogram's _contents array; doing so may yield unexpected results
    depending on whether the Histogram is using overflow tracking and
    may fail depending on its sparsity.  Always use the external
    accessors __getitem__ and __setitem__ to read or write subarrays
    of a Histogram; they can be called by directly indexing the
    histogram object, e.g., x = h[1:3] or h[3:5, 1:2] = 0.  Use
    .contents to obtain a view of the histogram's contents without
    overflow/underflow bins, or .full_contents to obtain a view with
    these extra bins.

    Internal users should use the _get() and _set() methods to read
    and write subarrays of the Histogram's contents if indices are to
    be interpreted as for __getitem__ / __setitem__.  These methods
    work with bare values; *do not* use the external accessors (e.g.,
    self[1:3]) unless the intent is to obtain/provide a Quantity
    whenever the Histogram has units.  Use _get_contents() to
    obtain the bare equivalent of .contents, or use ._contents
    directly for the bare equivalent of .full_contents.

    Internal users that directly access ._contents instead of using
    _get() and _set() are responsible for handling the impacts of
    overflow tracking and for ensuring that sparse arrays are in the
    correct form (DOK for writing, COO for everything else) if needed.
    """

    def _set(self, indices, new_contents):
        """
        Update a slice of a Histogram's contents.  If the Histogram
        is sparse, it is converted to DOK form to enable partial
        updates in place.
        """

        # Make it mutable if needed
        if self.is_sparse:
            self._contents = self._contents.asformat('dok')

        indices = self._prepare_indices(indices)

        try:
            self._contents[indices] = new_contents
        except (IndexError, ValueError) as e:

            if self.is_sparse:
                # Check if advanced indexing is being used
                for index in indices:
                    if isinstance(index, np.ndarray):
                        logger.warning(
                            "Advanced indexing is not yet fully supported "
                            "for sparse arrays. See "
                            "https://github.com/pydata/sparse/issues/1 and "
                            "https://github.com/pydata/sparse/issues/114")

                        break
            raise e

        # Make it fast read-only
        if self.is_sparse:
            self._contents = self._contents.asformat('coo')

    def __setitem__(self, indices, new_contents):
        """
        Update a slice of a Histogram's contents.  The
        value used to update the contents must be unit-conformable
        to the Histogram's units, if present.
        """
        self._set(indices, self._strip_units(new_contents))

    def _get(self, indices):
        """
        Get a slice of a Histogram's contents as an array.
        Returns a *view* into original contents.  If the
        histogram is sparse, it is converted to COO form.
        """
        indices = self._prepare_indices(indices)

        try:
            return self._contents[indices]
        except IndexError as e:

            if self.is_sparse:
                # Check if advanced indexing is being used
                for index in indices:
                    if isinstance(index, np.ndarray):
                        logger.warning(
                            "Advanced indexing is not yet fully supported "
                            "for sparse arrays. See "
                            "https://github.com/pydata/sparse/issues/1 and "
                            "https://github.com/pydata/sparse/issues/114")

                        break
            raise e

    def _get_contents(self):
        return self._get(slice(None))

    def __getitem__(self, indices):
        """
        Get a slice of a Histogram's contents as an array.
        Returns a *view* into original contents.  If the
        Histogram has a unit *and* the contents array is dense,
        return the slice as a Quantity.
        """

        value = self._get(indices)
        return self._with_units(value)

    @property
    def contents(self):
        """
        Equivalent to :code:`h[:]`. Does not include under and overflow bins.
        """
        return self[:]

    @property
    def full_contents(self):
        """
        Equivalent to :code:`h[...]`. The size of each axis can be
        nbins or nbins+2, depending on the track_overflow parameters
        """
        return self[...]

    class _special_getitem:
        """
        This allows to use regular indexing for special access methods,
        e.g., h.bin_error[]
        """

        def __init__(self, hist):
            self._hist = hist

        def __getitem__(self, item):
            raise NotImplementedError

        def __array__(self):
            return self.contents

        @property
        def contents(self):
            return self[:]

        @property
        def full_contents(self):
            return self[...]

    class _get_bin_error(_special_getitem):
        """
        Return the sqrt of sumw2
        """

        def __getitem__(self, item):
            if self._hist._sumw2 is not None:
                result = np.sqrt(self._hist._sumw2._get(item))
            else:
                # fake it if no sumw2
                result = np.sqrt(np.abs(self._hist._get(item)))

            return self._hist._with_units(result)

        def __setitem__(self, indices, new_bin_error):

            if self._hist._sumw2 is None:
                raise ValueError("Histogram does not have sumw2")

            self._hist._sumw2[indices] = new_bin_error**2

    @property
    def shape(self):
        """
        Tuple with length of each axis
        """
        return self._axes.shape

    @property
    def axes(self):
        """
        Underlying axes object
        """

        return self._axes

    @property
    def axis(self):
        """
        Equivalent to :code:`self.axes[0]`, but fails if :code:`ndim > 1`
        """

        if self.ndim > 1:
            raise ValueError("Property 'axis' can only be used with 1D "
                            "histograms. Use `axes` for multidimensional "
                            "histograms")

        return self._axes[0]

    @axis.setter
    def axis(self, new):

        self._axes[0] = new

        if self._sumw2 is not None:
            self._sumw2.axis = new

    def expand_dims(self, *args, **kwargs):
        """
        Same as h.axes.expand_dims().
        """
        return self._axes.expand_dims(*args, **kwargs)

    def broadcast(self, *args, **kwargs):
        """
        Same as h.axes.broadcast().
        """
        return self._axes.broadcast(*args, **kwargs)

    def expand_dict(self, *args, **kwargs):
        """
        Same as h.axes.expand_dict().
        """
        return self._axes.expand_dict(*args, **kwargs)

    @property
    def dtype(self):
        return self._contents.dtype

    @property
    def nbins(self):

        if self.ndim == 1:
            return self._axes[0].nbins
        else:
            return self._axes.nbins

    def interp(self, *values, kind="linear"):
        """
        Perform multilinear interpolation of one or more values
        relative to the contents of this Histogram. The center of
        histogram bin (i1,...,in) is assumed to have the value
        h[i1,...,in] for purposes of interpolation.

        The interpolation weights along each axis are controlled by
        its scale. If the scale is 'linear' or 'symmetric',
        interpolation is linear; if it is 'log', the interpolation is
        log-linear.  Hence, interpolating a value halfway between two
        bin centers along a log-scale axis returns the *geometric*
        mean of the centers.

        Interpolation may be done using either the values in the
        Histogram (default) or their logs using the 'kind'
        parameter. If kind='log' is requested, the histogram's
        contents should all be > 0 to avoid warnings or errors.

        Args:
            values (scalar or array-like): value(s) to interpolate
               If single value, may be ndim coordinates
                 as separate arguments or a single array-like
               if multiple values, may be ndim array-likes
                 of coordinates as separate arguments or
                 a single array-like containing same
            kind (string): 'linear' (default) if multilinear interpolation
               is to be done using this Histogram's contents, or
               'log' if it is to be done on the logs of the contents
               and the results converted back to the linear domain.
        Return:
            interpolated values (scalar or array of same shape as values)

        """

        bins, weights = self._axes.interp_weights(*values)

        # If contents is sparse, we cannot index it with numpy
        # arrays of dimension > 1 due to limitations of the Sparse
        # package (even though this is perfectly fine for dense
        # arrays). In this case, ravel the bins and weights
        # before interpolating and restore the result shape to
        # match the bins shape (which == the values shape) after.

        if self.is_sparse and bins[0].ndim > 2:
            vshape = bins[0].shape[1:]
            bins    = tuple( b.reshape(b.shape[0], -1) for b in bins )
            weights = tuple( w.reshape(w.shape[0], -1) for w in weights )
        else:
            vshape = None

        isLog = (kind == "log") # do log, not linear, combining

        contents = self._get_contents()

        if isLog: # convert to log domain before interpolating
            contents = np.log(contents)

        interp_values = self._interp_multilinear(contents, bins, weights)

        if isLog: # convert result back out of log domain
            interp_values = np.exp(interp_values)

        if vshape is not None:
            interp_values = interp_values.reshape(vshape)

        return self._with_units(interp_values)

    @staticmethod
    def _interp_multilinear(contents, bins, weights):
        """
        Perform multilinear interpolation with respect to matrix 'contents',
        given arrays of bins and weights for a set of points.

        Args:
           contents: array of dimension ndim
           bins: tuple of ndim arrays; ith array contains one or more
                integers per input point specifying which bins of contents
                contain the values to be interpolated in ith dimension.
           weights: tuple of ndim arrays; ith array contains
                one or more floats per input point specifying the weights
                for values to be interpolated in ith dimension.

        For all dimensions i and all bins j, both bins[i][j] and
        weights[i][j] must have the same (arbitrary) shape if contents
        is dense, or must be a flat 1D array if it is sparse.  The
        number of bins may be different for each dimension but must
        match the corresponding number of weights.

        Returns:
            array of interpolated values of same shape as each
            elt of bins / weights

        """

        is_sparse = isinstance(contents, SparseArray)

        def densify(v):
            if is_sparse and not np.isscalar(v):
                return v.todense()
            else:
                return v

        def interp_r(idim, prev_bins):
            """
            Recursive multilinear interpolation
            Allows interpolation in a given dimension to use a
            linear combination of two or more bins; standard linear
            interpolation uses two bins with weights w and 1 - w.

            """
            w  = weights[idim]

            # extend each bin in current dim with all previous bins
            dimbins = ((b,) + prev_bins for b in bins[idim])

            # interpolate remaining dimensions to get result for each
            # bin in bins[idim], and combine results into one array
            c = np.stack(tuple(
                ((densify(contents[b]) # base case
                  if idim == 0
                  else interp_r(idim - 1, b))
                 for b in dimbins)
            ))

            # weighted sum gives one interpolated value per input point
            return np.sum(c * w, axis=0)

        return interp_r(len(bins) - 1, ())

    def find_bin(self, *args, **kwargs):
        return self._axes.find_bin(*args, **kwargs)

    def _strip_units(self, quantity):
        """
        Remove the unit from a quantity (if it exists) and return
        its value in the units of the Histogram, so that we may combine
        it with the Histogram's contents.

        We FAIL if:
          * we try to combine a non-dimensionless Quantity with
            a Histogram that has no units
          * we try to combine a scalar with a Histogram that has
            units
        """

        # convert bare unit to trivial Quantity
        if isinstance(quantity, u.UnitBase):
            quantity = 1. * quantity

        if isinstance(quantity, u.Quantity):

            if quantity.unit == u.dimensionless_unscaled:
                return quantity.value

            if self._unit is None:
                raise u.UnitConversionError("Cannot apply Quantity to Histogram without units")

            return quantity.to_value(self._unit)

        else:

            if not (self._unit is None or self._unit == u.dimensionless_unscaled):
                raise u.UnitConversionError("Cannot apply scalar to Histogram with units")

            return quantity

    def fill(self, *values, weight = None, warn_overflow = True):
        '''
        Add an entry to the histogram. Can be weighted.

        Follow same convention as find_bin()

        Args:
            values (float or array): Value of entry
            weight (float): Value weight in histogram. Defaults to 1
                in whatever units the histogram has
            warn_overflow (bool): Enable/disable warnings when an
            underflow or overflow occurs --i.e. when one or more of
            the input values falls beyond the range of the
            corresponding axis.

        Note:
            Note that weight needs to be specified explicitly by key;
            otherwise it will be considered a value, and an IndexError
            will be thrown.

        '''

        # Remove units from weight, converting if needed
        if weight is None:
            weight = 1
        else:
            weight = self._strip_units(weight)

        indices = self.find_bin(*values)

        # Standardize if single axis
        if not isinstance(indices, tuple):
            indices = (indices,)

        # Each index must have same size for stacking, so make sure
        # the sizes match by broadcasting all to largest size
        indices = np.broadcast_arrays(*indices)

        # Build 2D array [ndims x npoints] of indices for input values.
        # Must reshape because indices in each dimension may not be
        # a 1-D linear array.
        indices = np.stack(indices, axis=0).reshape(len(indices),-1)
        weight = np.broadcast_to(np.asarray(weight), indices.shape[1])

        # adjust indices to be relative to .full_contents, so
        # that we can use them to access ._contents directly
        indices += self._track_overflow[:,None]

        # eliminate any indices that are out of bounds (can happen
        # if we are not tracking overflow in some dimension)
        mask = np.all(np.logical_and(indices >= 0,
                                     indices < np.asarray(self._contents.shape)[:,None]),
                      axis = 0)

        if not mask.all():

            if warn_overflow:
                logger.warning(
                    "fill() discarded one or more values due to out-of-bounds "
                    "coordinate in a dimension without under/overflow tracking"
                )

            indices = indices[:,mask]
            weight = weight[mask]

        if weight.size > 0: # empty fails for dense, pointless for sparse

            if not self.is_sparse:

                indices = tuple(indices)

                # add.at sums values associated with duplicate indices
                np.add.at(self._contents, indices, weight)

                if self._sumw2 is not None:
                    np.add.at(self._sumw2._contents, indices, weight**2)
            else:

                # COO sums values associated with duplicate indices by default
                new_contents = COO(coords = indices,
                                   data = weight,
                                   shape = self._contents.shape)

                self._contents += new_contents

                if self._sumw2 is not None:
                    new_contents_sq = COO(coords = indices,
                                          data = weight**2,
                                          shape = self._contents.shape)

                    self._sumw2._contents += new_contents_sq

    def clear(self):
        """
        Set all counts to 0
        """

        if self.is_sparse:
            self._contents = DOK(shape = self._contents.shape,
                                 dtype = self._contents.dtype,
                                 fill_value = 0).asformat('coo')
        else:
            self._contents[:] = 0

        if self._sumw2 is not None:
            self._sumw2.clear()

    def _clear_border(self, which, axes = None):
        """
        Set border cells (over and/or underflow) to 0 in both
        contents and sumw2

        Args:
            which : list of which borders to zero out
            axes (None or array): Axis numbers or labels. All by default
        """

        if self.is_sparse: # ensure sparse contents is writable
            self._contents = self._contents.asformat('dok')

        if axes is None:
            axes = range(self.ndim)
        elif np.isscalar(axes):
            axes = [axes]

        axes = self._axes.label_to_index(axes)

        for n in axes:
            if self._track_overflow[n]:
                for idx in which:
                    indices = self.expand_dict({n : idx}, self.all)
                    self._set(indices, 0)

        if self.is_sparse: # return sparse contents to fast readonly form
            self._contents = self._contents.asformat('coo')

        if self._sumw2 is not None:
            self._sumw2._clear_border(which, axes)

    def clear_overflow(self, axes = None):
        self._clear_border((self.of,), axes)

    def clear_underflow(self, axes = None):
        self._clear_border((self.uf,), axes)

    def clear_underflow_and_overflow(self, axes = None):
        self._clear_border((self.uf, self.of), axes)

    def project(self, *axis):
        """
        Return a histogram containing a projection of the current one.

        Args:
            axis (axis index/label or array-like of same): axis or axes onto
                which the histogram will be projected.  Omitted axes will be
                summed over. The axes of the projected histogram will have the
                order specified by this argument, so project() can be used
                to permute a Histogram's axes (whether or not some are
                projected away).

        Return:
            Histogram: Projected histogram (a new object, not a view)
        """

        return self._project(axis, project_out=False)

    def project_out(self, *axis):
        """
        Return a histogram containing a projection that sums over the
        specified axes of the current one, leaving the rest intact.

        Args:
            axis (axis index/label or array-like of same): axis or
                axes that will be projected out of the
                histogram. Omitted axes will be retained in their
                current order.

        Return:
            Histogram: Projected histogram (a new object, not a view)
        """

        return self._project(axis, project_out = True)

    def _project(self, axis, project_out = False):
        """
        Common core of project() and project_out()

        If project_out is False; the axes in `axis` will be retained
        in the specified order.  If it is True, the axes in `axis`
        will be summed away.

        Args:
           axis: array-like of axis numbers or labels
           project_out: bool

        Return:
           Histogram: Projected histogram (a new object, not a view)
        """

        def _project_contents(contents, keep_axes, sum_axes):

            # Transpose the contents so that the first keep_axes
            # dimensions are the axes to keep, in the order requested
            # by the caller, while the remaining axes are the ones
            # to be summed away.
            #
            # We transpose before projecting out the sum_axes so
            # that the projected array is contiguous in memory.

            reordered_axes = np.concatenate((keep_axes, sum_axes))
            new_contents = np.transpose(contents, reordered_axes)

            if len(sum_axes) == 0: # sparse does not handle this case
                new_contents = new_contents.copy()
            else:
                new_sum_axes = tuple(range(len(keep_axes), new_contents.ndim))
                new_contents = new_contents.sum(axis = new_sum_axes)

            return new_contents

        # standardize input
        if len(axis) == 1 and \
           isinstance(axis[0], (list, np.ndarray, range, tuple)):
            # Got a sequence
            axis = axis[0]

        axes = np.asarray(self._axes.label_to_index(axis), dtype=int)

        if len(np.unique(axes)) != len(axes):
            raise ValueError("An axis can't repeat")

        # Compute axis ids in 0..ndim that are not in exes;
        # result is guaranteed to be in increasing order
        rest = np.setdiff1d(np.arange(self.ndim, dtype=int),
                            axes,
                            assume_unique=True)

        if project_out: # axes are to be summed over
            sum_axes = axes
            keep_axes = rest
        else:           # axes are to be retained
            keep_axes = axes
            sum_axes = rest

        if len(keep_axes) == 0:
            raise ValueError("Cannot project out all axes of a Histogram. "
                             "Consider using np.sum(h) or np.sum(h.full_contents) (includes under/overflow)")

        new_contents = _project_contents(self._contents, keep_axes, sum_axes)

        new_sumw2 = None
        if self._sumw2 is not None:
            new_sumw2_contents = _project_contents(self._sumw2._contents, keep_axes, sum_axes)
            new_sumw2 = self._sumw2._replace(_axes = self._axes[keep_axes],
                                             _contents = new_sumw2_contents,
                                             _track_overflow = self._track_overflow[keep_axes])

        new = self._replace(_axes     = self._axes[keep_axes],
                            _contents = new_contents,
                            _sumw2    = new_sumw2,
                            _track_overflow = self._track_overflow[keep_axes])

        return new

    @staticmethod
    def concatenate(edges, histograms, label = None, track_overflow = None):
        """
        Generate a Histogram H from a list of histograms h_1
        ... h_n. We create a new first axis of length equal to the
        list and set H[i] = h_i.

        For this operation to be well-defined, the axes of all input
        histograms must be equal, and they must all have the same
        sparsity; if any input has a unit, all must have compatible
        units.  If any input is a subclass of Histogram, all must have
        the same subclass type.

        If all inputs have sumw2, the output will as well; otherwise,
        all sumw2 values are discarded.

        Generate a Histogram from a list of histograms. The axes of
        all input histograms must be equal, and the new histogram will
        have one more dimension than the input. The new axis has index
        0.  If histograms can be subclassed, all of them must have the
        same class type.

        Args:
            edges (Axes or array): Definition of bin edges of the new dimension
            histograms (list of Histogram): List of histogram to fill contents.
                Might or might not include under/overflow bins.
            labels (str): Label the new dimension
            track_overflow (bool): Track underflow and overflow on the newly created axis.
                Defaults to True if number of histograms on new axis is 2 + # bins,
                or False otherwise.
        Return:
            new object of the same type as histograms[0] (Histogram or subclass)

        """

        def check_compatible(h, h0):

            if h.__class__ != h0.__class__:
                raise ValueError("Cannot combine Histograms of different subclasses "
                                 f"{h.__class__.__name__}, {h0.__class__.__name__}")

            if h.axes != h0.axes:
                raise ValueError("Cannot combine Histograms with different axes")

            if h.is_sparse != h0.is_sparse:
                raise ValueError("Cannot combine Histograms with different sparsities")

            if not np.array_equal(h._track_overflow, h0._track_overflow):
                raise ValueError("Cannot combine Histograms with different track_overflow settings")

            if (h._unit == None) != (h0._unit == None):
                raise ValueError("Cannot combine Histograms with and without units")

            return (h._sumw2 is not None) # do we have sumw2?

        if len(histograms) == 0:
            raise ValueError("Cannot concatenate empty list of Histograms")

        h0 = histograms[0]

        has_sumw2 = [ check_compatible(h, h0) for h in histograms ]

        shared_axes = h0._axes
        axis_newdim = Axis(edges, label=label)
        new_axes = Axes([axis_newdim] + list(shared_axes), copy_axes=False)

        # stick all the old histogram contents together
        new_contents = np.concatenate([h._contents[None] for h in histograms])

        new_unit = h0._unit
        if new_unit is not None:
            # adjust each histogram's value to account for different, but compatible units
            for i, h in enumerate(histograms):
                unit_factor = h._unit.to(new_unit)
                if unit_factor != 1.:
                    new_contents[i] *= unit_factor

        if track_overflow is None:
            # by default, overflow tracking follows contents shape
            track_overflow = (len(histograms) == axis_newdim.nbins + 2)

        new_track_overflow = np.append(track_overflow, h0._track_overflow)

        # compute overflow padding for dimension corresponding to new axis
        # we need padding in only one dimension, but padding function expects arrays
        padding_newdim = Histogram._get_padding_for_overflow(np.atleast_1d(track_overflow),
                                                             np.atleast_1d(axis_newdim.nbins),
                                                             np.atleast_1d(len(histograms)))

        # padding of all axes after the first is unchanged
        new_padding = np.concatenate((padding_newdim, np.zeros((shared_axes.ndim, 2), dtype=int)))

        new_contents = Histogram._pad(new_contents, new_padding)

        # Combine sumw2s if they exist in all histograms, using same unit and padding adjustments
        # as for contents (except that we must square the unit)
        if all(has_sumw2):

            new_sumw2_contents = np.concatenate([h._sumw2._contents[None] for h in histograms])

            if new_unit is not None:
                # adjust each histogram's value to account for different, but compatible units
                for i, h in enumerate(histograms):
                    unit_factor = h._unit.to(new_unit)
                    if unit_factor != 1.:
                        new_sumw2_contents[i] *= unit_factor**2

            new_sumw2_contents = Histogram._pad(new_sumw2_contents, new_padding)
            new_sumw2 = h0._sumw2._replace(_axes=new_axes,
                                           _contents=new_sumw2_contents,
                                           _track_overflow=new_track_overflow)

        else:
            if any(has_sumw2):
                logger.warning("Not all input histograms have sum of weights "
                               "squared. sumw2 will be dropped")
            new_sumw2 = None

        new = h0._replace(_axes=new_axes,
                          _contents=new_contents,
                          _sumw2=new_sumw2,
                          _track_overflow=new_track_overflow)

        return new

    class _slice:

        def __init__(self, hist):
            self._hist = hist

        def __getitem__(self, item):
            """Return a Histogram which is a *view* containing a slice of
            the current one.

            Args:
              item -- an indexing expression suitable for a
                Histogram's contents.  Advanced indexing is not
                supported, but .end, .all, and ellipsis are supported
                with the same restrictions as for ordinary Histogram
                indexing.

                Restrictions on valid indexing expressions include:
                 (1) the slice must include at least one non-under/overflow
                 bin of the original Histogram.  Slices containing
                 only overflow or underflow bins are not permitted.

                 (2) slicees with stride > 1 are not permitted due to
                 ill-defined interactions with under/overflow.

            Returns:
              A view into the current Histogram containing the
              specified slice of its contents.

              The new Histogram tracks overflow in the same set of
              dimensions as the original.  If the slice explicitly
              includes the Histogram's underflow and overflow bins for
              a given axis, those will be copied into the result;
              otherwise, they will be set to zero.

              If the original Histogram contains sumw2, the new
              one contains the corresponding slice of sumw2.

            Note that, unlike Histogram.__getitem__, slice.__getitem__
            does *not* squeeze away dimensions of length 1 -- the
            slice will always have exactly as many axes as the
            original Histogram, so that we do not lose axis
            information for axes with a single bin.

            Because the returned Histogram is a view, there is no
            guarantee as to whether it shares axis or contents
            data with the original. Make a copy before modifying
            the new Histogram.

            """

            # Standardize indices into slices
            indices = self._hist._prepare_indices(item)
            indices = tuple(slice(i,i+1) if isinstance(i, (int, np.integer)) else i for i in indices)

            padding = np.zeros((self._hist.ndim, 2), dtype=int)

            new_axes = []
            for dim,(index, axis) in enumerate(zip(indices,
                                                    self._hist._axes)):

                track_overflow = self._hist._track_overflow[dim]

                # Sanity checks not already enforced by Axis.__getitem__
                if not isinstance(index, slice):
                    raise TypeError("slice[] supports only integers and slices as indices")

                start, stop, stride = index.indices(axis.nbins+2*track_overflow)

                if stride != 1:
                    raise IndexError("slice[] does not support non-unit strides")

                # Handle under/overflow
                if track_overflow:

                    if start == 0:
                        if stop-start == 1:
                            raise IndexError(f"slice[] cannot return only underflow bin on axis {dim}")
                    else:
                        padding[dim, 0] = 1 # supply our own, new underflow bin

                    if stop == axis.nbins + 2:
                        if stop-start == 1:
                            raise IndexError(f"slice[] cannot return only overflow bin on axis {dim}")
                    else:
                        padding[dim, 1] = 1 # supply our own, new overflow bin

                    # axes do not reference under/overflow bins
                    axis_start = max(start - 1, 0)
                    axis_stop = min(stop - 1, axis.nbins)

                else:
                    axis_start = start
                    axis_stop = stop

                # result of Histogram slice is a *view*, so we
                # allow result to share edge array with input Histogram
                new_axes.append( axis[axis_start:axis_stop] )


            # new axes will not be referenced outside Axes object
            new_axes = Axes(new_axes, copy_axes=False)

            # get new contents. Pad if we need to add zeros for oflow/uflow.
            new_contents = self._hist._contents[indices]
            new_contents = self._hist._pad(new_contents, padding)

            # apply identical slice to sumw2
            if self._hist._sumw2 is not None:
                new_sumw2_contents = self._hist._sumw2._contents[indices]
                new_sumw2_contents = self._hist._pad(new_sumw2_contents, padding)
                new_sumw2 = self._hist._sumw2._replace(_axes = new_axes,
                                                       _contents = new_sumw2_contents)

            else:
                new_sumw2 = None

            return self._hist._replace(_axes = new_axes,
                                       _contents = new_contents,
                                       _sumw2 = new_sumw2)


    # operation descriptors for every arithmetic operation
    # supported through the _operation() method below.
    class OpType(Enum):
        SUM = 1,
        PRODUCT = 2

    arith_op_properties = {
        # operator          inplace? sum or product op?
        operator.add:      (False,   OpType.SUM),
        operator.sub:      (False,   OpType.SUM),
        operator.mul:      (False,   OpType.PRODUCT),
        operator.truediv:  (False,   OpType.PRODUCT),
        operator.iadd:     (True,    OpType.SUM),
        operator.isub:     (True,    OpType.SUM),
        operator.imul:     (True,    OpType.PRODUCT),
        operator.itruediv: (True,    OpType.PRODUCT),
    }

    def _unit_operation(self, other, operation):
        """
        For binary arithmetic operation self <operation> other,
          - if other is not a Histogram, extract its value w/o units
          - compute the unit that will result from the operation

        Returns:
          tuple (value, new unit)
          If other is a Histogram or sparse or dense array, value == other
          Else, value is an equivalent scalar or np.ndarray
        """

        # Separate between value and unit
        if isinstance(other, Histogram):
            other_unit = other._unit
            other_value = other
        elif isinstance(other, u.Quantity):
            other_unit = other.unit
            other_value = other.value
        elif isinstance(other, u.UnitBase):
            other_unit = other
            other_value = 1
        elif isinstance(other, SparseArray):
            other_unit = None
            other_value = other # cannot use np.asarray
        else: # scalar or array-like
            other_unit = None
            if np.ndim(other) > 0:
                other_value = np.asarray(other)
            else:
                other_value = other

        if self._unit is None and other_unit is None:
            # If neither operand have units, do nothing else
            return other_value, None

        # Adjust other_value and self._unit depending on the operand

        # Standardize dimensionless
        if other_unit is None:
            other_unit = u.dimensionless_unscaled

        self_unit = self._unit
        if self_unit is None:
            self_unit = u.dimensionless_unscaled

        _, optype = Histogram.arith_op_properties.get(operation, (None, None))

        assert (optype is not None), "operation not supported"

        # For * and / the conversion factor is stored in the unit itself
        # ** only accepts scalar dimensionaless quantities, it will crash anyway
        # The idencity operator (for the raterizer) doesn't use the other's units
        if optype == Histogram.OpType.SUM:
            # +, -
            # We need to convert other's units to those of self. If
            # not a no-op, it requires copying the value (as we don't
            # want to modify the original). No change in units
            unit_conv = other_unit.to(self_unit)
            if unit_conv != 1.0:
                other_value = other_value * unit_conv
            new_unit = self_unit

        else: # optype == Histogram.OpType.PROD
            # *, /
            # The conversion factor is stored in the unit itself
            new_unit = operation(self_unit, other_unit)

        return other_value, new_unit

    def _operation(self, other, operation):
        """
        Perform binary arithmetic with first operand a Histogram (self) and
        a second operand 'other', which might be a Histogram, a scalar,
        or an array-like.

        This function is mainly concerned with getting other into a
        form that can be combined with self.  The details of the
        actual operation differ depending on whether operation is
        in-place (e.g., h *= x) or out-of-place (e.g., h = h * x).

        """
        is_inplace, optype = self.arith_op_properties.get(operation, (None, None))

        assert (optype is not None), "Unsupported arithmetic operation"

        # Get the value part of other and the new unit the result should have
        other, new_unit = self._unit_operation(other, operation)

        # convert other into a bare np.ndarray or scalar that can be
        # combined with this Histogram

        if isinstance(other, Histogram):

            # Histograms for operation must have same axes
            if self._axes != other._axes:
                raise ValueError("Axes mismatch")

            # temporarily remove other's units before extracting contents/sumw2
            other_unit = other._unit
            other.to(None, update = False, copy = False)

            # transform other to match overflow/underflow of self
            slices, padding = self._match_track_overflow(other._track_overflow,
                                                         self._track_overflow)

            other_value = other._contents[slices]
            other_value = self._pad(other_value, padding)

            if self._sumw2 is not None:
                if other._sumw2 is not None:
                    # Match over/underflow
                    other_sumw2 = other._sumw2._contents[slices]
                    other_sumw2 = self._pad(other_sumw2, padding)
                else:
                    # self has sumw2, but other does not
                    logger.warning("Other histogram lacks sumw2; assuming zero")
                    other_sumw2 = None
            else:
                if other._sumw2 is not None:
                    # other has sumw2, but self does not
                    logger.warning("Discarding sumw2 from other histogram")
                other_sumw2 = None

            # restore other's units after value extraction
            other.to(other_unit, update = False, copy = False)

        else:
            # other is array or scalar; array-likes were converted by _unit_operation()
            if np.ndim(other) > 0:

                if other.ndim != self.ndim:
                    raise ValueError(f"Operand number of dimensions ({other.ndim}) does not"
                                     f"match number of axes ({self.ndim})")

                if isinstance(other, DOK):
                    # Do not allow DOK format in arithmetic.  If combined with
                    # a dense array, it gives a DOK result, so it can 'pollute'
                    # a Histogram.  Use COO instead; we check later on whether
                    # the result is sparse and update .sumw2 to match if needed.
                    other = other.asformat('coo')

                # single-element axis can be broadcast as-is, so no need for overflow/underflow
                # bins; otherwise, match other's overflow with self
                oshape = np.asarray(other.shape)
                padding = self._get_padding_for_overflow(self._track_overflow,
                                                         self._axes.nbins, oshape,
                                                         mask=(oshape != 1))

                other_value = self._pad(other, padding)
            else:
                # other is scalar
                other_value = other

            other_sumw2 = None # bare value has no sumw2

        if is_inplace:
            self._inplace_operation(other_value, other_sumw2, operation,
                                    optype, new_unit)
            new = self
        else:
            new = self._outofplace_operation(other_value, other_sumw2, operation,
                                             optype, new_unit)

        # Ensure that sumw2 still has same dtype as contents
        # and is sparse if contents is sparse.  An operation
        # on dense self and sparse other can make the result
        # have sparse contents, but it might leave sumw2 dense.
        if new._sumw2 is not None:
            if new.is_sparse and not new._sumw2.is_sparse:
                new._sumw2 = new.sumw2.to_sparse()
            new._sumw2 = new._sumw2.astype(new._contents.dtype, copy=False)

        return new

    def _sumw2_product_op(self, self_sumw2, other_sumw2,
                          self_contents, new_contents,
                          other, operation):
        """
        Update the sum of squared weights self_sumw2 to reflect the impact
        of performing the operation self_contents <operation> other.
        operation is assumed to be a PRODUCT type.

        Args:
          self_sumw2  -- _sumw2._contents for Histogram self
          other_sumw2 -- _sumw2._contents for Histogram other, or
                          None if is lacks sumw2 or is not a Histogram
          self_contents -- _contents for Histogram self before operation
          new_contents  -- _contents for Histogram self after operation
          other         -- other operand's value (_contents if Histogram,
                           or scalar or np.ndarray)
          operation     -- operation performed

        Returns:
          updated sumw2 value for result of operation

        If operation is in-place, self_sumw2 is modified in place
        and returned if possible; otherwise, a new array is allocated
        and returned.  Either way, it is safe to set _sumw2._contents
        to the return value of this function for both in-place and
        out-of-place operations.
        """
        if other_sumw2 is None:
            # Other operaand is assumed to have zero error. Use
            # simplification of error formula below that depends
            # only on prior sumw2 and other's value.
            new_sumw2 = operation(operation(self_sumw2, other), other)
        else:
            # Error of either f = A*B or f = A/B is
            # f_err^2 = f^2 * ((A_err/A)^2 + (B_err/B)^2)
            relvar = self_sumw2 / (self_contents * self_contents)
            other_relvar = other_sumw2 / (other * other)

            new_sumw2 = new_contents * new_contents * (relvar + other_relvar)

        return new_sumw2

    def _inplace_operation(self, other, other_sumw2, operation,
                           optype, new_unit):
        """
        Perform an in-place binary arithmetic operation on the histogram
        self with second operand other.  Update both self's contents
        and its sumw2 value, if present.

        Args:
          other       -- second operand
          other_sumw2 -- second operand's sumw2 matrix, or None
                         if not defined
          operation   -- in-place arithmetic operation to be performed
          optype      -- is operation a SUM or PRODUCT type?
          new_unit    -- unit to assign to result

        self's contents and sumw2 are updated; nothing is returned.
        """
        # delete old units of self; will replace with result units
        self.to(None, update = False, copy = False)

        if self._sumw2 is not None and \
           other_sumw2 is not None and \
           optype == Histogram.OpType.PRODUCT:
            # save a copy of self._contents for sumw2 computation
            self_contents = self._contents.copy()
        else:
            self_contents = None # not used

        # overwrites self._contents
        new_contents = operation(self._contents, other)

        if self._sumw2 is not None:
            self_sumw2_contents = self._sumw2._contents

            if optype == Histogram.OpType.SUM:
                if other_sumw2 is not None:
                    self_sumw2_contents += other_sumw2

            else: # optype == Histogram.OpType.PRODUCT
                self._sumw2._contents = \
                    self._sumw2_product_op(self_sumw2_contents,
                                           other_sumw2,
                                           self_contents,
                                           new_contents,
                                           other,
                                           operation)

        # set unit of result
        self.to(new_unit, update = False, copy = False)

    def _outofplace_operation(self, other, other_sumw2, operation,
                              optype, new_unit):
        """
        Perform an out-of-place binary arithmetic operation on the
        histogram self with second operand other.  Allocate and
        return a new object of the same class as self to hold the result.
        Hence, this function works for subclasses of Histogram as
        well as for the base class.

        Args:
          other       -- second operand
          other_sumw2 -- second operand's sumw2 matrix, or None
                         if not defined
          operation   -- in-place arithmetic operation to be performed
          optype      -- is operation a SUM or PRODUCT type?
          new_unit    -- unit to assign to result

        Returns:
          new object of the same class as self holding result
        """

        # temporarily remove self's units
        self_unit = self._unit
        self.to(None, update = False, copy = False)

        self_contents = self._contents
        new_contents = operation(self_contents, other)

        if self._sumw2 is not None:

            self_sumw2_contents = self._sumw2._contents

            if optype == Histogram.OpType.SUM:
                if other_sumw2 is None:
                    new_sumw2_contents = self_sumw2_contents.copy()
                else:
                    new_sumw2_contents = self_sumw2_contents + other_sumw2

            else: # optype == Histogram.OpType.PRODUCT
                new_sumw2_contents = \
                    self._sumw2_product_op(self_sumw2_contents,
                                           other_sumw2,
                                           self_contents,
                                           new_contents,
                                           other,
                                           operation)
            new_sumw2_unit = None if new_unit is None else new_unit**2
            new_sumw2 = self._sumw2._replace(_contents = new_sumw2_contents,
                                             _unit = new_sumw2_unit)
        else:
            new_sumw2 = None

        # restore unit of self
        self.to(self_unit, update = False, copy = False)

        new = self._replace(_contents = new_contents,
                            _sumw2 = new_sumw2,
                            _unit = new_unit)

        return new

    def __imul__(self, other):

        return self._operation(other, operator.imul)

    def __mul__(self, other):

        return self._operation(other, operator.mul)

    def __rmul__(self, other):

        return self*other

    def __itruediv__(self, other):

        return self._operation(other, operator.itruediv)

    def __truediv__(self, other):

        return self._operation(other, operator.truediv)

    def __rtruediv__(self, other):
        """
        Divide a scalar by the histogram
        """

        if not np.isscalar(other):
            raise ValueError("Inverse operation can only occur between "
                             "histograms or a histogram and a scalar")

        # Temporarily disable self unit
        self_unit = self._unit
        self.to(None, update = False, copy = False)

        # Simple change of unit in this case. Other can't be Quantity or Unit
        new_unit = None if self_unit is None else (1/self_unit).unit

        # Error propagtion of f = b/A (where b is constant, no error) is:
        # f_err^2 = f^2 (A_err/A)^2
        self_contents = self._contents
        new_contents = other/self_contents

        if self._sumw2 is not None:
            new_sumw2_contents = (self._sumw2._contents * other * other /
                                  np.power(self_contents, 4))

            # make sure sumw2's type follows contents (not sure if necessary?)
            new_sumw2_contents = new_sumw2_contents.astype(self._contents.dtype,
                                                           copy=False)

            new_sumw2_unit = None if new_unit is None else new_unit**2

            new_sumw2 = self._sumw2._replace(_contents = new_sumw2_contents,
                                             _unit = new_sumw2_unit)

        # restore self unit
        self.to(self_unit, update = False, copy = False)

        new = self._replace(_contents = new_contents,
                            _sumw2 = new_sumw2,
                            _unit = new_unit)

        return new

    def __iadd__(self, other):

        return self._operation(other, operator.iadd)

    def __add__(self, other):

        return self._operation(other, operator.add)

    def __radd__(self, other):

        return self + other

    def __neg__(self):

        # Temporarily disable self unit
        self_unit = self._unit
        self.to(None, update = False, copy = False)

        new_contents = -(self._contents)

        # restore self unit
        self.to(self_unit, update = False, copy = False)

        # copy sumw2 if it exists, since it is unchanged by negation
        new = self._replace(_contents = new_contents)

        return new

    def __isub__(self, other):

        return self._operation(other, operator.isub)

    def __sub__(self, other):

        return self._operation(other, operator.sub)

    def __rsub__(self, other):

        return -self + other

    def _comparison_operator(self, other, operation):
        other = self._strip_units(other)

        return operation(self._get_contents(), other)

    def __lt__(self, other):
        return self._comparison_operator(other, operator.lt)

    def __le__(self, other):
        return self._comparison_operator(other, operator.le)

    def __gt__(self, other):
        return self._comparison_operator(other, operator.gt)

    def __ge__(self, other):
        return self._comparison_operator(other, operator.ge)

    def rebin(self, *ngroup):

        """
        Rebin a histogram by grouping adjacent bins into one on each axis

        If an axis does not have overflow tracking enabled, any
        partial group along that axis will be discarded.  If it *does*
        have overflow tracking enabled, any partial group's sum will
        be added to the axis' underflow bin if it is on the left, or
        to the overflow bin if it is on the right.

        For histograms with multiple axes, the result of rebinning is
        equivalent to rebinning the input on the first axis, then
        rebinning the result on the second axis, and so forth for all
        axes.

        Args:
            ngroup (int or array-like):
                number of adjacent bins to combine for each axis. If
                this value is > 0 for an axis, binning starts from left
                side of contents, so the last partial group (if any)
                is on the right; if < 0, binning starts from right side,
                so last partial group (if any) is on the left.

        Return:
            a new, rebinned Histogram

        """

        if len(ngroup) == 1:
            if not np.isscalar(ngroup[0]): # a single array-like
                ngroup = ngroup[0]
        else:
            # an array-like of values (must be scalar)
            if not all(np.isscalar(v) for v in ngroup):
                raise ValueError("input to rebin must be scalar or array-like of scalars")

        group_size = np.asarray(ngroup, dtype=int)

        if not group_size.all():
            raise ValueError("ngroup cannot contain 0")

        # number of bins to group on each axis, along with direction
        group_sign = np.broadcast_to(np.sign(group_size), self.ndim)
        group_size = np.broadcast_to(np.abs(group_size), self.ndim)

        # compute edges for each axis after grouping, along with padding necessary
        # for each axis' contents to have the correct size (including any uflow/oflow)
        # after rebinning
        new_axes = []
        padding = []
        slicing = []

        for a, gsz, gsgn, track in zip(self._axes, group_size, group_sign, self._track_overflow):

            # new axis contains every ngroupth bin. If sign is +, we start from
            # bin 0; if -, we shift to ensure last bin is included.

            start = a.nbins % gsz if gsgn < 0 else 0
            new_axes.append( a[start::gsz] )

            # for untracked dimensions, slice away any unused bins

            trim = 0 if track else a.nbins % gsz
            slicing.append( slice(trim, None) if gsgn < 0 else slice(None, a.nbins + 2*track - trim))

            # pad before and after by the minimum amount needed to ensure that
            # padded size is multiple of gsz and any uflow/oflow will be preserved

            p1 = track * (gsz - 1)                      # won't be grouped with contents
            p2 = (gsz - (a.nbins - trim + track)) % gsz # might be grouped with contents
            padding.append( (p1, p2) if gsgn > 0 else (p2, p1) )

        # create new Axes object. *Do* copy the existing Axes so that
        # they do not share edge arrays with the input Histogram's axes.
        new_axes = Axes(new_axes)
        slicing = tuple(slicing)

        # new shape splits each dimension into two; even dims are the
        # size of the array post-rebining, and odd dims are the size
        # of the groups to be summed on that axis

        new_shape = np.empty(2*self.ndim, dtype = int)
        new_shape[0::2] = (self._axes.nbins // group_size) + 2*self._track_overflow
        new_shape[1::2] = group_size

        sum_axes = tuple(range(1, 2*self.ndim, 2)) # axes to be summed away

        # pad and reshape contents matrix prior to summing
        new_contents = self._contents[slicing]
        new_contents = self._pad(new_contents, padding)
        new_contents = np.reshape(new_contents, new_shape)
        new_contents = np.sum(new_contents, axis=sum_axes)

        # apply same rebinning to sumw2 if it exists
        if self._sumw2 is not None:
            new_sumw2_c = self._sumw2._contents[slicing]
            new_sumw2_c = self._pad(new_sumw2_c, padding)
            new_sumw2_c = np.reshape(new_sumw2_c, new_shape)
            new_sumw2_c = np.sum(new_sumw2_c, axis=sum_axes)

            new_sumw2 = self._sumw2._replace(_axes = new_axes,
                                             _contents = new_sumw2_c)
        else:
            new_sumw2 = None

        return self._replace(_axes = new_axes,
                             _contents = new_contents,
                             _sumw2 = new_sumw2)

    def plot(self, ax = None,
             errorbars = None,
             colorbar = True,
             label_axes = True,
             **kwargs):
        """
        Quick plot of the histogram contents.

        Under/overflow bins are not included. Only 1D and 2D histograms
        are supported.

        Histogram with a HealpixAxis will automatically be plotted
        as a map, passing all kwargs to mhealpy's HealpixMap.plot()

        Args:
            ax (matplotlib.axes): Axes on which to draw the histogram. A new
                one will be created by default.
            errorbars (bool or None): Include errorbars for 1D histograms. The
                 default is to plot them if sumw2 is available
            colorbar (bool): Draw colorbar in 2D plots
            label_axes (bool): Label plots axes. Histogram axes must be labeled.
            **kwargs: Passed to `matplotlib.errorbar()` (1D) or
                `matplotlib.pcolormesh` (2D)
        """

        import matplotlib.pyplot as plt
        from mhealpy import HealpixMap
        from .healpix_axis import HealpixAxis

        def without_units(a):
            return a.value if isinstance(a, u.Quantity) else a

        # Matplotlib errorbar and pcolormesh need regular array
        contents = self._get_contents() # contents without units, oflow/uflow
        if self.is_sparse:
            contents = contents.todense()

        # Handle the special case of a healpix axis
        if self.ndim == 1 and isinstance(self._axes[0], HealpixAxis):

            axis = self._axes[0]

            # Pad in case it is partial map
            contents = self._pad(contents,
                                 (axis.lo_lim,
                                  axis.npix - axis.hi_lim))

            m = HealpixMap(data = contents, base = axis)

            args = ()
            if ax is not None:
                args = (ax,)

            plot, ax = m.plot(*args,
                              cbar = colorbar,
                              **kwargs)

            return ax, plot

        # Default errorbars
        if errorbars is None:
            if self._sumw2 is None:
                errorbars = False
            else:
                errorbars = True

        # Create axes if needed (with labels)
        if ax is None:
            fig, ax = plt.subplots()

        # Plot, depending on number of dimensions
        if self.ndim == 1:

            axis = self._axes[0]

            # We have two points per bin (lower edge+center), and 2 extra
            # point for under/overflow (these currently don't have errorbar,
            # they looked bad)
            if axis.unit is None:
                xdata = np.empty(2*axis.nbins + 2)
            else:
                xdata = np.empty(2*axis.nbins + 2)*axis.unit

            xdata[0] = axis.edges[0] # For underflow, first edge
            xdata[1::2] = axis.edges # In between edges. Last edge for overflow
            xdata[2::2] = axis.centers # For markers

            underflow = self._get(-1) if self._track_overflow[0] else 0
            overflow = self._get(axis.nbins) if self._track_overflow[0] else 0

            ydata = np.concatenate(([underflow],
                                    np.repeat(contents, 2),
                                    [overflow]))

            # Style
            drawstyle = kwargs.pop('drawstyle', 'steps-post')

            # Error bars
            yerr = None

            if errorbars:

                errors = without_units(self.bin_error.contents)
                if self.is_sparse:
                    # No auto densify
                    errors = errors.todense()

                yerr = np.empty(2*axis.nbins + 2)
                yerr[2::2] = errors
                yerr[0] = None # No underflow errorbar, looked bad
                yerr[1::2] = None # No overflow errorbar, looked bad

            # Plot
            plot = ax.errorbar(without_units(xdata),
                               ydata,
                               yerr = yerr,
                               drawstyle = drawstyle,
                               **kwargs)

            # Label axes
            if label_axes:
                ax.set_xlabel(axis.label_with_unit)

                if self._unit not in (None, u.dimensionless_unscaled):
                    ax.set_ylabel(f"[{self._unit}]")

        elif self.ndim == 2:

            # No under/overflow
            plot = ax.pcolormesh(without_units(self._axes[0].edges),
                                 without_units(self._axes[1].edges),
                                 np.transpose(contents),
                                 **kwargs)

            if label_axes:
                ax.set_xlabel(self._axes[0].label_with_unit)
                ax.set_ylabel(self._axes[1].label_with_unit)

            if colorbar:

                cax = ax.get_figure().colorbar(plot, ax = ax)

                if self._unit not in (None, u.dimensionless_unscaled):
                    cax.set_label(f"[{self._unit}]")

        else:

            raise ValueError("Plotting only available for 1D and 2D histograms")

        if self._axes[0].axis_scale == 'log':
                ax.set_xscale('log')

        if self.ndim > 1 and self._axes[1].axis_scale == 'log':
                ax.set_yscale('log')

        return ax, plot

    # draw() is an alias of plot()
    draw = plot

    def fit(self, f, lo_lim = None, hi_lim = None, **kwargs):
        """
        Fit histogram data using least squares.

        This is a convenient call to scipy.optimize.curve_fit. Sigma corresponds
        to the output of `h.bin_error`. Empty bins (e.g. error equals 0) are
        ignored

        Args:
            f (callable): Function f(x),... that takes the independent variable
                x as first argument, and followed by the parameters to be fitted.
                For a k-dimensional histogram is should handle arrays of shape
                (k,) or (k,N). The inputs and outputs must be unitless.
            lo_lim (float or array): Low axis limit to fit. One value per axis.
            lo_lim (float or array): High axis limit to fit. One value per axis.
            **kwargs: Passed to scipy.optimize.curve_fit
        """

        from inspect import signature
        from scipy.optimize import curve_fit

        lo_lim = np.broadcast_to(lo_lim, self.ndim, subok = True)
        hi_lim = np.broadcast_to(hi_lim, self.ndim, subok = True)

        # Sanity checks
        for axis,lo,hi in zip(self._axes, lo_lim, hi_lim):
            if ((lo is not None and lo < axis.lo_lim) or
                (hi is not None and hi >= axis.hi_lim)):
                raise ValueError("Fit limits out of bounds")

        # Get bins that correspond to the fit limits
        lim_bins = tuple(slice(None if lo is None else axis.find_bin(lo),
                                None if hi is None else axis.find_bin(hi))
                          for axis,lo,hi
                          in zip(self._axes, lo_lim, hi_lim))

        # Get data to fit
        x = [axis.centers[bins].value
             if axis.unit is not None
             else axis.centers[bins]
             for axis,bins in zip(self._axes,lim_bins)]
        x = np.meshgrid(*x, indexing='ij') # For multi-dimensional histograms
        y = self._get(lim_bins)
        sigma = self.bin_error[lim_bins]

        # Sparse
        if self.is_sparse:
            y = y.todense()
            sigma = sigma.todense()

        # Ignore empty bins
        non_empty = (sigma != 0)
        x = [centers[non_empty] for centers in x]
        y = y[non_empty]
        sigma = sigma[non_empty]

        # Flat matrices
        if self.ndim > 1:
            x = np.asarray([centers.ravel() for centers in x])
            y = y.ravel()
            sigma = sigma.ravel()
        else:
            x = x[0]

        # Sanity checks
        if x.shape[-1] < len(signature(f).parameters) - 1:
            raise RuntimeError("Fewer bins within limits than parameters to fit.")

        # Actual fit with scipy
        return curve_fit(f, x, y, sigma = sigma, **kwargs)

    def write(self, filename, name = "hist", overwrite = False):
        """
        Write histogram to a group in an HDF5 file. Appended if the file already
        exists.

        Args:
            filename (str): Path to file
            name (str): Name of group to save histogram (can be any HDF5 path)
            overwrite (str): Delete and overwrite group if already exists.
        """
        import h5py as h5

        with h5.File(filename, 'a') as f:

            # Will fail on existing group by default
            if name in f:
                if overwrite:
                    del f[name]
                else:
                    raise ValueError("Unable to write histogram. Another group "
                                     "with the same name already exists. Choose "
                                     "a different name or use overwrite")

            self._write(f, name)

    @classmethod
    def open(cls, filename, name = 'hist'):
        """
        Read a Histogram from a specified group in an HDF5 file.
        """
        import h5py as h5

        with h5.File(filename, 'r') as f:
            return cls._open(f[name])

    def _write(self, file, group_name):
        """
        Write histogram to the named group in an HDF5 file.  This method
        can be overriden by subclasses to add additional information to
        the group.

        Args:
            file : HDF5 file handle
            group_name (str): Name of group to save histogram (can be any HDF5 path)
        """

        hist_group = file.create_group(group_name)

        if self._unit is not None:
            hist_group.attrs['unit'] = str(self._unit)

        # Axes. Each one is a data set with attributes.
        # We rely on Axes to return them later in the same
        # order that they are saved.

        axes_group = hist_group.create_group('axes')

        self._axes.write(axes_group)

        if self.is_sparse:
            hist_group.attrs['format'] = 'coo'

            contents_group = hist_group.create_group('contents')

            contents = self._contents

            contents_group.create_dataset('coords',
                                          data = contents.coords,
                                          compression = "gzip",
                                          track_times = False)
            contents_group.create_dataset('data',
                                          data = contents.data,
                                          compression = "gzip",
                                          track_times = False)
            contents_group.create_dataset('shape',
                                          data = contents.shape,
                                          track_times = False)
            contents_group.create_dataset('fill_value',
                                          data = contents.fill_value,
                                          track_times = False)

            if self._sumw2 is not None:
                sumw2_group = hist_group.create_group('sumw2')

                sumw2_contents = self._sumw2._contents

                sumw2_group.create_dataset('coords',
                                           data = sumw2_contents.coords,
                                           compression = "gzip",
                                           track_times = False)
                sumw2_group.create_dataset('data',
                                           data = sumw2_contents.data,
                                           compression ="gzip",
                                           track_times = False)
                sumw2_group.create_dataset('shape',
                                           data = sumw2_contents.shape,
                                           track_times = False)
                sumw2_group.create_dataset('fill_value',
                                           data = sumw2_contents.fill_value,
                                           track_times = False)

        else:
            hist_group.attrs['format'] = 'dense'

            hist_group.create_dataset('contents',
                                      data = self._contents,
                                      track_times = False)

            if self._sumw2 is not None:
                hist_group.create_dataset('sumw2',
                                          data = self._sumw2._contents,
                                          track_times = False)

        return hist_group


    @classmethod
    def _open(cls, hist_group):
        """
        Alternative constructor that reads contents from a group in an
        HDF5 file.  May be overridden just like a regular constructor.

        Args:
            hist_group: group in HDF5 file where data is stored

        Returns:
            New object of type cls (which may be a subclass of Histogram)

        """

        axes, contents, sumw2, unit, track_overflow = Histogram._read_from_hdf(hist_group)

        new = cls.__new__(cls)

        # sanity-checks values and allocates special accessor objects
        Histogram.__init__(new,
                           edges = axes,
                           contents = contents,
                           sumw2 = sumw2,
                           unit = unit,
                           track_overflow = track_overflow,
                           copy_contents = False)

        return new


    @staticmethod
    def _read_from_hdf(hist_group):
        """Read contents of a histogram from a data group.  Return the raw
        contents as a tuple; caller is responsible for creating the
        object.

        Args:
            hist_group: an HD5 group object

        Returns:
            a tuple (axes, contents, sumw2, unit, track_overflow)
            that may be given to the Histogram constructor

        """

        unit = None
        if 'unit' in hist_group.attrs:
            unit = u.Unit(hist_group.attrs['unit'])

        # Axes
        axes_group = hist_group['axes']

        axes = Axes.open(axes_group)

        # Contents
        # Backwards compatible before sparse was supported
        if ('format' not in hist_group.attrs or
            hist_group.attrs['format'] == 'dense'):

            contents = np.asarray(hist_group['contents'])

            sumw2 = None
            if 'sumw2' in hist_group:
                sumw2 = np.asarray(hist_group['sumw2'])

        elif hist_group.attrs['format'] == 'gcxs':

            contents_group = hist_group['contents']

            compressed_axes = None
            if 'compressed_axes' in contents_group:
                compressed_axes = np.asarray(contents_group['compressed_axes'])

            contents = GCXS((np.asarray(contents_group['data']),
                             np.asarray(contents_group['indices']),
                             np.asarray(contents_group['indptr'])),
                            compressed_axes = compressed_axes,
                            shape = tuple(contents_group['shape']),
                            fill_value = np.asarray(contents_group['fill_value']).item())

            sumw2 = None
            if 'sumw2' in hist_group:
                sumw2_group = hist_group['sumw2']

                compressed_axes = None
                if 'compressed_axes' in sumw2_group:
                    compressed_axes = np.asarray(sumw2_group['compressed_axes'])

                sumw2 = GCXS((np.asarray(sumw2_group['data']),
                              np.asarray(sumw2_group['indices']),
                              np.asarray(sumw2_group['indptr'])),
                             compressed_axes = compressed_axes,
                             shape = tuple(sumw2_group['shape']),
                             fill_value = np.asarray(sumw2_group['fill_value']).item())

        elif hist_group.attrs['format'] == 'coo':

            contents_group = hist_group['contents']

            contents = COO(coords = np.asarray(contents_group['coords']),
                           data = np.asarray(contents_group['data']),
                           shape = tuple(contents_group['shape']),
                           fill_value = np.asarray(contents_group['fill_value']).item())

            sumw2 = None
            if 'sumw2' in hist_group:
                sumw2_group = hist_group['sumw2']

                sumw2 = COO(coords = np.asarray(sumw2_group['coords']),
                            data = np.asarray(sumw2_group['data']),
                            shape = tuple(sumw2_group['shape']),
                            fill_value = np.asarray(sumw2_group['fill_value']).item())

        else:
            raise IOError(f"Format {hist_group.attrs['format']} unknown.")

        # Deduce track_overflow based on contents shape
        track_overflow = [size == a.nbins + 2
                          for size,a in zip(contents.shape, axes)]

        return (axes, contents, sumw2, unit, track_overflow)
