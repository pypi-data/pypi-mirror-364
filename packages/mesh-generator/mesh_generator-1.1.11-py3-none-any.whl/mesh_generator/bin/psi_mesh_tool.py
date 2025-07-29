"""This is a translation of the FORTRAN mesh psi_tool.
Generate a one-dimensional mesh.
Input: tmp_mesh_[t/p/r].dat (legacy mesh results)
Output: mesh_res_[t/p/r].txt (a file with mesh points).
"""
import numpy as np


def write_mesh_res_file(output_file_path, input_file_path):
    """Writes a file with mesh points, respective resolution, and cell-to-cell ratio.
    :param input_file_path: input file path.
    :param output_file_path: output file path.
    :return: mesh_res_[t/p/r].txt (a file with mesh points).
    """
    # Open the input file.
    with open(input_file_path, 'r') as f:
        input_data = f.readlines()

    # Get the coordinate label
    label = input_data[1].rstrip('\n')[0]

    # Get the flag to indicate a periodic mesh.
    periodic = input_data[3].rstrip(' \n')
    periodic = is_periodic(periodic)

    # Get the number of mesh points.
    nx = int(input_data[5].rstrip('\n'))
    # Get the domain limits.
    x0 = float(input_data[7].rstrip('\n').split(",")[0])
    x1 = float(input_data[7].rstrip('\n').split(",")[1])

    # Get the node positions.
    xfrac = input_data[9].rstrip('\n')
    xfrac = xfrac[:len(xfrac) - 2]
    xfrac = xfrac.split(",")
    xfrac = [float(item) for item in xfrac]

    # Get the magnification factors.
    dxratio = input_data[11].rstrip('\n')
    dxratio = dxratio[:len(dxratio) - 2]
    dxratio = dxratio.split(",")
    dxratio = [float(item) for item in dxratio]

    # Get the shift amount.
    xshift = float(input_data[13].rstrip('\n'))

    # Get the number of times to filter the mesh.
    nfilt = int(input_data[-1])

    # Generate the mesh.
    c = mesh_coordinate_transforms(label, nx, x0, x1, xfrac, dxratio, nfilt, periodic, xshift)

    # Write the mesh to a text file if requested.
    write_mesh(output_file_path, label, nx, periodic, c)


