# @file cellbuilder_tools.py
#  Contains routines for building unit cells with adsorbed species.
#
#  Written by JP Janet for HJK Group
#
#  Dpt of Chemical Engineering, MIT

import re

import numpy
try:
    from openbabel import openbabel  # version 3 style import
except ImportError:
    import openbabel  # fallback to version 2
import copy
from math import sqrt, pi
from molSimplify.Classes.globalvars import globalvars
from molSimplify.Classes.mol3D import mol3D
from molSimplify.Scripts.geometry import distance


###############################
# Main cell FF opt routine
#
#  optimize complexes placed on cell to avoid clashes. Will use UFF for speed
#
#  @param ff Force field to use, available MMFF94, UFF, Ghemical, GAFF,
#  @param mol mol3D of cell to be optimized
#  @param frozenats List of frozen atom indices, will usually be the cell
#  @return FF-calculated energy, mol3D of optimized cell


def cell_ffopt(ff, mol, frozenats):
    ### FORCE FIELD OPTIMIZATION ##
    # INPUT
    #   - ff: force field to use, available MMFF94, UFF< Ghemical, GAFF
    #   - mol: mol3D to be ff optimized
    # OUTPUT
    #   - mol: force field optimized mol3D
    metals = list(range(21, 31))+list(range(39, 49))+list(range(72, 81))
    # check requested force field
    ffav = 'mmff94, uff, ghemical, gaff, mmff94s'  # force fields
    if ff.lower() not in ffav:
        print('Requested force field not available. Defaulting to UFF')
        ff = 'UFF'
    # convert mol3D to OBMol via xyz file, because AFTER/END option have coordinates
    backup_mol = mol3D()
    backup_mol.copymol3D(mol)
    mol.convert2OBMol()
    # initialize constraints
    constr = openbabel.OBFFConstraints()
    # openbabel indexing starts at 1 ### !!!
    # convert metals to carbons for FF
    indmtls = []
    mtlsnums = []
    for iiat, atom in enumerate(openbabel.OBMolAtomIter(mol.OBMol)):
        if atom.GetAtomicNum() in metals:
            indmtls.append(iiat)
            mtlsnums.append(atom.GetAtomicNum())
            atom.SetAtomicNum(6)
    for cat in frozenats:
        constr.AddAtomConstraint(cat+1)  # indexing babel
    # set up forcefield
    forcefield = openbabel.OBForceField.FindForceField(ff)
    forcefield.Setup(mol.OBMol, constr)
    # force field optimize structure
    forcefield.ConjugateGradients(2500)
    forcefield.GetCoordinates(mol.OBMol)
    # reset atomic number to metal
    for i, iiat in enumerate(indmtls):
        mol.OBMol.GetAtomById(iiat).SetAtomicNum(mtlsnums[i])
    mol.convert2mol3D()
    en = forcefield.Energy()

    del forcefield, constr
    return mol, en
################################
###############################
# Import CIF to mol3D
#
#  @param fst string of  .cif file path
#  @return mol3D of unit cell, cell vector


