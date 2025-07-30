"""
Feature testing and version-dependent definitions
"""

import numpy as np

# test for NumPy 1.x
try:
    NUMPY_LT_2 = (int(np.__version__.split('.')[0]) < 2)
except TypeError:
    # Make sphinx autodocs mock module work
    NUMPY_LT_2 = True

# NumPy copying semantics in np.array() changed from 1.x to 2.x in
# a way that impacts histpy's use of AstroPy's units.Quantity. See
# https://gitlab.com/burstcube/histpy/-/merge_requests/4 .
COPY_IF_NEEDED = False if NUMPY_LT_2 else None