def mesh_coordinate_transforms(label, nc, c0, c1, frac, dratio, nfilt, periodic, c_shift):
    """Generate a 1D Mesh.
    Input arguments:
            LABEL   : [character(*)]
                      Name for the mesh coordinate (example: 'x').

            NC      : [integer]
                      Number of mesh points to load.

            C0      : [real]
                      The starting location for the coordinate.

            C1      : [real]
                      The ending location for the coordinate.
                      It is required that C1.gt.C0.


            FRAC    : [real array, dimension NSEG]
                       The normalized positions of the mesh segment
                       boundaries (as a fraction of the size of the
                       domain).  For a non-periodic mesh, the first
                       value of FRAC specified must equal 0. and the
                       last value must equal 1.  For a periodic mesh,
                       FRAC must not contain both 0. and 1., since
                       these represent the same point.

            DRATIO  : [real array, dimension NSEG]
                       The ratio of the mesh spacing at the end of a
                       segment to that at the beginning.

            NFILT   : [integer]
                      The number of times to filter the mesh-point
                      distribution array.  Set NFILT=0 if filtering
                      is not desired.  Filtering can reduce
                      discontinuities in the derivative of the mesh
                      spacing.

            PERIODIC: [logical]
                       A flag to indicate whether the mesh to be
                       generated represents a periodic coordinate.
                       If the coordinate is specified as periodic,
                       the range [C0,C1] should be the whole periodic
                       interval; the first mesh point is set at C0
                       and the last mesh point, C(NC), is set at C1.

            C_SHIFT : [real]
                       Amount by which to shift the periodic coordinate.
                       C_SHIFT is only used when PERIODIC=.true.,
                       and is ignored otherwise.  A positive C_SHIFT
                       moves the mesh points to the right.

    Output arguments:

             C       : [real array, dimension NC]
                       The locations of the mesh points.
    """

    eps = 10. ** -5  # epsilon

    # Check that the number of mesh points is valid.
    if nc < 2:
        print('### ERROR in GENMESH:')
        print('### Invalid number of mesh points specified.')
        print('### There must be at least two mesh points.')
        print('Mesh coordinate: ' + str(label) + '. Number of mesh points specified = ' + str(nc))
        return

    # Check that a positive mesh interval has been specified.
    if c0 >= c1:
        print('### ERROR in GENMESH:')
        print('### Invalid mesh interval specified.')
        print('### C1 must be greater than C0.')
        print(' Mesh coordinate: ' + str(label) + ', C0 = ' + str(c0) + ', C1 = ' + str(c1))
        return

    # Find the number of values of FRAC specified.
    nf = len(frac)

    # When no values have been specified (NF=1, the default), a uniform mesh is produced.
    if nf == 1. and frac[0] == 0.:
        cs = [c0, c1]
        r = [1]

    # Check that the specified values of FRAC are monotonically increasing.
    for i in range(1, nf):
        if frac[i] < frac[i - 1]:
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('The values in FRAC must increase monotonically.')
            print('FRAC = ', frac)
            return

    # Check the specified values of FRAC.
    if periodic:
        if frac[0] < 0. or frac[-1] > 1.:
            # A periodic mesh requires the specified values of FRAC to be in the range 0. to 1.
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('For a periodic coordinate, the values in FRAC must be between 0. and 1.')
            print('FRAC = ', frac)
            return

        if frac[0] == 0. and frac[-1] == 1.:
            # A periodic mesh cannot contain both 0. and 1. in FRAC, since these represent the same point.
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('For a periodic coordinate, the values in FRAC must not contain both 0. and 1.')
            print('FRAC = ', frac)
            return

    if not periodic:
        # A non-periodic mesh requires the first specified value of FRAC to be 0., and the last value to equal 1.
        if frac[0] != 0.:
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('For a non-periodic coordinate, the first value of FRAC must equal 0. ')
            print('FRAC = ', frac)
            return

        if frac[-1] != 1.:
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('For a non-periodic coordinate, the last value of FRAC must equal 1. ')
            print('FRAC = ', frac)
            return

    # Check that the required values of DRATIO have been set, and are positive.
    if periodic:
        nr = nf
    else:
        nr = nf - 1

    for i in range(0, nr):
        if dratio[i] <= 0.:
            print('### ERROR in GENMESH:')
            print('### Invalid mesh specification.')
            print('Mesh coordinate: ', label)
            print('A required value in DRATIO has not been set or is not positive.')
            print('DRATIO = ', dratio)
            return

    # Check that an inherently discontinuous mesh has not been
    if periodic and nr == 1 and dratio[0] != 1.:
        print('### WARNING from GENMESH:')
        print('### Discontinuous mesh specification.')
        print('Mesh coordinate: ', label)
        print('An inherently discontinuous mesh has been specified.')
        print('FRAC = ', frac)
        print('DRATIO = ', dratio)

    # Set the number of segments
    ns = nf - 1

    # For a periodic coordinate, add points at XI=0. and XI=1. If they are not already present.
    if periodic:
        if frac[0] != 0.:
            ns = ns + 1
        if frac[-1] != 1.:
            ns = ns + 1

    # allocate cs and r
    cs, r = [None] * (int(ns + 1)), [None] * int(ns)

    # Set up the coordinate limits of the segments.
    if periodic:
        if frac[0] != 0.:
            # allocate cs and r
            cs[0] = c0
            cs[1:] = [c0 + (c1 - c0) * x for x in frac]
            if frac[nf - 1] != 1.:
                alpha = (1. - frac[-1]) / (frac[0] + 1. - frac[-1])
                r[0] = dratio[-1] / (1. + alpha * (dratio[-1] - 1.))
                r[1:] = dratio
                cs[-1] = c1
                r[-1] = 1. + alpha * (dratio[-1] - 1.)
            else:
                r[0] = dratio[-1]
                r[1:nr] = dratio[:nr - 1]
        else:
            cs = [c0 + (c1 - c0) * x for x in frac]
            cs.append(c1)
            r = dratio
    else:
        cs = [c0 + (c1 - c0) * x for x in frac]
        r = dratio

    # convert to numpy arrays
    cs = np.asarray(cs)
    r = np.asarray(r)

    # allocate xi, a, f
    xi = np.zeros(int(ns + 1))
    a = np.zeros(int(ns))
    f = np.zeros(int(ns))

    # Compute the XI values at the segment limits.
    for i in range(0, ns):
        dr = r[i] - 1.
        if abs(dr) < eps:
            f[i] = (cs[i + 1] - cs[i]) * (1. + 0.5 * dr)
        else:
            f[i] = (cs[i + 1] - cs[i]) * np.log(r[i]) / dr

    fac = 0.
    for i in range(ns - 1, -1, -1):
        fac = fac / r[i] + f[i]

    d = f[0] / fac
    xi[0] = 0.
    for i in range(1, ns):
        xi[i] = xi[i - 1] + d
        if i < ns - 1:
            d = d * f[i] / (f[i - 1] * r[i - 1])
    xi[ns] = 1.

    # Set the amplification factor for each segment.
    for i in range(0, ns):
        a[i] = np.log(r[i]) / (xi[i + 1] - xi[i])

    # For a periodic coordinate, find the XI shift corresponding to a shift of C_SHIFT in the coordinate.
    # Note that a positive value of C_SHIFT moves the mesh points to the right.
    if periodic:
        xi_shift = map_c_to_xi(periodic, ns, xi, cs, a, r, -c_shift, eps)
    else:
        xi_shift = 0.

    # Compute the location of the mesh points in array C by mapping from the XI values.
    dxi = 1. / (nc - 1.)
    c = np.zeros(nc)
    c[0] = c0
    for j in range(2, nc):
        xiv = (j - 1) * dxi
        c[j - 1] = map_xi_to_c(periodic, ns, xi, cs, a, r, -c_shift, xi_shift, xiv, eps)
    c[nc - 1] = c1

    # Filter the mesh if requested
    if nfilt > 0:
        for i in range(0, nfilt):
            if periodic:
                c = filter_coord_periodic(c1 - c0, nc, c)
            else:
                c = filter_coord(nc, c)
    return c