def import_from_cif(fst, return_extra_cif_info=False):
    # INPUT:
    # fst:  filename of cif file
    # OUTPUT:
    # unit_cell:  mol3D class of a single unit cell
    # cell_vector: list of lists of floats, each
    #           corresponds to one of the defining cell
    #           vectors
    cell_vector = list()
    unit_cell = mol3D()
    A = 0
    B = 0
    C = 0
    alpha = 0
    beta = 0
    emsg = list()
    exit_status = 0
    gamma = 0
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("cif", "xyz")
    mol = openbabel.OBMol()
    if obConversion.ReadFile(mol, fst):
        fillUC = openbabel.OBOp.FindType("fillUC")
        fillUC.Do(mol, "strict")
        unit_cell.OBMol = mol
        unit_cell.convert2mol3D()
    else:
        emsg.append("Error in reading of cif file by openbabel")
        exit_status = 1
    with open(fst, errors='ignore') as f: # ignore takes care of unicode errors in some cifs
        lines = f.readlines()
        for line in lines:
            linesplit = line.split()
            if len(linesplit) != 0:
                if linesplit[0] == "_cell_length_a":
                    A = float((re.sub(r'\([^)]*\)', '',
                                      ''.join(c for c in linesplit[1]))))
                if linesplit[0] == "_cell_length_b":
                    B = float((re.sub(r'\([^)]*\)', '',
                                      ''.join(c for c in linesplit[1]))))
                if linesplit[0] == "_cell_length_c":
                    C = float((re.sub(r'\([^)]*\)', '',
                                      ''.join(c for c in linesplit[1]))))

                if linesplit[0] == "_cell_angle_alpha":
                    alpha = float(
                        ''.join(c for c in linesplit[1] if c not in '()').rstrip('.'))
                if linesplit[0] == "_cell_angle_beta":
                    beta = float(
                        ''.join(c for c in linesplit[1] if c not in '()').rstrip('.'))
                if linesplit[0] == "_cell_angle_gamma":
                    gamma = float(
                        ''.join(c for c in linesplit[1] if c not in '()').rstrip('.'))
    # create cell vectors
    print(f'cell vectors: alpha, beta, gamma = {alpha}, {beta}, {gamma}')
    try:
        cell_vector.append([A, 0, 0])
        cell_vector.append([B*numpy.cos((gamma*pi)/180),
                            B*numpy.sin((gamma*pi)/180), 0])
        cx = C*numpy.cos((beta*pi)/180)
        cy = C*(numpy.cos((alpha*pi)/180)-numpy.cos((beta*pi)/180) *
                numpy.cos((gamma*pi/180)))/numpy.sin((gamma*pi)/180)
        cz = sqrt(C*C - cx*cx - cy*cy)
        cell_vector.append([cx, cy, cz])
    except ValueError:  # Negative number in sqrt
        emsg = emsg.append('Error in creating unit cell from cif informtation')
        exit_status = 2
    for i, rows in enumerate(cell_vector):
        for j, elements in enumerate(rows):
            if abs(elements) <= 1e-8:
                cell_vector[i][j] = 0
    if exit_status != 0:
        return emsg
    elif return_extra_cif_info:
        return unit_cell, cell_vector, alpha, beta, gamma
    else:
        return unit_cell, cell_vector
##################################
# get center_of_sym CIF to mol3D
#
#  @param list_of_points list of points
#  @return csym center of sym


def center_of_sym(list_of_points):
    n = len(list_of_points)
#    print('lop = ' + str(list_of_points))
    csym = [float(sum(x)/n) for x in zip(*list_of_points)]
    return csym
# get sets min z coord of mol3D to zero
#
#  @param super_cell mol3D of cell


def zero_z_csm(super_cell):
    # puts center of sym
    # at z = 0
    csm = super_cell.centersym()
    vec = [0, 0, 0]
    vec[2] = -1*csm[2]
    super_cell.translate(vec)
##################################


def xgcd(b, n):
    # calculate x,y such that b*x + n*y = gcd(b,n)
    # by extended Euclidean algorithm
    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return b, x0, y0
#
##################################


def distance_zw(r1, r2):
    dx = r1[0] - r2[0]
    dy = r1[1] - r2[1]
    dz = 150*(r1[2] - r2[2])
    d = sqrt(dx**2+dy**2+dz**2)
    return d
##################################


def mdistance(r1, r2):
    dx = r1[0] - r2[0]
    dy = r1[1] - r2[1]
    dz = r1[2] - r2[2]
    d = sqrt(numpy.power(dx, 2) + numpy.power(dy, 2) + numpy.power(dz, 2))
    return d
###################################


def get_basis_coefficients(point, basis):
    # function to get basis set coefficients
    # for an arbitrary point in a given (complete)
    # basis set
    coefficients = numpy.linalg.solve(
        numpy.transpose(numpy.asarray(basis)), point)
    return coefficients
###################################


def evaluate_basis_coefficients(coefficients, basis):
    # get cartessian coords from basis set and
    # coefficients

    recons = [0, 0, 0]
    for j in [0, 1, 2]:
        recons = numpy.add(
            recons, [coefficients[j]*numpy.asarray(basis[j][i]) for i in [0, 1, 2]])
    return recons
###################################


def change_basis(mol, old_basis, new_basis):
    new_mol = mol3D()
    new_mol.copymol3D(mol)
    point_coefficients = [get_basis_coefficients(
        at.coords(), old_basis) for at in new_mol.getAtoms()]
    new_points = [get_basis_coefficients(
        point, new_basis) for point in point_coefficients]
    for i, at in enumerate(new_mol.getAtoms()):
        at.setcoords(new_points[i])
    return new_mol
###################################


def normalize_vector(v):
    length = distance(v, [0, 0, 0])
    if length:
        nv = [float(i)/length for i in v]
    else:
        nv = [0, 0, 0]
    return nv
##############################


def threshold_basis(basis, threshold):
    new_basis = [threshold_vector(i, threshold) for i in basis]
    return new_basis
