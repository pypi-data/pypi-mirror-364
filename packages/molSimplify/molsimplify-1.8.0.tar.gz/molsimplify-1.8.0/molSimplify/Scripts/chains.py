# @file chains.py
#  Builds chains of monomers with regular conformation.
#
#  Written by JP Janet for HJK Group
#
#  Dpt of Chemical Engineering, MIT

from math import sqrt

import numpy as np

from molSimplify.Classes.mol3D import mol3D
from molSimplify.Scripts.geometry import (rotate_around_axis,
                                          rotation_params,
                                          vecangle,
                                          vecdiff,
                                          distance)
from molSimplify.Scripts.structgen import (ffopt)
import numpy


def mdistance(r1, r2):
    dx = r1[0] - r2[0]
    dy = r1[1] - r2[1]
    dz = r1[2] - r2[2]
    d = sqrt(numpy.power(dx, 2) + numpy.power(dy, 2) + numpy.power(dz, 2))
    return d


def find_extents(mol):
    # INPUT
    #   - mol: mol3D class that contains the super cell
    # OUTPUT
    #   - extents: list of max coords of atoms on the surface
    xmax = 0
    zmax = 0
    ymax = 0
    for atoms in mol.getAtoms():
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


def interatomic_dist(mol, ind1, ind2):
    coord1 = mol.getAtom(ind1).coords()
    coord2 = mol.getAtom(ind2).coords()
    distance = mdistance(coord1, coord2)
    print(('iad between', mol.getAtom(ind1).symbol(), mol.getAtom(ind2).symbol()))

    vector = [coord1[i] - coord2[i] for i in [0, 1, 2]]
    return distance, vector


def find_term_heavy(mol, reference_point):
    min_dist = 1000
    min_ind = 0
    print(('reference_point', reference_point))
    for inds, atoms in enumerate(mol.getAtoms()):
        if not atoms.symbol() == "H":
            this_coord = atoms.coords()
            this_dist = distance(this_coord, reference_point)
            if this_dist < min_dist:
                min_dist = this_dist
                min_ind = inds
    return min_ind


def trim_H(mol, reference_point):
    trimmed_mol = mol3D()
    trimmed_mol.copymol3D(mol)
    min_ind = find_term_heavy(mol, reference_point)
    hydrogen_list = trimmed_mol.getHsbyIndex(min_ind)
    trimmed_mol.deleteatoms([hydrogen_list[0]])
    return trimmed_mol


def zero_dim(mol, dim):
    if dim == 0:
        return zero_x(mol)
    elif dim == 1:
        return zero_y(mol)
    elif dim == 2:
        return zero_z(mol)
    else:
        return 'Error'


def zero_z(mol):
    zeroed_mol = mol3D()
    zeroed_mol.copymol3D(mol)
    zmin = 1000
    for i, atoms in enumerate(mol.getAtoms()):
        coords = atoms.coords()
        if (coords[2] < zmin):
            zmin = coords[2]
    zeroed_mol.translate([0, 0, -1*zmin])
    return zeroed_mol


def zero_x(mol):
    zeroed_mol = mol3D()
    zeroed_mol.copymol3D(mol)
    xmin = 1000
    for i, atoms in enumerate(mol.getAtoms()):
        coords = atoms.coords()
        if (coords[0] < xmin):
            xmin = coords[0]
    zeroed_mol.translate([-1*xmin, 0, 0])
    return zeroed_mol


def zero_y(mol):
    zeroed_mol = mol3D()
    zeroed_mol.copymol3D(mol)
    ymin = 1000
    for i, atoms in enumerate(mol.getAtoms()):
        coords = atoms.coords()
        if (coords[1] < ymin):
            ymin = coords[1]
    zeroed_mol.translate([0, -1*ymin, 0])
    return zeroed_mol


def zero_1st(mol):
    zeroed_mol = mol3D()
    zeroed_mol.copymol3D(mol)
    coord_to_zero = zeroed_mol.getAtom(0).coords()
    zeroed_mol.translate([-1*i for i in coord_to_zero])
    return zeroed_mol


def remove_closest_h(mol, other_mol):
    new_mol = mol3D()
    new_mol.copymol3D(mol)
    min_distance = 1000
    current_ind = 0
    for Hatoms in mol.getHs():
        this_H = mol.getAtom(Hatoms)
        for atoms in other_mol.getAtoms():
            this_distance = mdistance(this_H.coords(), atoms.coords())
            if this_distance < min_distance:
                min_distance = this_distance
                current_ind = Hatoms
    print(f'the H ind to delete is {current_ind} at {min_distance}')
    new_mol.deleteatoms([current_ind])
    return new_mol