def write_mesh(fname, label, nc, periodic, c):
    """Write a one-dimensional mesh to file FNAME."""
    with open(fname, 'w') as f:
        # allocate dc and rc
        dc = c - np.roll(c, 1)
        if periodic:
            dc[0] = dc[nc - 1]
        rdc = dc / np.roll(dc, 1)
        if periodic:
            rdc[0] = rdc[nc - 1]

        f.write("i	" + label + "	d" + label + "	ratio\n")
        if periodic:
            j0 = 1
        else:
            j0 = 3
            f.write('{0: >8}'.format('1') + "\t " + "{:.14E}".format(c[0]) + "    " +
                    "{:.14E}".format(dc[1]) + "\t " + "{:.14E}".format(rdc[2]) + "\n")
            f.write('{0: >8}'.format('2') + "\t " + "{:.14E}".format(c[1]) + "\t " +
                    "{:.14E}".format(dc[1]) + "\t " + "{:.14E}".format(rdc[2]) + "\n")
        for j in range(j0, nc + 1):
            f.write('{0: >8}'.format(j) + "\t " + "{:.14E}".format(c[j - 1]) + "\t " +
                    "{:.14E}".format(dc[j - 1]) + "\t " + "{:.14E}".format(rdc[j - 1]) + "\n")


def filter_coord(n, f):
    """
    Apply a "(1,2,1)/4" low-pass digital filter to a 1D coordinate.
    The end-points F(1) and F(N) are not changed.
    """
    # Make a copy of the function.
    ff = np.copy(f)

    # Apply the filter.
    for i in range(1, n - 1):
        f[i] = 0.25 * (ff[i - 1] + 2. * ff[i] + ff[i + 1])

    return f


