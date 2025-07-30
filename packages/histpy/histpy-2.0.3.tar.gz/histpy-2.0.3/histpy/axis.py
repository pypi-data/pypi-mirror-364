import logging
logger = logging.getLogger(__name__)

import operator

from copy import deepcopy

import numpy as np

import astropy.units as u

from .feature import COPY_IF_NEEDED

class Axis:
    """
    Bin edges. Optionally labeled

    You can select specific edges using the slice operator (:code:`[]`).
    The result is also another Axis object.

    Args:
        edges (array-like): Bin edges. Can be a Quantity array, if you need units
        label (str): Label for axis. If edges is an Axis object, this will
            override its label
        scale (str): Bin center mode e.g. `"linear"` or `"log"`.
            See `axis_scale` property. If edges is an Axis
            object, this will override its mode
        unit  (unit-like): Unit for axis (will override unit of edges)
        copy (bool): True if edge array should be distinct from passed-in
                     edges; if False, will use same edge array if possible
    """

    def __init__(self, edges, label = None, scale = None, unit = None,
                 copy=True):

        copy_edges = True if copy else COPY_IF_NEEDED
        unit = None if unit is None else u.Unit(unit)

        if isinstance(edges, Axis):
            self._edges = np.array(edges._edges, copy=copy_edges)

            if unit is None:
                self._unit = edges._unit
            else:
                self._unit = unit
                if edges._unit is not None: # convert axis values
                    factor = edges._unit.to(self._unit)
                    if factor != 1.0:
                        self._edges *= factor

            #Overrides
            self._label = edges._label if label is None else label

            # must use setter to validate scale
            self.axis_scale = edges._scale if scale is None else scale

        else:
            if isinstance(edges, u.Quantity):
                if unit is None:
                    self._unit = edges._unit
                else:
                    self._unit = unit
                    if edges._unit is not None: # convert axis values
                        edges = edges.to_value(self._unit)
            else:
                self._unit = unit

            self._edges = np.array(edges, copy=copy_edges)

            self._validate_edges(self._edges)

            self._label = label

            # must use setter to validate scale
            self.axis_scale = 'linear' if scale is None else scale

    def copy(self):
        """
        Make a deep copy of self
        """
        return self._copy()

    def __deepcopy__(self, memo):
        """
        Hook for deepcopy()
        """

        self._memo = memo # cache memo dict in case we need it
        new = self._copy()
        del self._memo

        return new

    def replace_edges(self, edges, copy=True):
        """
        Replace edge array of self (see _copy documentation)
        """

        # Handle edges with units
        if isinstance(edges, u.Quantity):
            edges = edges.to_value(self.unit)

        # Handle iterables that are not arrays
        edges = np.asarray(edges)

        return self._copy(edges, copy)

    def _copy(self, edges=None, copy_edges=True):
        """
        Make a deep copy of an Axis, optionally replacing the edge
        array.  The copy shares no *writable* members with the
        original; the only shared members are those that will never be
        mutated.

        This function preserves subclass types if called from a
        derived class.  Subclasses with additional data members
        may override this function; if they do not, their
        data members will be deepcopied.

        If the edge array is replaced, the new array will be validated.

        Args:
           edges: np.ndarray
             new array of edges; if None, use edges of self
           copy_edges: bool
             copy edges before assigning to Axis (default True)
        Returns:
            new object of same type of self

        """

        cls = self.__class__
        new = cls.__new__(cls)

        if edges is not None: # new edge array
            self._validate_edges(edges)
            new._edges = edges.copy() if copy_edges else edges
        else: # copy existing array
            new._edges = self._edges.copy()

        # these values are immutable so need not be deepcopied
        new._unit  = self._unit
        new._label = self._label
        new._scale = self._scale

        if cls != Axis and cls._copy == Axis._copy: # _copy not overridden
            self_dict = vars(self)
            new_dict  = vars(new)

            # if we were called from __deepcopy__(), pass along
            # the supplied memo object to recursive deepcopy calls.
            kwargs = {}
            if hasattr(self, '_memo'):
                kwargs['memo'] = self._memo

            # don't copy the temporary _memo field recursively
            for member in self_dict.keys() - new_dict.keys() - { '_memo' }:
                setattr(new, member, deepcopy(self_dict[member], **kwargs))

        return new


    @staticmethod
    def _validate_edges(edges):

        if edges.ndim != 1:
            raise ValueError("Bin edges list must be a 1-dimensional array")

        if len(edges) < 2:
            raise ValueError("Axis needs at least two bin edges")

        if np.any(edges[1:] <= edges[:-1]):
            raise ValueError("All bin edges must be strictly monotonically"
                             " increasing")

    @property
    def unit(self):
        """
        Return the astropy units of the axis. Or ``None`` is units where not declare.
        """

        return self._unit

    def to(self, unit, equivalencies=[], update=True, copy=True):
        """
        Convert an Axis to a different unit.

        Args:
            unit (unit-like): Unit to convert to.
            equivalencies (list or tuple): A list of equivalence pairs to try if the units are not
                directly convertible.
            update (bool): If ``update`` is ``False``, only the units will be changed without
                updating the edges accordingly
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
            # Apply factor needed to convert to new unit to edges
            if old_unit is None:
                if new_unit is not None and new_unit != u.dimensionless_unscaled:
                    raise TypeError("Axis without units")
            elif new_unit is not None:
                factor = old_unit.to(new_unit, equivalencies = equivalencies)
                if factor != 1.0:
                    new._edges *= factor

        # Update units
        new._unit = new_unit

        return new

    @property
    def axis_scale(self):
        """
        Control what is considered the center of the bin. This affects
        `centers()` and interpolation.

        Modes:
            - linear (default): The center is the midpoint between the bin edges
            - symmetric: same as linear, except for the first center, which
              will correspond to the lower edge. This is, for example, useful
              when the histogram is filled with the absolute value of a
              variable.
            - log: The center is the logarithmic (or geometrical) midpoint between
              the bin edges.
        """

        return self._scale

    @axis_scale.setter
    def axis_scale(self, mode):
        """
        Set the mode of the axis and make sure it is set to a valid value
        """

        if mode not in {'linear', 'symmetric', 'log'}:
            raise ValueError(f"Bin center mode '{mode}' not supported")

        if mode == 'log' and self._edges[0] <= 0:
            raise ArithmeticError("Bin center mode 'log' can only be assigned "
                                  "to axes starting at a positive number")

        self._scale = mode

    def __array__(self, dtype=None, copy=None):
        """
        Return a view or copy of our edges
        """
        if dtype is not None and self._edges.dtype != dtype:
            return self._edges.astype(dtype) # makes a copy
        elif copy:
            return self._edges.copy()
        else:
            return self._edges

    def __len__(self):
        return len(self._edges)

    def __eq__(self, other):

        return (self._unit == other._unit
                and
                self._scale == other._scale
                and
                self._label == other._label
                and
                np.array_equal(self._edges, other._edges)) # false if lengths differ

    def __getitem__(self, key):
        """
        Get a slice of this axis.  Indices for slice
        are assumed to specify *bins*; hence,
        slice(start,stop) asks for edges[start:stop+1].
        Slice is a *view* of existing Axis, not a copy
        """

        if isinstance(key, int):

            if key < 0:
                key += self.nbins # given with respect to end of array

            key = slice(key, key+1)

        if isinstance(key, slice):

            # clips indices > self.nbins to = self.nbins
            start,stop,stride = key.indices(self.nbins)

            stop += 1 # convert from bins to endpts

            if stop <= start:
                raise IndexError("Axis slices cannot reverse the bin order.")
            elif stop == start + 1:
                raise IndexError("Axis slice must have a least one bin")
            if stride < 1:
                raise IndexError("Step must be positive when getting an axis slice.")

            key = slice(start, stop, stride)

        else:
            raise TypeError("Axis slice operator supports only integers and slices")

        new_edges = self._edges[key]

        return self._copy(new_edges, copy_edges=False)

    def _strip_units(self, quantity):
        """
        Remove the unit from a quantity (if it exists) and return
        its value in the units of the Axis, so that we may combine
        it with the Axis's contents.  Avoid copying an input
        Quantity array if possible.

        We FAIL if:
          * we try to combine a non-dimensionless Quantity with
            a Histogram that has no units
          * we try to combine a scalar with an Axis that has
            units
        """

        # convert bare unit to trivial Quantity
        if isinstance(quantity, u.UnitBase):
            quantity = 1. * quantity

        if isinstance(quantity, u.Quantity):

            if quantity.unit == u.dimensionless_unscaled:
                return quantity.value

            if self._unit is None:
                raise u.UnitConversionError("Cannot apply Quantity to Axis without units")

            return quantity.to_value(self._unit)

        else:

            if self._unit is not None:
                raise u.UnitConversionError("Cannot apply scalar to Axis with units")

            return quantity

    def find_bin(self, value, right=False):
        """
        Return the bin `value` corresponds to.

        Args:
            value: scalar or np.ndarray
               value(s) to bin
            right: bool
               If false, a bin strictly includes its left edge
               If true, a bin strictly includes its right edge
        Return:
            int: Bin number. -1 for underflow, `nbins` for overflow
        """

        value = self._strip_units(value)

        dir = 'left' if right else 'right' # yes, really
        return np.searchsorted(self._edges, value, dir) - 1

    def interp_weights(self, values):
        """
        Get the two closest bins to each value in `values`, together
        with the weights to linearly interpolate between the centers
        of these two bins.

        If the axis has log scale, interpolation weights are computed
        in the log domain, and `values` must be > 0.

        Before interpolation, values are be clamped to be at least
        the center of the first bin and at most the center of the last
        bin.

        Return:
            Bins: int array containing left and right bins for each value,
            of shape
               (2,) if values is scalar or 0-D array,
               (2, values.shape) otherwise
            Weights: float array containing left and right weights for
            each value, of shape
               (2,) if values is scalar or 0-D array,
               (2, values.shape) otherwise

        NB: return values are for compatibility with old code; it
        would suffice to return bins[0] and weights[0], since
        bins[1] = bins[0] + 1 and weights[1] = 1. - weights[0].

        """

        values = self._strip_units(values)

        # scalar or 0-D array
        isscalar = np.isscalar(values) or \
            ( isinstance(values, np.ndarray) and values.ndim == 0)

        values = np.atleast_1d(values)

        if self._scale == 'log': # bin centers will be in log domain
            values = np.log(values)

        centers = self._get_centers()

        # clamp out-of-range values to centers of edge bins
        values = np.clip(values, centers[0], centers[-1])

        # identify bin with greatest center <= each value;
        # this is the left flanking bin
        b0 = np.searchsorted(centers, values, side='left') - 1

        # assign value exactly at leftmost center to first bin
        b0[b0 == -1] = 0

        # compute interpolating weights
        w0 = (centers[b0+1] - values) / np.diff(centers)[b0]

        # materialize right bin and weight
        bins    = np.stack((b0, b0 + 1))
        weights = np.stack((w0, 1. - w0))

        # if just one value, return its bins/weights, rather than lists
        if isscalar:
            return ( bins[:,0], weights[:,0] )
        else:
            return ( bins, weights )

    def _with_units(self, a):
        """
        Return a version of value a in the units of this Axis, if any.
        Do not copy a unless needed.
        """
        if self._unit is None:
            return a
        else:
            return u.Quantity(a, unit=self._unit, copy=COPY_IF_NEEDED)

    @property
    def lower_bounds(self):
        '''
        Lower bound of each bin
        '''

        return self._with_units(self._edges[:-1])

    @property
    def upper_bounds(self):
        '''
        Upper bound of each bin
        '''

        return self._with_units(self._edges[1:])

    @property
    def bounds(self):
        '''
        Start of [lower_bound, upper_bound] values for each bin.
        '''

        lower = self._edges[:-1]
        upper = self._edges[1:]
        return self._with_units(np.transpose((lower, upper)))

    @property
    def lo_lim(self):
        """
        Overall lower bound
        """

        return self._with_units(self._edges[0])

    @property
    def hi_lim(self):
        """
        Overall upper bound of histogram
        """

        return self._with_units(self._edges[-1])

    @property
    def edges(self):
        """
        Edges of each bin
        """

        return self._with_units(self._edges)

    @property
    def label(self):
        """
        Axis label
        """
        return self._label

    @label.setter
    def label(self, new_label):
        self._label = new_label

    @property
    def label_with_unit(self):
        """
        Axis 'label [units]'
        """

        strs = []
        if self._label is not None:
            strs.append(f"{self._label}")

        if self._unit not in (None, u.dimensionless_unscaled):
            strs.append(f"[{self._unit}]")

        return " ".join(strs)

    @property
    def centers(self):
        '''
        Center of each bin, in linear domain and axis units, if any
        '''

        centers = self._get_centers()

        if self._scale == 'log':
            centers = np.exp(centers)

        return self._with_units(centers)

    def _get_centers(self):
        '''
        If scale is not logarithmic, center of each bin
        If scale is logarithmic, center of each bin in log domain
        '''

        if self._scale == 'log':
            edges = np.log(self._edges)
        else:
            edges = self._edges

        centers = 0.5*(edges[1:] + edges[:-1])
        if self._scale == 'symmetric':
            centers[0] = edges[0]

        return centers

    @property
    def widths(self):
        '''
        Width of each bin.
        '''

        return self._with_units(np.diff(self._edges))

    @property
    def nbins(self):
        """
        Number of elements along each axis. Either an int (1D histogram) or an
        array
        """

        return len(self._edges) - 1

    def _enforce_unitless(self, value, error_message = None):

        if isinstance(value, u.UnitBase):
            unit = value
            v = 1
        elif isinstance(value, u.Quantity):
            unit = value.unit
            v = value.value
        else:
            unit = u.dimensionless_unscaled
            v = value

        if unit != u.dimensionless_unscaled:
            raise TypeError(error_message)

        return v

    def _ioperation(self, other, operation):

        if self._unit is None or operation in (operator.imul, operator.itruediv):
            # If the axis doesn't have units, then both shifting and
            # scaling operator must be unitless
            # Scaling operator must alway be unitless, independently of
            # whether the axis has units or not

            other = self._enforce_unitless(other,
                                           "Operations with dimensional quantities "
                                           "are not allowed")

        else:

            # Shift operations (+/-) must have the same units as the axis
            other = self._strip_units(other)

        self._edges = operation(self._edges, other)

        # if other is not scalar, op can break monotonicity
        if np.any(self._edges[1:] <= self._edges[:-1]):
            raise ValueError("All bin edges must be strictly monotonically"
                             " increasing")

        return self

    def _operation(self, other, operation):

        new = self.copy()
        new = new._ioperation(other, operation) # modifies edges in place
        return new

    def __imul__(self, other):
        return self._ioperation(other, operator.imul)

    def __mul__(self, other):
        return self._operation(other, operator.imul)

    def __rmul__(self, other):
        return self*other

    def __itruediv__(self, other):
        return self._ioperation(other, operator.itruediv)

    def __truediv__(self, other):
        return self._operation(other, operator.itruediv)

    # No rtruediv nor rsub. Bins must be monotonically increasing

    def __iadd__(self, other):
        return self._ioperation(other, operator.iadd)

    def __add__(self, other):
        return self._operation(other, operator.iadd)

    def __radd__(self, other):
        return self + other

    def __isub__(self, other):
        return self._ioperation(other, operator.isub)

    def __sub__(self, other):
        return self._operation(other, operator.isub)

    def _write(self, axes_group, name):
        """
        Save all needed information to recreate Axis into
        a HDF5 group.  Subclasses may override

        Returns: dataset holding axis
        """

        axis_set = axes_group.create_dataset(name,
                                             data = self._edges,
                                             track_times = False)

        axis_set.attrs['__class__'] = (self.__class__.__module__,
                                       self.__class__.__name__)

        axis_set.attrs['scale'] = self._scale

        if self._label is not None:
            # HDF5 doesn't support unicode
            axis_set.attrs['label'] = str(self._label)

        if self._unit is not None:
            axis_set.attrs['unit'] = str(self._unit)

        return axis_set

    @classmethod
    def _open(cls, dataset):
        """
        Create Axis from HDF5 dataset
        Written as a virtual constructor so that
        subclasses may override
        """

        edges = np.asarray(dataset)

        # back-compatibility with old version of Axis
        # that stored edges as Quantity if it had units
        if isinstance(edges, u.Quantity):
            unit = edges.unit
            edges = edges.value

        if 'unit' in dataset.attrs:
            unit = u.Unit(dataset.attrs['unit'])
        else:
            unit = None

        if 'label' in dataset.attrs:
            label = dataset.attrs['label']
        else:
            label = None

        if 'scale' in dataset.attrs:
            scale = dataset.attrs['scale']
        else: # legacy HealpixAxis writes did not always have this
            scale = 'linear'

        new = cls.__new__(cls)
        Axis.__init__(new,
                      edges = edges,
                      unit = unit,
                      scale = scale,
                      label = label,
                      copy = False)

        return new