def grow_linear_step(chain, new_unit, dim, interv, conatom, freezehead):
    combined_mol = mol3D()
    combined_mol.copymol3D(chain)
    combined_mol.convert2OBMol()
    add_mol = mol3D()
    add_mol.copymol3D(new_unit)
    add_mol.convert2OBMol()
    add_mol = zero_dim(new_unit, dim)

    chain_inds = list(range(0, chain.natoms))
    print(('chain_inds', chain_inds))
    print(f'freezehead is {freezehead}')
    basic_lengths = find_extents(chain)
    print(f'extents are {basic_lengths}')
    basic_dist = basic_lengths[dim]
    tv = [0, 0, 0]
    tv[dim] = basic_dist

    print(('translating', tv))

    add_mol.translate(interv)

    add_mol.writexyz('precut.xyz')
    add_mol.writexyz('postcut.xyz')
    combined_mol = combined_mol.combine(
        add_mol, bond_to_add=[(conatom, combined_mol.natoms, 1)])

    # ffopt(ff,mol,connected,constopt,frozenats,frozenangles,mlbonds,nsteps,debug=False):
    combined_mol, en = ffopt('MMFF94', mol=combined_mol, connected=[], constopt=0,
                             frozenats=list(range(0, freezehead+1)), frozenangles=[],
                             mlbonds=[], nsteps=200, debug=False)
    combined_mol.convert2mol3D()
    combined_mol.writexyz('pre.xyz')

    combined_mol.writexyz('post.xyz')

    return combined_mol


def chain_builder_supervisor(args, rundir):
    emsg = list()

    if not (args.chain) and not (isinstance(args.chain_units, (int))):
        emsg.append('Invalid input: need monomer AND number of units')

    print(args.chain)
    print(args.chain_units)

    print('loading monomer')
    monomer = mol3D()
    monomer.OBMol = monomer.getOBMol(args.chain, convtype='smistring')
    monomer.convert2mol3D()
    monomer = zero_1st(monomer)

    conatom = len(args.chain)-1
    print(f'connection atom is {monomer.getAtom(conatom).symbol()}')

    old_pos = monomer.getAtom(conatom).coords()
    idist = 1.25*mdistance(old_pos, [0, 0, 0])
    print(f'currently at located at {old_pos}')
    target = [0, 0, -1*mdistance(old_pos, [0, 0, 0])]

    print(f'target located at {target}')
    vec1 = vecdiff([0, 0, 0], old_pos)
    print(f'vecdiff is {vec1}')
    vec2 = [0, 0, 1]

    thetaold = vecangle(vec1, vec2)

    print(f'thetaold is {thetaold}')

    myu = np.cross(vec1, vec2)

    theta, u = rotation_params(target, [0, 0, 0], old_pos)
    print(f'rot params are {[theta, u]} my way {thetaold} my norm {myu}')

    monomer = rotate_around_axis(monomer, [0, 0, 0], u, theta)
    # rotate_around_axis(mol,         Rp,u,theta):
    #  Loops over PointRotateAxis().
    #  @param mol mol3D of molecule to be rotated
    #  @param Rp Reference point along axis
    #  @param u Direction vector of axis
    #  @param theta Angle of rotation in DEGREES
    #  @return mol3D of rotated molecule

    new_coords = monomer.getAtom(conatom).coords()

    print(f'now located at {new_coords}')
    print(f'target located at {target}')
    print('\n\n\n')


    interv = [0, 0, idist]

    my_dim = mol3D()
    my_dim.copymol3D(monomer)

    my_dim = trim_H(my_dim, monomer.getAtom(len(args.chain)-1).coords())

    middle = mol3D()
    middle.copymol3D(monomer)
    print('connection atom is ' + monomer.getAtom(len(args.chain)-1).symbol())
    conatom = len(args.chain)-1
    middle = trim_H(middle, monomer.getAtom(len(args.chain)-1).coords())

    middle = trim_H(middle, [0, 0, 0])

    print('loading end')
    end = mol3D()
    print(args.chain_head)
    if args.chain_head:
        end.OBMol = end.getOBMol(args.chain_head, convtype='smistring')
    else:
        end.OBMol = end.getOBMol(args.chain, convtype='smistring')
    end.convert2mol3D()
    end.writexyz('endi.xyz')
    end = zero_1st(end)
    end.writexyz('end_zero_z.xyz')
    conatom_end = 0
    print('end connection atom is ' + end.getAtom(conatom_end).symbol())
    end_pos = end.getAtom(conatom_end).coords()
    print(f'end target position is {end_pos}')
    target_displacement = mdistance(end_pos, [0, 0, 0])
    end.printxyz()
    if target_displacement > 0.05:
        target_end = [0, 0, -1*mdistance(end_pos, [0, 0, 0])]
        theta, u = rotation_params(target_end, [0, 0, 0], end_pos)
        end = rotate_around_axis(end, [0, 0, 0], u, theta)
    end = trim_H(end, [0, 0, 0])
    end.printxyz()
    end.writexyz('end.xyz')

    repu = mol3D()
    repu.copymol3D(middle)

    interv0 = interv
    old_nat = my_dim.natoms

    for i in range(0, int(args.chain_units)-1):

        locked_atoms = my_dim.natoms - 1
        my_dim = grow_linear_step(
            my_dim, repu, 0, interv, conatom, freezehead=locked_atoms)
        interv = [interv[i] + interv0[i] for i in [0, 1, 2]]
        print(f'con is {conatom}')
        print(f'old nat is {old_nat}')
        conatom = conatom + old_nat
        old_nat = repu.natoms + 1
        if not i % 2:
            old_nat -= 1
    print('build start')
    locked_atoms = my_dim.natoms - 1
    my_dim = grow_linear_step(my_dim, end, 0, interv,
                              conatom-1, freezehead=locked_atoms)
    my_dim.writexyz('poly.xyz')
    my_dim, en = ffopt('MMFF94', my_dim, [], 0, [], mlbonds=[],
                       frozenangles=[], nsteps=200, debug=False)
    my_dim.writexyz('polyf.xyz')

    if emsg:
        print(emsg)

    return emsg