def filter_coord_periodic(xl, n, f):
    """
    Apply a "(1,2,1)/4" low-pass digital filter to a periodic 1D coordinate.
    XL is the periodic interval for the coordinate.
    The filtered coordinate is translated so that F(1) is preserved.
    """
    ff = np.zeros(n + 2)
    # Save the value of F(1).
    f1old = f[0]
    # Make a periodic copy of the function.
    ff[1: n + 1] = f
    ff[0] = f[int(n - 2)] - xl
    ff[n + 1] = f[1] + xl
    # Apply the filter:
    for i in range(0, n):
        f[i] = 0.25 * (ff[i] + 2. * ff[i + 1] + ff[i + 2])
    # Translate F so that F(1) is preserved.
    f1new = f[0]
    for i in range(0, n):
        f[i] = f[i] - f1new + f1old
    return f


def map_xi_to_c(periodic, ns, xi, cs, a, r, cshft, xi_shift, xiv, eps):
    """
    Get the mesh coordinate value CV for the specified xi value XIV.
    Set PERIODIC=.true. for a periodic coordinate. NS is the number of segments in the mesh definition.
    The arrays XI, CS, A, and R define the mesh mapping.
    CSHFT represents the amount to shift a periodic coordinate.
    XI_SHIFT represents the corresponding amount to shift xi.
    This is a utility routine for GENMESH.
    """
    # Find the index of the segment to which XIV belongs.
    if periodic:
        # Shift XIV by XI_SHIFT.
        xiv_p = xiv + xi_shift
        # Fold XIV_P into the main interval.
        xiv_p = fold(0., 1., xiv_p)
    else:
        xiv_p = xiv

    for i in range(0, ns):
        if xi[i] <= xiv_p <= xi[i + 1]:
            break

    d = xiv_p - xi[i]
    d1 = xi[i + 1] - xi[i]
    da = a[i] * d
    da1 = a[i] * d1

    # Interpolate the mapping function at XIV_P.
    if abs(da1) < eps:
        fac = (d * (1. + 0.5 * da)) / (d1 * (1. + 0.5 * da1))
    else:
        fac = (np.exp(da) - 1.) / (r[i] - 1.)
    cv = cs[i] + (cs[i + 1] - cs[i]) * fac

    if periodic:
        # Shift CV by the amount CSHFT.
        cv = cv - cshft
        # Fold CV into the main interval.
        cv = fold(cs[0], cs[ns], cv)
    return cv


def map_c_to_xi(periodic, ns, xi, cs, a, r, cv, eps):
    """
    Get the xi value XIV for the specified coordinate value CV.
    Set PERIODIC=.true. for a periodic coordinate.
    NS is the number of segments in the mesh definition.
    The arrays XI, CS, A, and R define the mesh mapping.
    This is a utility routine for GENMESH.
    """
    # Find the index of the segment to which CV belongs.
    if periodic:
        # Fold CV_P into the main interval.
        cv_p = fold(cs[0], cs[ns], cv)
    else:
        cv_p = cv

    for i in range(0, ns):
        if cs[i] <= cv_p <= cs[i + 1]:
            break

    d = (cv_p - cs[i]) / (cs[i + 1] - cs[i])
    da = (r[i] - 1.) * d

    # Interpolate the mapping function at XIV_P.
    if abs(da) < eps:
        fac = d * (xi[i + 1] - xi[i])
    else:
        fac = np.log(da + 1.) / a[i]

    xiv = xi[i] + fac
    return xiv


def fold(x0, x1, x):
    """
    "Fold" X into the periodic interval [X0,X1].
    On return, X is such that X0.le.X.lt.X1.
    It is assumed that X0 does not equal X1, as is physically necessary.
    If X0 and X1 are equal, the routine just returns with FOLD=X.
    :param x0: begin mesh coordinate
    :param x1: end mesh coordinate
    :param x: shift
    """
    if x0 == x1:
        return x
    xl = x1 - x0
    x = ((x - x0) % xl) + x0
    if x < x0:
        x = x + xl
    if x >= x1:
        x = x - xl
    return x


def is_periodic(state):
    if state == ".true.":
        return True
    if state == ".false.":
        return False
    else:
        return False