##############################


def threshold_vector(v, threshold):
    nv = copy.copy(v)
    for i, vi in enumerate(v):
        if abs(vi) < threshold:
            nv[i] = 0
    return nv
##############################


def find_all_surface_atoms(super_cell, tol=1e-2, type_of_atom=False):
    # Get all atoms on the tope surface - NB, this will
    # not handle complex (2 or more) atom-type surfaces
    # if the atoms are 'layered', e.g. TiO2 - Ti under O2,
    # no Ti will be found. This can be overcome by using \
    # a looser tolerance, such that the interlayer differences
    # are smaller than tol, but not so large as to conflate
    # different layers!
    # INPUT:
    #   - super_cell: mol3D class that contains the super cell
    #   - tol: float, max distance from extent plane to look
    #   - type_of_atom: optional, string, gets atoms of the given type on the face plane
    #                   if left out, will not care about types of atoms
    # OUTPUT
    #   - avail_sites_list: list of int, indices of atoms on the surface
    #
    extents = find_extents(super_cell)
    target_height = extents[2]
    avail_sites_list = list()
    if type_of_atom:
        possible_atom_inds = super_cell.findAtomsbySymbol(type_of_atom)
    else:
        possible_atom_inds = list(range(0, super_cell.natoms))
    for indices in possible_atom_inds:
        z_dist = abs(super_cell.getAtom(indices).coords()[2] - target_height)
        if (z_dist <= tol):
            avail_sites_list.append(indices)

    return avail_sites_list

###################################


def distance_2d_torus(R1, R2, dim):
    # distance between points in Euclidean torus
    dx = abs(R1[0] - R2[0])
    dy = abs(R1[1] - R2[1])
    dz = abs((R1[2] - R2[2]))
    d1 = sqrt(numpy.power(dim[0] - dx, 2)
              + numpy.power(dim[1] - dy, 2)
              + numpy.power(dz, 2))
    d2 = sqrt(numpy.power(dim[0] - dx, 2)
              + numpy.power(dy, 2)
              + numpy.power(dz, 2))
    d3 = sqrt(numpy.power(dx, 2)
              + numpy.power(dim[1] - dy, 2)
              + numpy.power(dz, 2))
    d4 = sqrt(numpy.power(dx, 2)
              + numpy.power(dy, 2)
              + numpy.power(dz, 2))
    d = min(d1, d2, d3, d4)
    return d
###################################


def distance_2d_torus_next_only(R1, R2, dim):
    # distance between points in Euclidean torus
    dx = abs(R1[0] - R2[0])
    dy = abs(R1[1] - R2[1])
    dz = abs((R1[2] - R2[2]))
    d1 = sqrt(numpy.power(dim[0] - dx, 2)
              + numpy.power(dim[1] - dy, 2)
              + numpy.power(dz, 2))
    d2 = sqrt(numpy.power(dim[0] - dx, 2)
              + numpy.power(dy, 2)
              + numpy.power(dz, 2))
    d3 = sqrt(numpy.power(dx, 2)
              + numpy.power(dim[1] - dy, 2)
              + numpy.power(dz, 2))

    d = min(d1, d2, d3)
    return d
################################################################


def periodic_2d_distance(R1, R2, cell_vector):
    # distance between points in Euclidean torus
    # STILL UNDER CONSTRUCTION, WIP WIP WIP ***
    dx = abs(R1[0] - R2[0])
    dy = abs(R1[1] - R2[1])
    dz = abs((R1[2] - R2[2]))
    for v1shifts in [-1, 0, 1]:
        for v1shifts in [-1, 0, 1]:
            for yshifts in [-1, 0, 0]:
                pass
    d1 = sqrt(numpy.power(dim[0] - dx, 2)  # noqa: F821 (under construction)
              + numpy.power(dim[1] - dy, 2)  # noqa: F821 (under construction)
              + numpy.power(dz, 2))
    d2 = sqrt(numpy.power(dim[0] - dx, 2)  # noqa: F821 (under construction)
              + numpy.power(dy, 2)
              + numpy.power(dz, 2))
    d3 = sqrt(numpy.power(dx, 2)
              + numpy.power(dim[1] - dy, 2)  # noqa: F821 (under construction)
              + numpy.power(dz, 2))
    d = min(d1, d2, d3)
    return d
################################################################


