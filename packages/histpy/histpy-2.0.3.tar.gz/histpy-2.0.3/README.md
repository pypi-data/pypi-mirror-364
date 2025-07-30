# The histpy library

The histpy library provides a `Histogram` class which is, essentially, an array with axes attached defining the bin boundaries. The histpy library class is loosely based on [ROOT's histogram](https://root.cern/manual/histograms/) but using a more pythonic interface.

Full documentation: https://histpy.readthedocs.io

The histpy library supports:
- Histograms with an arbitrary number of dimensions.
- Numpy-like element indexing.
- Multiple operations: projection, slicing, addition, multiplication, concatenation, rebinning, fitting, interpolation and plotting.
- Tracking of under and overflow contents along each axes.
- Weighted histograms.
- Automatic error propagation.
- [Astropy's units](https://docs.astropy.org/en/stable/units/index.html), both for the histogram contents and the axis edges.
- Spherical coordinates axes, using the [HEALPix](https://healpix.sourceforge.io/) grid.
- [Sparse](https://sparse.pydata.org/en/stable/) contents
- I/O to/from [HDF5](https://www.hdfgroup.org/solutions/hdf5/) files.

## Breaking changes

This section only summarizes non-backward compatible API changes. See [CHANGELOG.md](CHANGELOG.md) for the full list of changes and further details.

### Version 2.0.0

- `Histogram` no longer tracks under and overflow contents by default. To get the old behavior either set `track_overflow = True` or initialize the contents with a shape that includes the under and overflow bins.
- `Axis.to()` now returns a new `Axis` object by default, instead of modifying it in place. To get the old behavior, add the argument `copy = False`.
- The output format of `Axes.interp_weights()` has changed. Previously, it returned all bins and weights combinations needed for the interpolation. It now returns interpolation indices and weights for each individual dimension. If the user wishes to recover the points and weights in the old format, this may be done with the following code snippet:
    ```python
    bins_old = np.asarray(list(itertools.product(*bins_new)))
    weights_old = np.prod(np.array(list(itertools.product(*weights_new))), axis = 1)
    ```
- The `Axes.__array__()` interface has been removed. 