def periodic_mindist(mol, surf, dim):
    ### calculates minimum distance between atoms in 2 molecules ###
    # INPUT
    #   - mol: mol3D class,  molecule
    #   - surf: mol3D class, the surface
    #   - dim: list of float, replication
    # OUTPUT
    #   - mind: minimum distance between atoms of the 2 mol objects
    mind = 1000
    for atom1 in mol.getAtoms():
        for atom0 in surf.getAtoms():
            if (distance_2d_torus(atom1.coords(), atom0.coords(), dim) < mind):
                mind = distance(atom1.coords(), atom0.coords())
    return mind
################################################################


def periodic_selfdist(mol, dim):
    ### calculates minimum distance between atoms in 2 molecules ##
    # INPUT
    #   - mol: mol3D class,  molecule
    #   - dim: list of floats, replication
    # OUTPUT
    #   - mind: minimum distance between atoms of the 2 mol and periodic
    #             images
    mind = 1000
    for ii, atom1 in enumerate(mol.getAtoms()):
        for jj, atom0 in enumerate(mol.getAtoms()):
            if (distance_2d_torus(atom1.coords(), atom0.coords(), dim) < mind) and (ii != jj):
                mind = distance(atom1.coords(), atom0.coords())
    return mind

##################################


def closest_torus_point(mol, dim):
    min_dist = 1000
    for atom1 in mol.getAtoms():
        R1 = atom1.coords()
        for atom2 in mol.getAtoms():
            R2 = atom2.coords()
            d = distance_2d_torus_next_only(R1, R2, dim)
            if (d < min_dist):
                min_dist = d
    return min_dist
#################################


def check_top_layer_correct(super_cell, atom_type):
    # remove the layer on
    # top of the cell if
    # wrong material is exposed
    trimmed_cell = mol3D()
    trimmed_cell.copymol3D(super_cell)
    globs = globalvars()
    elements = globs.elementsbynum()
    print(f'checking surface for {atom_type}\n')
    if atom_type not in elements:
        print("unknown surface type, unable to trim")
        return trimmed_cell
    else:
        stop_flag = False
        counter = 0  # 3 tries max
        while not stop_flag:
            atom_type_surf = find_all_surface_atoms(
                trimmed_cell, tol=1e-3, type_of_atom=atom_type)
            top_surf = find_all_surface_atoms(
                trimmed_cell, tol=1e-3, type_of_atom=False)
            if set(atom_type_surf) == set(top_surf):
                print('match')
                stop_flag = True
            else:
                counter += 1
                trimmed_cell = shave_surface_layer(trimmed_cell, 1e-3)
            if counter == 3:
                print('unable to find target atom in 3 cuts')
                stop_flag = True
    return trimmed_cell
###############################


def shave_surface_layer(super_cell, TOL=1e-1):
    # dlist = fractionate_points_by_plane(super_cell,n)
    # points_below_plane(point,n,refd)

    shaved_cell = mol3D()
    shaved_cell.copymol3D(super_cell)
    extents = find_extents(super_cell)
    zmax = extents[2]
    del_list = list()
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if abs(coords[2] - zmax) < TOL:
            del_list.append(i)
    shaved_cell.deleteatoms(del_list)
    return shaved_cell
###############################


def shave_under_layer(super_cell):
    shaved_cell = mol3D()
    shaved_cell.copymol3D(super_cell)
    TOL = 1e-1
    zmin = 1000
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if (coords[2] < zmin):
            zmin = coords[2]
    del_list = list()
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if abs(coords[2] - zmin) < TOL:
            del_list.append(i)
    shaved_cell.deleteatoms(del_list)
    return shaved_cell
###############################


def shave__type(super_cell, dim, mode):
    ## dim  = 0,1,2
    # x,y,z
    #   mode = 1 for max, -1 for min
    shaved_cell = mol3D()
    shaved_cell.copymol3D(super_cell)
    TOL = 1e-1

    dim_ref = 1000

    del_list = []
    if (mode == -1):
        for i, atoms in enumerate(super_cell.getAtoms()):
            coords = atoms.coords()
            if (coords[dim] < dim_ref):
                dim_ref = coords[dim]
        for i, atoms in enumerate(super_cell.getAtoms()):
            coords = atoms.coords()
            if abs(coords[dim] - dim_ref) < TOL:
                del_list.append(i)
    elif (mode == 1):
        extents = find_extents(super_cell)
        dim_max = extents[dim]
        for i, atoms in enumerate(super_cell.getAtoms()):
            coords = atoms.coords()
            if abs(coords[dim] - dim_max) < TOL:
                del_list.append(i)
    # return
    shaved_cell.deleteatoms(del_list)
    return shaved_cell
###############################


def zero_z(super_cell):
    zeroed_cell = mol3D()
    zeroed_cell.copymol3D(super_cell)
    zmin = 1000
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if (coords[2] < zmin):
            zmin = coords[2]
    zeroed_cell.translate([0, 0, -1*zmin])
    return zeroed_cell


def zero_x(super_cell):
    zeroed_cell = mol3D()
    zeroed_cell.copymol3D(super_cell)
    xmin = 1000
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if (coords[0] < xmin):
            xmin = coords[0]
    zeroed_cell.translate([-1*xmin, 0, 0])
    return zeroed_cell


def zero_y(super_cell):
    zeroed_cell = mol3D()
    zeroed_cell.copymol3D(super_cell)
    ymin = 1000
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if (coords[1] < ymin):
            ymin = coords[1]
    zeroed_cell.translate([0, -1*ymin, 0])
    return zeroed_cell

###############################


def point_in_box(point, box):
    outcome = False
    fx = (box[0][0] <= point[0])*(point[0] < box[0][1])
    fy = (box[1][0] <= point[1])*(point[1] < box[1][1])
    fz = (box[2][0] <= point[2])*(point[2] < box[2][1])
    if fz and fy and fx:
        outcome = True
    return outcome
##############################


def apply_plane_to_point(point, n):
    dplane = sum([n[i]*point[i] for i in [0, 1, 2]])
    return dplane
##############################


def fractionate_points_by_plane(super_cell, n, tol=1E-8):
    vals = list()
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        this_frac = apply_plane_to_point(coords, n)
        if len(vals) > 0:
            # compare to seen values
            these_dists = [abs(this_frac-j) for j in vals]
            if min(these_dists) < tol:
                pass
            else:
                vals.append(this_frac)
                print(f'new point at {this_frac}')
        else:
            vals.append(this_frac)
    return vals
##############################


def points_below_plane(point, n, refd):
    dplane = apply_plane_to_point(point, n)  # noqa: F841 (under construction)
    if abs(d-refd) < 1E-6:  # noqa: F821 (under construction)
        outcome = False
    elif d < dref:  # noqa: F821 (under construction)
        outcome = True
    else:
        outcome = False
    return outcome
#################################


def freeze_bottom_n_layers(super_cell, n):
    frozen_cell = mol3D()
    frozen_cell.copymol3D(super_cell)
    counter = 0
    while counter < n:
        frozen_cell_new = freeze_under_layer(frozen_cell)
        frozen_cell = mol3D()
        frozen_cell.copymol3D(frozen_cell_new)
        counter += 1
    return frozen_cell
###############################


def freeze_under_layer(super_cell):
    frozen_cell = mol3D()
    frozen_cell.copymol3D(super_cell)
    TOL = 1.5
    zmin = 1000
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if not atoms.frozen:
            if (coords[2] < zmin):
                zmin = coords[2]
    freeze_list = list()
    for i, atoms in enumerate(super_cell.getAtoms()):
        coords = atoms.coords()
        if not atoms.frozen:
            if abs(coords[2] - zmin) < TOL:
                freeze_list.append(i)
    frozen_cell.freezeatoms(freeze_list)
    return frozen_cell
##############################


def find_extents(super_cell):
    # INPUT
    #   - super_cell: mol3D class that contains the super cell
    # OUTPUT
    #   - extents: list of max coords of atoms on the surface
    xmax = 0
    zmax = 0
    ymax = 0
    for atoms in super_cell.getAtoms():
        coords = atoms.coords()
        x_ext = coords[0]  # + atoms.rad
        y_ext = coords[1]  # + atoms.rad
        z_ext = coords[2]  # + atoms.rad
        xmax = max(xmax, x_ext)
        ymax = max(ymax, y_ext)
        zmax = max(zmax, z_ext)
    extents = [xmax, ymax, zmax]
    return extents
#####################################


def find_extents_cv(super_cell_vector):
    # INPUT
    #   - super_cell_vector: matrix of the three vectors that define the super cell
    # OUTPUT
    #   - extents: list of max coords of the super cell
    xmax = 0
    zmax = 0
    ymax = 0
    for columns in super_cell_vector:
        xmax = max(xmax, abs(columns[0]))
        ymax = max(ymax, abs(columns[1]))
        zmax = max(zmax, abs(columns[2]))
    xmax = numpy.linalg.norm(super_cell_vector[0])
    ymax = numpy.linalg.norm(super_cell_vector[1])
    zmax = numpy.linalg.norm(super_cell_vector[2])

    extents = [xmax, ymax, zmax]
    return extents
