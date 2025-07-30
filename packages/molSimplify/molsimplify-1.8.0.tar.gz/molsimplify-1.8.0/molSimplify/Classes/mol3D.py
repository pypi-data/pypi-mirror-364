# @file mol3D.py
#  Defines mol3D class and contains useful manipulation/retrieval routines.
#
#  Written by HJK Group
#
#  Dpt of Chemical Engineering, MIT

import os
import re
import sys
import tempfile
import time
import copy
import xml.etree.ElementTree as ET
import numpy as np
import networkx as nx
try:
    from openbabel import openbabel  # version 3 style import
except ImportError:
    import openbabel  # fallback to version 2
from typing import List, Optional, Tuple, Dict, Any
from scipy.spatial import ConvexHull
from molSimplify.utils.decorators import deprecated

from molSimplify.Classes.atom3D import atom3D
from molSimplify.Classes.globalvars import globalvars
from molSimplify.Scripts.geometry import (
    connectivity_match,
    distance,
    rotate_around_axis,
    rotation_params,
    vecangle,
    )
from molSimplify.Scripts.rmsd import (
    kabsch_rmsd,
    kabsch_rotate,
    rigorous_rmsd,
    )
from itertools import permutations
from collections import Counter

'''
The methods of mol3D:
ACM
ACM_axis
BCM
BCM_opt
IsOct
IsStructure
Oct_inspection
RCAngle
RCDistance
Structure_inspection
__class__
__delattr__
__dict__
__dir__
__doc__
__eq__
__format__
__ge__
__getattribute__
__gt__
__hash__
__init__
__init_subclass__
__le__
__lt__
__module__
__ne__
__new__
__reduce__
__reduce_ex__
__repr__
__setattr__
__sizeof__
__str__
__subclasshook__
__weakref__
addAtom
add_bond
alignmol
apply_ffopt
apply_ffopt_list_constraints
aromatic_charge
assign_graph_from_net
calcCharges
centermass
centersym
check_angle_linear
choose_atoms_to_move
cleanBonds
closest_H_2_metal
combine
continuous_shape_measure
convert2OBMol
convert2OBMol2
convert2mol3D
convexhull
coords
coordsvect
copymol3D
count_atoms
count_electrons
count_nonH_atoms
count_specific_atoms
createMolecularGraph
create_mol_with_inds
deleteHs
deleteatom
deleteatoms
dev_from_ideal_geometry
dict_check_processing
distance
draw_svg
findAtomsbySymbol
findMetal
findcloseMetal
findsubMol
flip_symmetry
freezeatom
freezeatoms
from_smiles
geo_dict_initialization
geo_maxatomdist
geo_rmsd
getAngle
getAtom
getAtomCoords
getAtomTypes
getAtoms
getAtomwithSyms
getAtomwithinds
getBondCutoff
getBondedAtoms
getBondedAtomsBOMatrix
getBondedAtomsBOMatrixAug
getBondedAtomsByCoordNo
getBondedAtomsByThreshold
getBondedAtomsH
getBondedAtomsOct
getBondedAtomsSmart
getBondedAtomsnotH
getClosestAtom
getClosestAtomlist
getClosestAtomnoHs
getFarAtom
getHs
getHsbyAtom
getHsbyIndex
getMLBondLengths
getNumAtoms
getOBMol
get_bo_dict_from_inds
get_coordinate_array
get_element_list
get_fcs
get_features
get_first_shell
get_geometry_type
get_geometry_type_distance
get_geometry_type_old
get_graph
get_graph_hash
get_linear_angle
get_mol_graph_det
get_molecular_mass
get_num_coord_metal
get_octetrule_charge
get_pair_distance
get_smiles
get_smilesOBmol_charge
get_submol_noHs
get_symmetry
get_symmetry_denticity
getfarAtomdir
getfragmentlists
graph_from_bodict
initialize
isPristine
is_edge_compound
is_linear_ligand
is_sandwich_compound
ligand_comp_org
make_formula
match_lig_list
maxatomdist
maxatomdist_nonH
maxdist
meanabsdev
mindist
mindistmol
mindistnonH
mindisttopoint
mol3D_to_networkx
mols_symbols
molsize
moments_of_inertia
num_rings
oct_comp
overlapcheck
populateBOMatrix
populateBOMatrixAug
principal_moments_of_inertia
print_geo_dict
printxyz
read_bo_from_mol
read_bond_order
read_charge
read_smiles
readfrommol
readfrommol2
readfromstring
readfromtxt
readfromxyz
reflect_coords
resetBondOBMol
returnxyz
rmsd
rmsd_nonH
roland_combine
sanitycheck
sanitycheckCSD
setLoc
symvect
translate
typevect
writegxyz
writemol
writemol2
writemxyz
writenumberedxyz
writesepxyz
writexyz
'''

class mol3D:
    """
    Holds information about a molecule, used to do manipulations.
    Reads information from structure file (XYZ, mol2) or is directly
    built from molsimplify. Please be cautious with periodic systems.

    Example instantiation of an octahedral iron-ammonia complex from an XYZ file:

    >>> complex_mol = mol3D()
    >>> complex_mol.readfromxyz('fe_nh3_6.xyz')  # doctest: +SKIP

    """

    def __init__(self, name='ABC', loc='', use_atom_specific_cutoffs=False):
        # List of atom3D objects
        self.atoms: List[atom3D] = []
        # Number of atoms
        self.natoms = 0
        # Mass of molecule
        self.mass = 0
        # Size of molecule
        self.size = 0
        # Charge of molecule
        self.charge = 0
        # Force field optimization settings
        self.ffopt = 'BA'
        # Name of molecule (analogous to three_lc in AA3D)
        self.name = name
        # Holder for openbabel molecule
        self.OBMol = False
        # Holder for bond order matrix
        self.bo_mat = np.array([])
        # Holder for bond order dictionary
        self.bo_dict = {}
        # List of connection atoms
        self.cat = []
        # Denticity
        self.denticity = 0
        # Identifier
        self.ident = ''
        # Holder for global variables
        self.globs = globalvars()
        # Holder for molecular graph
        # Same as bo_mat, but only ones and zeros.
        self.graph = np.array([])
        self.xyzfile = 'undef'
        self.needsconformer = False
        # Holder for molecular group
        self.grps = False
        # Holder for metals
        self.metals: Optional[List[int]] = None
        # Conformation (empty string if irrelevant)
        self.loc = loc
        # Temporary list for storing conformations
        self.temp_list = []
        # Convex hull
        self.hull = []

        # Holder for partial charge for each atom
        self.partialcharges: List[float] = []

        # ---geo_check------
        self.dict_oct_check_loose = self.globs.geo_check_dictionary()[
            "dict_oct_check_loose"]
        self.dict_oct_check_st = self.globs.geo_check_dictionary()[
            "dict_oct_check_st"]
        self.dict_oneempty_check_loose = self.globs.geo_check_dictionary()[
            "dict_oneempty_check_loose"]
        self.dict_oneempty_check_st = self.globs.geo_check_dictionary()[
            "dict_oneempty_check_st"]
        self.oct_angle_ref = self.globs.geo_check_dictionary()["oct_angle_ref"]
        self.oneempty_angle_ref = self.globs.geo_check_dictionary()[
            "oneempty_angle_ref"]
        self.geo_dict = dict()
        self.std_not_use = list()

        self.num_coord_metal = -1
        self.catoms = list()
        self.init_mol_trunc = False
        self.my_mol_trunc = False
        self.flag_oct = -1
        self.flag_list = list()
        self.dict_lig_distort = dict()
        self.dict_catoms_shape = dict()
        self.dict_orientation = dict()
        self.dict_angle_linear = dict()
        self.use_atom_specific_cutoffs = use_atom_specific_cutoffs

    def __repr__(self):
        return f"mol3D({self.make_formula(latex=False)})"

    def ACM(self, idx1, idx2, idx3, angle):
        """
        Performs angular movement on a mol3D object. A submolecule is
        rotated about idx2. Operates directly on object.

        Note: Function is sometimes unreliable in non-simple cases.

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom 1.
            idx3 : int
                Index of anchor atom 2.
            angle : float
                New bond angle in degrees.
        """

        atidxs_to_move = self.findsubMol(idx1, idx2)
        atidxs_anchor = self.findsubMol(idx2, idx1)
        submol_to_move = mol3D()
        submol_anchor = mol3D()
        for atidx in atidxs_to_move:
            atom = self.getAtom(atidx)
            submol_to_move.addAtom(atom)
        for atidx in atidxs_anchor:
            atom = self.getAtom(atidx)
            submol_anchor.addAtom(atom)
        mol = mol3D()
        mol.copymol3D(submol_anchor)
        r0 = self.getAtom(idx1).coords()
        r1 = self.getAtom(idx2).coords()
        r2 = self.getAtom(idx3).coords()
        theta, u = rotation_params(r2, r1, r0)
        if theta < 90:
            angle = 180 - angle
        submol_to_move = rotate_around_axis(
            submol_to_move, r1, u, theta - angle)
        for i, atidx in enumerate(atidxs_to_move):
            asym = self.atoms[atidx].sym
            xyz = submol_to_move.getAtomCoords(i)
            self.atoms[atidx].__init__(Sym=asym, xyz=xyz)

    def ACM_axis(self, idx1, idx2, axis, angle):
        """
        Performs angular movement about an axis on a mol3D object. A submolecule
        is rotated about idx2. Operates directly on object.

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom.
            axis : list
                Direction vector of axis. Length 3 (X, Y, Z).
            angle : float
                New bond angle in degrees.
        """

        atidxs_to_move = self.findsubMol(idx1, idx2)
        atidxs_anchor = self.findsubMol(idx2, idx1)
        submol_to_move = mol3D()
        submol_anchor = mol3D()
        for atidx in atidxs_to_move:
            atom = self.getAtom(atidx)
            submol_to_move.addAtom(atom)
        for atidx in atidxs_anchor:
            atom = self.getAtom(atidx)
            submol_anchor.addAtom(atom)
        mol = mol3D()
        mol.copymol3D(submol_anchor)
        r1 = self.getAtom(idx2).coords()
        submol_to_move = rotate_around_axis(submol_to_move, r1, axis, angle)
        for i, atidx in enumerate(atidxs_to_move):
            asym = self.atoms[atidx].sym
            xyz = submol_to_move.getAtomCoords(i)
            self.atoms[atidx].__init__(Sym=asym, xyz=xyz)

    def BCM(self, idx1, idx2, d):
        """
        Performs bond centric manipulation (same as Avogadro, stretching
        and squeezing bonds). A submolecule is translated along the bond axis
        connecting it to an anchor atom.

        Illustration: H3A-BH3 -> H3A----BH3 where B = idx1 and A = idx2

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom.
            d : float
                Bond distance in angstroms.

        >>> complex_mol = mol3D()
        >>> complex_mol.addAtom(atom3D('H', [0, 0, 0]))
        >>> complex_mol.addAtom(atom3D('H', [0, 0, 1]))
        >>> complex_mol.BCM(1, 0, 0.7) # Set distance between atoms 0 and 1 to be 1.5 angstroms. Move atom 1.
        >>> complex_mol.coordsvect()
        array([[0. , 0. , 0. ],
               [0. , 0. , 0.7]])
        """

        bondv = self.getAtom(idx1).distancev(self.getAtom(idx2))  # 1 - 2
        # compute current bond length
        u = 0.0
        for u0 in bondv:
            u += (u0 * u0)
        u = np.sqrt(u)
        dR = [i * (d / u - 1) for i in bondv]
        submolidxes = self.findsubMol(idx1, idx2)
        for submolidx in submolidxes:
            self.getAtom(submolidx).translate(dR)

    def BCM_opt(self, idx1, idx2, d, ff='uff'):
        """
        Performs bond centric manipulation (same as Avogadro, stretching
        and squeezing bonds). A submolecule is translated along the bond axis
        connecting it to an anchor atom. Performs force field optimization
        after, freezing the moved bond length.

        Illustration: H3A-BH3 -> H3A----BH3 where B = idx1 and A = idx2

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom.
            d : float
                Bond distance in angstroms.
            ff : str
                Name of force field to be used from openbabel.
        """

        self.convert2OBMol()
        OBMol = self.OBMol
        forcefield = openbabel.OBForceField.FindForceField(ff)
        constr = openbabel.OBFFConstraints()
        constr.AddDistanceConstraint(idx1 + 1, idx2 + 1, d)
        s = forcefield.Setup(OBMol, constr)
        if s is not True:
            print('forcefield setup failed.')
            exit()
        else:
            forcefield.SteepestDescent(500)
            forcefield.GetCoordinates(OBMol)
        self.OBMol = OBMol
        self.convert2mol3D()

    def IsOct(self, init_mol=None, dict_check=False,
              angle_ref=False, flag_catoms=False,
              catoms_arr=None, debug=False,
              flag_lbd=True, BondedOct=True,
              skip=False, flag_deleteH=True,
              silent=False, use_atom_specific_cutoffs=True):
        """
        Main geometry check method for octahedral structures.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            flag_catoms : bool, optional
                Whether or not to return the catoms arr. Default as False.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            debug : bool, optional
                Flag for extra printout. Default is False.
            flag_lbd : bool, optional
                Flag for using ligand breakdown on the optimized geometry. If False, assuming equivalent index to initial geo.
                Default is True.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.
            skip : list, optional
                Geometry checks to skip. Default is False.
            flag_deleteH : bool, optional,
                Flag to delete Hs in ligand comparison. Default is True.
            silent : bool, optional
                Flag for warning suppression. Default is False.
            use_atom_specific_cutoffs : bool, optional
                Determine bonding with atom specific cutoffs.

        Returns
        -------
            flag_oct : int
                Good (1) or bad (0) structure.
            flag_list : list
                Metrics that are preventing a good geometry.
            dict_oct_info : dict
                Dictionary of measurements of geometry.
        """

        self.use_atom_specific_cutoffs = True
        if not dict_check:
            dict_check = self.dict_oct_check_st
        if not angle_ref:
            angle_ref = self.oct_angle_ref
        if skip:
            print("Warning: you are skipping following geometry checks:")
            print(skip)
        else:
            skip = list()

        self.get_num_coord_metal(debug=debug)
        # Note: use this only when you want to specify the metal connecting atoms.
        # This will change the attributes of mol3D.
        if catoms_arr is not None:
            self.catoms = catoms_arr
            self.num_coord_metal = len(catoms_arr)
        if init_mol is not None:
            init_mol.get_num_coord_metal(debug=debug)
            catoms_init = init_mol.catoms
        else:
            catoms_init = [0, 0, 0, 0, 0, 0]
        self.geo_dict_initialization()
        if len(catoms_init) >= 6:
            if self.num_coord_metal >= 6:
                if True:
                    self.num_coord_metal = 6
                    if 'FCS' not in skip:
                        dict_catoms_shape, catoms_arr = self.oct_comp(angle_ref,
                                                                      catoms_arr,
                                                                      debug=debug,
                                                                      )
                if init_mol is not None:
                    init_mol.use_atom_specific_cutoffs = True
                    if any(self.getAtom(ii).symbol() != init_mol.getAtom(ii).symbol()
                           for ii in range(min(self.natoms, init_mol.natoms))):
                        print(
                            "The ordering of atoms in the initial and final geometry is different.")
                        init_mol = mol3D()
                        init_mol.copymol3D(self)
                    if 'lig_distort' not in skip:
                        self.ligand_comp_org(init_mol=init_mol,
                                             flag_lbd=flag_lbd,
                                             debug=debug,
                                             BondedOct=BondedOct,
                                             flag_deleteH=flag_deleteH,
                                             angle_ref=angle_ref)
                if 'lig_linear' not in skip:
                    self.check_angle_linear()
                if debug:
                    self.print_geo_dict()
            eqsym, maxdent, _, _, _, eq_catoms = self.get_symmetry_denticity(
                return_eq_catoms=True)
            if eqsym:
                metal_coord = self.getAtomCoords(self.findMetal()[0])
                eq_dists = [np.linalg.norm(np.array(self.getAtom(
                    ii).coords()) - np.array(metal_coord)) for ii in eq_catoms]
                eq_dists.sort()
                self.dict_catoms_shape['dist_del_eq'] = eq_dists[-1] - eq_dists[0]
                eq_dists_relative = [(np.linalg.norm(np.array(self.getAtom(ii).coords()) -
                                                     np.array(metal_coord)))
                                     / (self.globs.amass()[self.getAtom(ii).sym][2]
                                        + self.globs.amass()[self.getAtom(self.findMetal()[0]).sym][2])
                                     for ii in eq_catoms]
                self.dict_catoms_shape['dist_del_eq_relative'] = np.max(
                    eq_dists_relative) - np.min(eq_dists_relative)
            if maxdent > 1:
                choice = 'multi'
            else:
                choice = 'mono'

            used_geo_cutoffs = dict_check[choice]
            if not eqsym:
                used_geo_cutoffs['dist_del_eq'] = used_geo_cutoffs['dist_del_all']
            flag_oct, flag_list, dict_oct_info = self.dict_check_processing(used_geo_cutoffs,
                                                                            num_coord=6,
                                                                            debug=debug,
                                                                            silent=silent)
        else:
            flag_oct = 0
            flag_list = ["bad_init_geo"]
            dict_oct_info = {"num_coord_metal": "bad_init_geo"}
        if flag_catoms:
            return flag_oct, flag_list, dict_oct_info, catoms_arr
        else:
            return flag_oct, flag_list, dict_oct_info

    def IsStructure(self, init_mol=None, dict_check=False,
                    angle_ref=False, num_coord=5,
                    flag_catoms=False, catoms_arr=None, debug=False,
                    skip=False, flag_deleteH=True):
        """
        Main geometry check method for square pyramidal structures.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            num_coord : int, optional
                The metal coordination number.
            flag_catoms : bool, optional
                Whether or not to return the catoms arr. Default as False.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            debug : bool, optional
                Flag for extra printout. Default is False.
            skip : list, optional
                Geometry checks to skip. Default is False.
            flag_deleteH : bool, optional,
                Flag to delete Hs in ligand comparison. Default is True.

        Returns
        -------
            flag_oct : int
                Good (1) or bad (0) structure.
            flag_list : list
                Metrics that are preventing a good geometry.
            dict_oct_info : dict
                Dictionary of measurements of geometry.
        """

        self.use_atom_specific_cutoffs = True
        if not dict_check:
            dict_check = self.dict_oneempty_check_st
        if not angle_ref:
            angle_ref = self.oneempty_angle_ref
        if skip:
            print("Warning: you are skipping following geometry checks:")
            print(skip)
        else:
            skip = list()

        self.get_num_coord_metal(debug=debug)
        if catoms_arr is not None:
            self.catoms = catoms_arr
            self.num_coord_metal = len(catoms_arr)
        if init_mol is not None:
            init_mol.get_num_coord_metal(debug=debug)
            catoms_init = init_mol.catoms
        else:
            catoms_init = [0 for i in range(num_coord)]
        self.geo_dict_initialization()
        print(angle_ref)
        if len(catoms_init) >= num_coord:
            if self.num_coord_metal >= num_coord:
                if True:
                    self.num_coord_metal = num_coord
                    if 'FCS' not in skip:
                        dict_catoms_shape, catoms_arr = self.oct_comp(angle_ref, catoms_arr,
                                                                      debug=debug)
                if init_mol is not None:
                    init_mol.use_atom_specific_cutoffs = True
                    if any(self.getAtom(ii).symbol() != init_mol.getAtom(ii).symbol()
                           for ii in range(min(self.natoms, init_mol.natoms))):
                        print(
                            "The ordering of atoms in the initial and final geometry is different.")
                        init_mol = mol3D()
                        init_mol.copymol3D(self)
                    if 'lig_distort' not in skip:
                        self.ligand_comp_org(
                            init_mol, flag_deleteH=flag_deleteH, debug=debug, angle_ref=angle_ref)
                if 'lig_linear' not in skip:
                    self.check_angle_linear()
                if debug:
                    self.print_geo_dict()
            eqsym, maxdent, _, _, _, eq_catoms = self.get_symmetry_denticity(
                return_eq_catoms=True)
            if eqsym:
                metal_coord = self.getAtomCoords(self.findMetal()[0])
                eq_dists = [np.linalg.norm(np.array(self.getAtom(
                    ii).coords()) - np.array(metal_coord)) for ii in eq_catoms]
                eq_dists.sort()
                self.dict_catoms_shape['dist_del_eq'] = eq_dists[-1] - eq_dists[0]
                eq_dists_relative = [(np.linalg.norm(np.array(self.getAtom(ii).coords()) -
                                                     np.array(metal_coord)))
                                     / (self.globs.amass()[self.getAtom(ii).sym][2]
                                        + self.globs.amass()[self.getAtom(self.findMetal()[0]).sym][2])
                                     for ii in eq_catoms]
                self.dict_catoms_shape['dist_del_eq_relative'] = np.max(
                    eq_dists_relative) - np.min(eq_dists_relative)
            if maxdent > 1:
                choice = 'multi'
            else:
                choice = 'mono'
            used_geo_cutoffs = dict_check[choice]
            if not eqsym:
                used_geo_cutoffs['dist_del_eq'] = used_geo_cutoffs['dist_del_all']
            flag_oct, flag_list, dict_oct_info = self.dict_check_processing(used_geo_cutoffs,
                                                                            num_coord=num_coord,
                                                                            debug=debug)
        else:
            flag_oct = 0
            flag_list = ["bad_init_geo"]
            dict_oct_info = {"num_coord_metal": "bad_init_geo"}
        if flag_catoms:
            return flag_oct, flag_list, dict_oct_info, catoms_arr
        else:
            return flag_oct, flag_list, dict_oct_info

    def Oct_inspection(self, init_mol=None, catoms_arr=None, dict_check=False,
                       angle_ref=False, flag_lbd=False, dict_check_loose=False,
                       BondedOct=True, debug=False):
        """
        Used to track down the changing geo_check metrics in a DFT geometry optimization.
        Catoms_arr always specified.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            flag_lbd : bool, optional
                Flag for using ligand breakdown on the optimized geometry. If False, assuming equivalent index to initial geo.
                Default is True.
            dict_check_loose: dict, optional
                Dictionary of geo check metrics, if a dictionary other than the default one from globalvars is desired.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.
            debug : bool, optional
                Flag for extra printout. Default is False.

        Returns
        -------
            flag_oct : int
                Good (1) or bad (0) structure.
            flag_list : list
                Metrics that are preventing a good geometry.
            dict_oct_info : dict
                Dictionary of measurements of geometry.
            flag_oct_loose : int
                Good (1) or bad (0) structures with loose cutoffs.
            flag_list_loose : list
                Metrics that are preventing a good geometry with loose cutoffs.
        """

        self.use_atom_specific_cutoffs = True
        if not dict_check:
            dict_check = self.dict_oct_check_st
        if not angle_ref:
            angle_ref = self.oct_angle_ref
        if not dict_check_loose:
            dict_check_loose = self.dict_oct_check_loose

        if catoms_arr is None:
            init_mol.get_num_coord_metal(debug=debug)
            catoms_arr = init_mol.catoms
            if len(catoms_arr) > 6:
                _, catoms_arr = init_mol.oct_comp(debug=debug)
        if len(catoms_arr) != 6:
            print('Error, must have 6 connecting atoms for octahedral.')
            print('Please DO CHECK what happens!!!!')
            flag_oct = 0
            flag_list = ["num_coord_metal"]
            dict_oct_info = {'num_coord_metal': len(catoms_arr)}
            geo_metrics = ['rmsd_max', 'atom_dist_max', 'oct_angle_devi_max', 'max_del_sig_angle',
                           'dist_del_eq', 'dist_del_all', 'devi_linear_avrg', 'devi_linear_max']
            for metric in geo_metrics:
                dict_oct_info.update({metric: "NA"})
            flag_oct_loose = 0
            flag_list_loose = ["num_coord_metal"]
        else:
            self.num_coord_metal = 6
            self.geo_dict_initialization()
            if init_mol is not None:
                init_mol.use_atom_specific_cutoffs = True
                if any(self.getAtom(ii).symbol() != init_mol.getAtom(ii).symbol()
                       for ii in range(min(self.natoms, init_mol.natoms))):
                    raise ValueError(
                        "initial and current geometry does not match in atom ordering!")
                dict_lig_distort = self.ligand_comp_org(init_mol=init_mol,
                                                        flag_lbd=flag_lbd,
                                                        catoms_arr=catoms_arr,
                                                        debug=debug,
                                                        BondedOct=BondedOct,
                                                        angle_ref=angle_ref)
                if dict_lig_distort['rmsd_max'] == 'lig_mismatch':
                    print("Warning: Potential issues about lig_mismatch.")
                else:
                    _, catoms_arr = self.oct_comp(angle_ref, catoms_arr, debug=debug)

            # Unsure if still needed. RM 2022/07/19
            _, _ = self.check_angle_linear(catoms_arr=catoms_arr)
            if debug:
                self.print_geo_dict()
            eqsym, maxdent, _, _, _ = self.get_symmetry_denticity()
            if maxdent > 1:
                choice = 'multi'
            else:
                choice = 'mono'
            used_geo_cutoffs = dict_check[choice]
            if not eqsym:
                used_geo_cutoffs['dist_del_eq'] = used_geo_cutoffs['dist_del_all']
            flag_oct, flag_list, dict_oct_info = self.dict_check_processing(dict_check=used_geo_cutoffs,
                                                                            num_coord=6, debug=debug)
            flag_oct_loose, flag_list_loose, __ = self.dict_check_processing(dict_check=dict_check_loose[choice],
                                                                             num_coord=6, debug=debug)
        return flag_oct, flag_list, dict_oct_info, flag_oct_loose, flag_list_loose

    def RCAngle(self, idx1, idx2, idx3, anglei, anglef, angleint=1.0, writegeo=False, dir_name='rc_angle_geometries'):
        """
        Generates geometries along a given angle reaction coordinate.
        In the given molecule, idx1 is rotated about idx2 with respect
        to idx3. Operates directly on object.

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom 1.
            idx3 : int
                Index of anchor atom 2.
            anglei : float
                New initial bond angle in degrees.
            anglef : float
                New final bond angle in degrees.
            angleint : float; default is 1.0 degree
                The angle interval in which the angle is changed
            writegeo : if True, the generated geometries will be written
                to a directory; if False, they will not be written to a
                directory; default is False
            dir_name : string; default is 'rc_angle_geometries'
                The directory to which generated reaction coordinate
                geoemtries are written, if writegeo=True.

        >>> complex_mol = mol3D()
        >>> complex_mol.addAtom(atom3D('O', [0, 0, 0]))
        >>> complex_mol.addAtom(atom3D('H', [0, 0, 1]))
        >>> complex_mol.addAtom(atom3D('H', [0, 1, 0]))

        Generate reaction coordinate geometries using the given structure by changing the angle between atoms 2, 1,
        and 0 from 90 degrees to 160 degrees in intervals of 10 degrees
        >>> complex_mol.RCAngle(2, 1, 0, 90, 160, 10)
        [mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2)]

        Generate reaction coordinates with the given geometry by changing the angle between atoms 2, 1, and 0 from
        160 degrees to 90 degrees in intervals of 10 degrees, and the generated geometries will not be written to
        a directory.
        >>> complex_mol.RCAngle(2, 1, 0, 160, 90, -10)
        [mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2), mol3D(O1H2)]
        """

        if writegeo:
            os.mkdir(dir_name)
        temp_list = []
        for ang_val in np.arange(anglei, anglef+angleint, angleint):
            temp_angle = mol3D()
            temp_angle.copymol3D(self)
            temp_angle.ACM(idx1, idx2, idx3, ang_val)
            temp_list.append(temp_angle)
            if writegeo:
                temp_angle.writexyz(f'{dir_name}/rc_{ang_val:.4f}.xyz')
        return temp_list

    def RCDistance(self, idx1, idx2, disti, distf, distint=0.05, writegeo=False, dir_name='rc_distance_geometries'):
        """
        Generates geometries along a given distance reaction coordinate.
        In the given molecule, idx1 is moved with respect to idx2.
        Operates directly on object.

        Parameters
        ----------
            idx1 : int
                Index of bonded atom containing submolecule to be moved.
            idx2 : int
                Index of anchor atom 1.
            disti : float
                New initial bond distance in angstrom.
            distf : float
                New final bond distance in angstrom.
            distint : float; default is 0.05 angstrom
                The distance interval in which the distance is changed
            writegeo : if True, the generated geometries will be written
                to a directory; if False, they will not be written to a
                directory; default is False
            dir_name : string; default is 'rc_distance_geometries'
                The directory to which generated reaction coordinate
                geoemtries are written if writegeo=True.

        >>> complex_mol = mol3D()
        >>> complex_mol.addAtom(atom3D('H', [0, 0, 0]))
        >>> complex_mol.addAtom(atom3D('H', [0, 0, 1]))

        Generate reaction coordinate geometries using the given structure by changing the distance between atoms 1 and 0
        from 1.0 to 3.0 angstrom (atom 1 is moved) in intervals of 0.5 angstrom
        >>> complex_mol.RCDistance(1, 0, 1.0, 3.0, 0.5)
        [mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2)]

        Generate reaction coordinates
        geometries using the given structure by changing the distance between atoms 1 and 0
        from 3.0 to 1.0 angstrom (atom 1 is moved) in intervals of 0.2 angstrom, and
        the generated geometries will not be written to a directory.
        >>> complex_mol.RCDistance(1, 0, 3.0, 1.0, -0.25)
        [mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2), mol3D(H2)]
        """

        if writegeo:
            os.mkdir(dir_name)
        temp_list = []
        for dist_val in np.arange(disti, distf+distint, distint):
            temp_dist = mol3D()
            temp_dist.copymol3D(self)
            temp_dist.BCM(idx1, idx2, dist_val)
            temp_list.append(temp_dist)
            if writegeo:
                temp_dist.writexyz(f'{dir_name}/rc_{dist_val:.4f}.xyz')
        return temp_list

    def Structure_inspection(self, init_mol=None, catoms_arr=None, num_coord=5, dict_check=False,
                             angle_ref=False, flag_lbd=False, dict_check_loose=False, BondedOct=True, debug=False):
        """
        Used to track down the changing geo_check metrics in a DFT geometry optimization. Specifically
        for a square pyramidal structure. Catoms_arr always specified.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            num_coord : int, optional
                The metal coordination number.
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            flag_lbd : bool, optional
                Flag for using ligand breakdown on the optimized geometry. If False, assuming equivalent index to initial geo.
                Default is True.
            dict_check_loose: dict, optional
                Dictionary of geo check metrics, if a dictionary other than the default one from globalvars is desired.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.
            debug : bool, optional
                Flag for extra printout. Default is False.

        Returns
        -------
            flag_oct : int
                Good (1) or bad (0) structure.
            flag_list : list
                Metrics that are preventing a good geometry.
            dict_oct_info : dict
                Dictionary of measurements of geometry.
            flag_oct_loose : int
                Good (1) or bad (0) structures with loose cutoffs.
            flag_list_loose : list
                Metrics that are preventing a good geometry with loose cutoffs.
        """

        if not dict_check:
            dict_check = self.dict_oneempty_check_st
        if not angle_ref:
            angle_ref = self.oneempty_angle_ref
        if not dict_check_loose:
            dict_check_loose = self.dict_oneempty_check_loose

        if catoms_arr is None:
            init_mol.get_num_coord_metal(debug=debug)
            catoms_arr = init_mol.catoms
            if len(catoms_arr) > num_coord:
                _, catoms_arr = init_mol.oct_comp(
                    angle_ref=angle_ref, debug=debug)
        if len(catoms_arr) != num_coord:
            print(f'Error, must have {num_coord} connecting atoms for octahedral.')
            print('Please DO CHECK what happens!!!!')
            flag_oct = 0
            flag_list = ["num_coord_metal"]
            dict_oct_info = {'num_coord_metal': len(catoms_arr)}
            geo_metrics = ['rmsd_max', 'atom_dist_max', 'oct_angle_devi_max', 'max_del_sig_angle',
                           'dist_del_eq', 'dist_del_all', 'devi_linear_avrg', 'devi_linear_max']
            for metric in geo_metrics:
                dict_oct_info.update({metric: "NA"})
            flag_oct_loose = 0
            flag_list_loose = ["num_coord_metal"]
        else:
            self.num_coord_metal = num_coord
            self.geo_dict_initialization()
            if init_mol is not None:
                init_mol.use_atom_specific_cutoffs = True
                if any(self.getAtom(ii).symbol() != init_mol.getAtom(ii).symbol()
                       for ii in range(min(self.natoms, init_mol.natoms))):
                    raise ValueError(
                        "initial and current geometry does not match in atom ordering!")
                dict_lig_distort = self.ligand_comp_org(init_mol=init_mol,
                                                        flag_lbd=flag_lbd,
                                                        catoms_arr=catoms_arr,
                                                        debug=debug,
                                                        BondedOct=BondedOct,
                                                        angle_ref=angle_ref)
                if dict_lig_distort['rmsd_max'] == 'lig_mismatch':
                    self.num_coord_metal = -1
                    print('!!!!!Should always match. WRONG!!!!!')
                else:
                    _, catoms_arr = self.oct_comp(angle_ref, catoms_arr, debug=debug)
            # Unsure if still needed. RM 2022/07/19
            _, _ = self.check_angle_linear(catoms_arr=catoms_arr)
            if debug:
                self.print_geo_dict()
            eqsym, maxdent, _, _, _ = self.get_symmetry_denticity()
            if maxdent > 1:
                choice = 'multi'
            else:
                choice = 'mono'
            used_geo_cutoffs = dict_check[choice]
            if not eqsym:
                used_geo_cutoffs['dist_del_eq'] = used_geo_cutoffs['dist_del_all']
            flag_oct, flag_list, dict_oct_info = self.dict_check_processing(dict_check=used_geo_cutoffs,
                                                                            num_coord=num_coord, debug=debug)
            flag_oct_loose, flag_list_loose, _ = self.dict_check_processing(dict_check=dict_check_loose[choice],
                                                                            num_coord=num_coord, debug=debug)
        return flag_oct, flag_list, dict_oct_info, flag_oct_loose, flag_list_loose

    def addAtom(self, atom: atom3D, index: Optional[int] = None, auto_populate_bo_dict: bool = True):
        """
        Adds an atom to the atoms attribute, which contains a list of
        atom3D class instances.

        Parameters
        ----------
            atom : atom3D
                atom3D class instance of added atom.
            index : int, optional
                Index of added atom. Default is None.
            auto_populate_bo_dict : bool, optional
                Populate bond order dictionary with newly added atom. Default is True.

        >>> complex_mol = mol3D()
        >>> C_atom = atom3D('C', [1, 1, 1])
        >>> complex_mol.addAtom(C_atom) # Add carbon atom at cartesian position 1, 1, 1 to mol3D object.
        """

        if index is None:
            index = len(self.atoms)
        # self.atoms.append(atom)
        self.atoms.insert(index, atom)
        # If partial charge list exists, add partial charge:
        if len(self.partialcharges) == self.natoms:
            partialcharge = atom.partialcharge
            if partialcharge is None:
                partialcharge = 0.0
            self.partialcharges.insert(index, partialcharge)
        if atom.frozen:
            self.atoms[index].frozen = True

        # If bo_dict exists, auto-populate the bo_dict with "1"
        # for all newly bonded atoms. (Atoms indices in pair must be sorted,
        # i.e., a bond order pair (1,5) is valid  but (5,1) is invalid.
        if auto_populate_bo_dict and self.bo_dict:
            new_bo_dict = {}
            # Adjust indices in bo_dict to reflect insertion
            for pair, order in list(self.bo_dict.items()):
                idx1, idx2 = pair
                if idx1 >= index:
                    idx1 += 1
                if idx2 >= index:
                    idx2 += 1
                new_bo_dict[(idx1, idx2)] = order
            self.bo_dict = new_bo_dict

            # Adjust indices in graph to reflect insertion
            graph_size = self.graph.shape[0]
            self.graph = np.insert(
                self.graph, index, np.zeros(graph_size), axis=0)
            self.graph = np.insert(
                self.graph, index, np.zeros(graph_size+1), axis=1)
            self.bo_mat = np.insert(
                self.bo_mat, index, np.zeros(graph_size), axis=0)
            self.bo_mat = np.insert(
                self.bo_mat, index, np.zeros(graph_size+1), axis=1)

            # Grab connecting atom indices and populate bo_dict and graph
            catom_idxs = self.getBondedAtoms(index)
            for catom_idx in catom_idxs:
                sorted_indices = sorted([catom_idx, index])
                self.bo_dict[tuple(sorted_indices)] = '1'
                self.graph[catom_idx, index] = 1
                self.graph[index, catom_idx] = 1
                self.bo_mat[catom_idx, index] = 1
                self.bo_mat[index, catom_idx] = 1
        else:
            self.graph = np.array([])
            self.bo_mat = np.array([])

        self.natoms += 1
        self.mass += atom.mass
        self.size = self.molsize()
        self.metals = None

    def add_bond(self, idx1: int, idx2: int, bond_type: int) -> dict:
        """
        Add a bond of order bond_type between the atom at idx1 and the atom at idx2.
        Adjusts bo_dict, bo_mat, and graph only, not OBMol.

        Parameters
        ----------
            idx1: int
                Index of first atom.
            idx2: int
                Index of second atom.
            bond_type: int
                The order of the new bond.

        Returns
        -------
            self.bo_dict: dict
                The modified bond order dictionary.
        """

        if not (isinstance(idx1, int) and isinstance(idx2, int) and isinstance(bond_type, int)):
            raise TypeError('Incorrect input!')  # Error handling. The user gave input of the wrong type.

        # Keys in bo_dict must be sorted tuples, where the first index is smaller than the second.
        if idx1 < idx2:
            self.bo_dict[(idx1, idx2)] = bond_type
        elif idx2 < idx1:
            self.bo_dict[(idx2, idx1)] = bond_type
        else:
            raise IndexError('Indices should be different!')  # Cannot have an atom bond to itself.

        # Adjusting the graph as well.
        if self.graph.size == 0:
            self.graph = np.zeros((self.natoms, self.natoms))
        self.graph[idx1][idx2] = 1
        self.graph[idx2][idx1] = 1
        if self.bo_mat.size == 0:
            self.bo_mat = np.zeros((self.natoms, self.natoms))
        self.bo_mat[idx1][idx2] = bond_type
        self.bo_mat[idx2][idx1] = bond_type

        return self.bo_dict

    def alignmol(self, atom1, atom2):
        """
        Aligns two molecules such that the coordinates of two atoms overlap.
        Second molecule is translated relative to the first. No rotations are
        performed. Use other functions for rotations. Moves the mol3D class.

        Parameters
        ----------
            atom1 : atom3D
                atom3D of reference atom in first molecule.
            atom2 : atom3D
                atom3D of reference atom in second molecule.
        """

        dv = atom2.distancev(atom1)
        self.translate(dv)

    def apply_ffopt(self, constraints=False, ff='uff'):
        """
        Apply forcefield optimization to a given mol3D class.

        Parameters
        ----------
            constraints : int, optional
                Range of atom indices to employ cartesian constraints before ffopt.
            ff : str, optional
                Force field to be used in openbabel. Default is UFF.

        Returns
        -------
            energy : float
                Energy of the ffopt in kJ/mol.
        """

        forcefield = openbabel.OBForceField.FindForceField(ff)
        constr = openbabel.OBFFConstraints()
        if constraints:
            for catom in range(constraints):
                # Openbabel uses a 1 index instead of a 0 index.
                constr.AddAtomConstraint(catom+1)
        self.convert2OBMol()
        forcefield.Setup(self.OBMol, constr)
        if self.OBMol.NumHvyAtoms() > 10:
            forcefield.ConjugateGradients(200)
        else:
            forcefield.ConjugateGradients(50)
        forcefield.GetCoordinates(self.OBMol)
        en = forcefield.Energy()
        self.convert2mol3D()
        return en

    def apply_ffopt_list_constraints(self, list_constraints=False, ff='uff'):
        """
        Apply forcefield optimization to a given mol3D class.
        Differs from apply_ffopt in that one can specify constrained atoms as a list.

        Parameters
        ----------
            list_constraints : list of int, optional
                List of atom indices to employ cartesian constraints before ffopt.
            ff : str, optional
                Force field to be used in openbabel. Default is UFF.

        Returns
        -------
            energy : float
                Energy of the ffopt in kJ/mol.
        """

        forcefield = openbabel.OBForceField.FindForceField(ff)
        constr = openbabel.OBFFConstraints()
        if list_constraints:
            for catom in list_constraints:
                # Openbabel uses a 1 index instead of a 0 index.
                constr.AddAtomConstraint(catom+1)
        self.convert2OBMol()
        forcefield.Setup(self.OBMol, constr)
        if self.OBMol.NumHvyAtoms() > 10:
            forcefield.ConjugateGradients(200)
        else:
            forcefield.ConjugateGradients(50)
        forcefield.GetCoordinates(self.OBMol)
        en = forcefield.Energy()
        self.convert2mol3D()
        return en

    def aromatic_charge(self, bo_graph):
        '''
        Get the charge of aromatic rings based on 4*n+2 rule.

        Parameters
        ----------
            bo_graph: numpy.array
                Bond order matrix.

        Returns
        -------
            aromatic_charge: int
                The charge of the aromatic rings.
        '''

        aromatic_atoms = np.count_nonzero(bo_graph == 1.5)/2
        if aromatic_atoms > bo_graph.shape[0] - 1:
            aromatic_n = np.rint((aromatic_atoms-2)*1./4)
            aromatic_e = 4 * aromatic_n + 2
            aromatic_charge = int(aromatic_atoms - aromatic_e)
        else:
            aromatic_charge = 0

        return aromatic_charge

    def assign_graph_from_net(self, path_to_net, return_graph=False):
        """
        Uses a .net file to assign a graph (and return if needed).

        Parameters
        ----------
            path_to_net : str
                path to .net file containing the molecular graph.
            return_graph : bool
                Return the graph in addition to assigning it to self. Default is False.

        Returns
        -------
            graph: np.array
                A numpy array containing the unattributed molecular graph.
        """

        with open(path_to_net, 'r') as f:
            strgraph = f.readlines()
            graph = []
            for i, line in enumerate(strgraph):
                if i == 0:
                    continue
                else:
                    templine = np.array([int(val) for val in line.strip('\n').split(',')])
                    graph.append(templine)
            graph = np.array(graph)
            self.graph = graph
        if return_graph:
            return graph

    def calcCharges(self, charge=0, method='QEq'):
        """
        Compute the partial charges of a molecule using openbabel.

        Parameters
        ----------
            charge : int
                Net charge assigned to a molecule
            method : str
                Method to calculate partial charge. Default is 'QEq'.
        """

        self.convert2OBMol()
        self.OBMol.SetTotalCharge(charge)
        charge = openbabel.OBChargeModel.FindType(method)
        charge.ComputeCharges(self.OBMol)
        self.partialcharges = charge.GetPartialCharges()

    def centermass(self):
        """
        Computes coordinates of center of mass of molecule.

        Returns
        -------
            center_of_mass : list
                Coordinates of center of mass. List of length 3: (X, Y, Z).
        """

        center_of_mass = np.array([0, 0, 0], dtype='float64')
        mmass = 0
        # loop over atoms in molecule
        if self.natoms > 0:
            for atom in self.atoms:
                # calculate center of mass (relative weight according to atomic mass)
                xyz = atom.coords()
                center_of_mass += np.array(xyz) * atom.mass
                mmass += atom.mass
            # normalize
            center_of_mass = np.divide(center_of_mass, mmass)
            center_of_mass = list(center_of_mass)
        else:
            center_of_mass = False
            print(
                'ERROR: Center of mass calculation failed. Structure will be inaccurate.\n')
        return center_of_mass

    def centersym(self):
        """
        Computes coordinates of center of symmetry of molecule.
        Identical to centermass, but not weighted by atomic masses.

        Returns
        -------
            center_of_symmetry : list
                Coordinates of center of symmetry. List of length 3: (X, Y, Z).
        """

        # initialize center of mass and mol mass
        center_of_symmetry = np.array([0.0, 0.0, 0.0], dtype='float64')
        # loop over atoms in molecule
        for atom in self.atoms:
            # calculate center of symmetry
            xyz = atom.coords()
            center_of_symmetry += np.array(xyz)
        # normalize
        center_of_symmetry = np.divide(center_of_symmetry, self.natoms)
        center_of_symmetry = list(center_of_symmetry)
        return center_of_symmetry

    def check_angle_linear(self, catoms_arr=None):
        """
        Get the ligand orientation for linear ligands.

        Parameters
        ----------
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.

        Returns
        -------
            dict_orientation : dict
                Dictionary containing average deviation from linearity (devi_linear_avrg) and max deviation (devi_linear_max).
        """

        dict_angle_linear = {}
        if catoms_arr is not None:
            pass
        else:
            catoms_arr = self.catoms
        for ind in catoms_arr:
            flag, ang = self.get_linear_angle(ind)
            dict_angle_linear[str(ind)] = [flag, float(ang)]
        dict_orientation = {}
        devi_linear_avrg, devi_linear_max = 0, 0
        count = 0
        for key in dict_angle_linear:
            [flag, ang] = dict_angle_linear[key]
            if flag:
                count += 1
                devi_linear_avrg += 180 - ang
                if (180 - ang) > devi_linear_max:
                    devi_linear_max = 180 - ang
        if count:
            devi_linear_avrg /= count
        else:
            devi_linear_avrg = 0
        dict_orientation['devi_linear_avrg'] = float(devi_linear_avrg)
        dict_orientation['devi_linear_max'] = float(devi_linear_max)
        self.dict_angle_linear = dict_angle_linear
        self.dict_orientation = dict_orientation
        return dict_angle_linear, dict_orientation

    def choose_atoms_to_move(self, ligands, swap_indices, catoms):
        """
        Helper function for flip_symmetry to determine atoms to reflect

        Parameters
        ----------
            ligands: list
                Indices of atoms in each ligand
            swap_indices: list
                Indices indicating which ligand of each type to be moved
            catoms: list
                Indices of coordinating atoms in each ligand

        Returns
        -------
            atoms_to_move: list
                List of atom indices to be moved
        """

        from molSimplify.Classes.mol2D import Mol2D
        # determine denticity of each ligand type
        dents = [len(catoms[0])/len(ligands[0]), len(catoms[1])/len(ligands[1])]
        atoms_to_move = []
        for idx, atoms in enumerate(ligands):
            # for monodentate ligands
            if dents[idx] == 1:
                atoms_to_move.extend(atoms[swap_indices[idx]])
            # for multidentate ligands
            elif dents[idx] > 1:
                # delete metal, update ligand atom and catom indices
                metal_idx = self.findMetal()[0]
                ligands_mol = mol3D()
                ligands_mol.copymol3D(self)
                ligands_mol.deleteatom(atomIdx=metal_idx)
                atoms[0] = [atom_idx-1 for atom_idx in atoms[0] if metal_idx < atom_idx]
                catoms[idx] = np.array([catom_idx - 1 for catom_idx in catoms[idx] if metal_idx < catom_idx])
                other_catoms = np.delete(catoms[idx], swap_indices[idx])
                # get simple paths
                simple_paths = []
                for other_catom in other_catoms:
                    simple_paths.extend(Mol2D.from_mol3d(mol3d=ligands_mol).find_simple_paths(source=catoms[idx][swap_indices[idx]],
                                                                                              sink=other_catom,
                                                                                              cutoff=None,
                                                                                              constraints=None))
                # remove paths which cross multiple coordinating atoms
                simple_paths = [path for path in simple_paths if
                                sum([path.count(other_catom) for other_catom in other_catoms]) == 1]
                # check for and include side chains
                ligand_atoms = [idx for idx in range(ligands_mol.natoms)]
                ligand_atoms = list(np.delete(ligand_atoms, np.where(np.isin(ligand_atoms, other_catoms))))
                side_chains = []
                for path in simple_paths:
                    for side_chain_atom in ligand_atoms:
                        for node in path:
                            # add side chains as atoms for which a path exists to moving catoms, excluding fixed catoms
                            side_chains.extend(Mol2D.from_mol3d(mol3d=ligands_mol).find_simple_paths(source=side_chain_atom,
                                                                                                          sink=node,
                                                                                                          cutoff=None,
                                                                                                          constraints=list(other_catoms)))
                # convert back to indices including metal
                atoms[0] = [atom_idx+1 for atom_idx in atoms[0] if metal_idx <= atom_idx]
                catoms[idx] = np.array([catom_idx+1 for catom_idx in catoms[idx] if metal_idx <= catom_idx])
                simple_paths = [[node+1 for node in path if metal_idx <= node] for path in simple_paths]
                side_chains = [[node+1 for node in path if metal_idx <= node] for path in side_chains]
                # ignore final node in each path since these are coordinating atoms which should remain fixed
                atoms_to_move.extend(node for path in simple_paths for node in path[0:-1])
                # add side chain atoms
                atoms_to_move.extend(node for side_chain in side_chains for node in side_chain)
        return list(set(atoms_to_move))

    def cleanBonds(self):
        """
        Removes all stored openbabel bond order information.
        """

        obiter = openbabel.OBMolBondIter(self.OBMol)
        bonds_to_del = []
        for bond in obiter:
            bonds_to_del.append(bond)
        for i in bonds_to_del:
            self.OBMol.DeleteBond(i)

    def closest_H_2_metal(self, delta=0):
        """
        Get closest hydrogen atom to metal.

        Parameters
        ----------
            delta : float
                Distance tolerance in angstrom.

        Returns
        -------
            flag : bool
                Flag for if a hydrogen exists in the distance tolerance.
            min_dist_H : float
                Minimum distance for a hydrogen.
            min_dist_nonH : float
                Minimum distance for a heavy atom.
        """

        min_dist_H = 3.0
        min_dist_nonH = 3.0
        for i, atom in enumerate(self.atoms):
            if atom.ismetal():
                metal_atom = atom
                break
        else:
            raise ValueError('No metal found.')
        metal_coord = metal_atom.coords()
        for atom1 in self.atoms:
            if atom1.sym == 'H':
                if distance(atom1.coords(), metal_coord) < min_dist_H:
                    min_dist_H = distance(atom1.coords(), metal_coord)
            elif not atom1.ismetal():
                if distance(atom1.coords(), metal_coord) < min_dist_nonH:
                    min_dist_nonH = distance(atom1.coords(), metal_coord)
        if min_dist_H <= (min_dist_nonH - delta):
            flag = True
        else:
            flag = False
        return (flag, min_dist_H, min_dist_nonH)

    def combine(self, mol, bond_to_add=[], dirty=False):
        """
        Combines two molecules. Each atom in the second molecule
        is appended to the first while preserving orders. Assumes
        operation with a given mol3D instance, when handed a second mol3D instance.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance containing molecule to be added.
            bond_to_add : list, optional
                List of tuples (ind1,ind2,order) bonds to add. Default is empty.
            dirty : bool, optional
                Add atoms without worrying about bond orders. Default is False.

        Returns
        -------
            cmol : mol3D
                New mol3D class containing the two molecules combined.
        """

        cmol = self

        if not dirty:
            # BondSafe
            cmol.convert2OBMol(force_clean=False, ignoreX=True)
            mol.convert2OBMol(force_clean=False, ignoreX=True)
            n_one = cmol.natoms
            n_two = mol.natoms
            n_tot = n_one + n_two
            # allocate
            jointBOMat = np.zeros([n_tot, n_tot])
            # get individual mats
            con_mat_one = cmol.populateBOMatrix()
            con_mat_two = mol.populateBOMatrix()
            # combine mats
            for i in range(0, n_one):
                for j in range(0, n_one):
                    jointBOMat[i][j] = con_mat_one[i][j]
            for i in range(0, n_two):
                for j in range(0, n_two):
                    jointBOMat[i + n_one][j + n_one] = con_mat_two[i][j]
            # optional add additional bond(s)
            if bond_to_add:
                for bond_tuples in bond_to_add:
                    jointBOMat[bond_tuples[0], bond_tuples[1]] = bond_tuples[2]
                    jointBOMat[bond_tuples[1], bond_tuples[0]] = bond_tuples[2]

        # add mol3Ds
        for atom in mol.atoms:
            cmol.addAtom(atom)
        if not dirty:
            cmol.convert2OBMol(ignoreX=True)
            # clean all bonds
            cmol.cleanBonds()
            # restore bond info
            for i in range(0, n_tot):
                for j in range(0, n_tot):
                    if jointBOMat[i][j] > 0:
                        cmol.OBMol.AddBond(i + 1, j + 1, int(jointBOMat[i][j]))
        # reset graph
        cmol.graph = np.array([])
        cmol.bo_mat = np.array([])
        cmol.bo_dict = {}
        self.metals = None
        return cmol

    def continuous_shape_measure(self, ideal_polyhedron):
        """
        Return the continuous shape measure for the FCS, defined as:
        min(sum_i^N (q_i - p_i)^2 / sum_i^N(q_i - q_0)^2)
        Where q_i, p_i are vertices of the polyhedron and reference,
        and q_0 is the center of geometry of the real structure.
        The minimization is over possible pairwise combinations of vertices,
        and a rotation of the reference polyhedron (which is done with Kabsch).
        Only works for single-metal center TMCs since the translation is handled
        by centering on the metal.
        Scaling is handled by making the average bond lengths the same for the two structures.
        0 means perfect matching, maximum is 100.

        Parameters
        ----------
            ideal_polyhedron: np.array of 3-tuples of coordinates
                Reference list of points for an ideal geometry

        Returns
        -------
            min_cshm: float
                Continuous Shape Measure between the geometry and ideal_polyhedron
        """

        metal_idx = self.findMetal()
        if len(metal_idx) == 0:
            raise ValueError('No metal centers exist in this complex.')
        elif len(metal_idx) != 1:
            raise ValueError('Multimetal complexes are not yet handled.')
        temp_mol = self.get_first_shell()[0]
        fcs_indices = temp_mol.get_fcs(max6=False)
        # Remove metal index from first coordination shell.
        fcs_indices.remove(temp_mol.findMetal()[0])

        if len(fcs_indices) != len(ideal_polyhedron):
            raise ValueError('The coordination number differs between the two provided structures.')

        # Have to redo getting metal_idx with the new mol after running get_first_shell.
        # Want to work with temp_mol since it has the edge and sandwich logic implemented to replace those with centroids.
        metal_atom = temp_mol.getAtoms()[temp_mol.findMetal()[0]]
        fcs_atoms = [temp_mol.getAtoms()[i] for i in fcs_indices]
        # construct a np array of the non-metal atoms in the FCS
        distances = []
        positions = np.zeros([len(fcs_indices), 3])
        for idx, atom in enumerate(fcs_atoms):
            distance = atom.distance(metal_atom)
            distances.append(distance)
            # Shift so the metal is at (0, 0, 0)
            positions[idx, :] = np.array(atom.coords()) - np.array(metal_atom.coords())

        min_cshm = np.inf
        orders = permutations(range(len(ideal_polyhedron)))

        # Make it so the ideal polyhedron has same average bond distance as the mol.
        scaled_polyhedron = ideal_polyhedron * np.mean(np.array(distances))

        # For all possible assignments, find CShM between ideal and actual structure.
        ideal_positions = np.zeros([len(fcs_indices), 3])
        for order in orders:
            # Assign reference structure for pairwise matching.
            for i in range(len(order)):
                ideal_positions[i, :] = scaled_polyhedron[order[i]]
            # Rotate reference structure onto actual positions.
            ideal_positions = kabsch_rotate(ideal_positions, positions)
            # Could allow for another global scale factor on ideal_positions here, not done to maintain same avg bond lengths.
            numerator = sum(np.vstack([np.linalg.norm(positions[i] - ideal_positions[i]) for i in range(len(positions))]))[0]
            centroid = np.mean(positions, axis=0)
            denominator = sum(np.vstack([np.linalg.norm(positions[i] - centroid) for i in range(len(positions))]))[0]
            cshm = numerator / denominator * 100
            if cshm < min_cshm:
                min_cshm = cshm

        # return minimum CShM
        return min_cshm

    def convert2OBMol(self, force_clean=False, ignoreX=False):
        """
        Converts mol3D class instance to OBMol class instance.
        Stores as OBMol attribute. Necessary for force field optimizations
        and other openbabel operations.

        Parameters
        ----------
            force_clean : bool, optional
                Force no bond info retention. Default is False.
            ignoreX : bool, optional
                Ignore X element when writing. Default is False.
        """

        # Get BO matrix if exits:
        repop = False

        if self.OBMol and not force_clean:
            bo_mat = self.populateBOMatrix()
            repop = True
        elif self.bo_mat.size != 0 and not force_clean:
            bo_mat = self.bo_mat
            repop = True

        # Write temporary xyz.
        fd, tempf = tempfile.mkstemp(suffix=".xyz")
        os.close(fd)
        self.writexyz(tempf, symbsonly=True, ignoreX=ignoreX)

        obConversion = openbabel.OBConversion()
        obConversion.SetInFormat("xyz")

        OBMol = openbabel.OBMol()
        obConversion.ReadFile(OBMol, tempf)

        self.OBMol = OBMol

        os.remove(tempf)

        if repop and not force_clean:
            self.cleanBonds()
            for i in range(0, self.natoms):
                for j in range(0, self.natoms):
                    if bo_mat[i][j] > 0:
                        self.OBMol.AddBond(i + 1, j + 1, int(bo_mat[i][j]))

    def convert2OBMol2(self, ignoreX=False):
        """
        Converts mol3D class instance to OBMol class instance, but uses mol2
        function, so bond orders are not interpreted, but rather read through the mol2.
        Stores as OBMol attribute. Necessary for force field optimizations
        and other openbabel operations.

        Parameters
        ----------
            ignoreX : bool, optional
                Ignore X element when writing. Default is False.
        """

        # Get BO matrix if exits:
        obConversion = openbabel.OBConversion()
        obConversion.SetInFormat('mol2')
        if self.bo_dict:
            mol2string = self.writemol2('temporary', writestring=True,
                                        ignoreX=ignoreX)
            OBMol = openbabel.OBMol()
            obConversion.ReadString(OBMol, mol2string)
            self.OBMol = OBMol
            self.populateBOMatrix(bonddict=False, set_bo_mat=True)
        else:  # If bonddict not assigned - Use OBMol to perceive bond orders
            mol2string = self.writemol2('temporary', writestring=True,
                                        ignoreX=ignoreX, force=True)
            OBMol = openbabel.OBMol()
            obConversion.ReadString(OBMol, mol2string)
            OBMol.PerceiveBondOrders()
            #####
            obConversion.SetOutFormat('mol2')
            ss = obConversion.WriteString(OBMol)
            # Update atom types from OBMol.
            if "UNITY_ATOM_ATTR" in ss:  # If this section is present, it will be before the @<TRIPOS>BOND section.
                lines = ss.split('ATOM\n')[1].split(
                    '@<TRIPOS>UNITY_ATOM_ATTR')[0].split('\n')[:-1]
            else:
                lines = ss.split('ATOM\n')[1].split(
                    '@<TRIPOS>BOND')[0].split('\n')[:-1]
            for i, line in enumerate(lines):
                if '.' in line.split()[5]:
                    self.atoms[i].name = line.split()[5].split('.')[1]
            ######
            self.OBMol = OBMol
            self.populateBOMatrix(bonddict=True, set_bo_mat=True)

    def convert2mol3D(self):
        """
        Converts OBMol class instance to mol3D class instance.
        Generally used after openbabel operations, such as FF optimizing a molecule.
        Updates the mol3D as necessary.
        """

        original_graph = self.graph
        self.initialize()
        self.graph = original_graph
        # get elements dictionary
        elem = globalvars().elementsbynum()
        # loop over atoms
        for atom in openbabel.OBMolAtomIter(self.OBMol):
            # get coordinates
            pos = [atom.GetX(), atom.GetY(), atom.GetZ()]
            # get atomic symbol
            sym = elem[atom.GetAtomicNum() - 1]
            # add atom to molecule
            self.addAtom(atom3D(sym, pos))
        # reset metal ID
        self.metals = None

    def convexhull(self):
        """
        Computes convex hull of molecule.

        Returns
        -------
            hull : array
                Coordinates of convex hull.
        """

        points = []
        # loop over atoms in protein
        if self.natoms > 0:
            for atom in self.atoms:
                points.append(atom.coords())
            hull = ConvexHull(points)
        else:
            hull = False
            print(
                'ERROR: Convex hull calculation failed. Structure will be inaccurate.\n')
        self.hull = hull

    def coords(self, no_tabs=False):
        """
        Method to obtain string of coordinates in molecule.

        Parameters
        ----------
            no_tabs : bool, optional
                Whether or not to use tabs in coordinate columns.

        Returns
        -------
            coord_string : string
                String of molecular coordinates with atom identities in XYZ format.
        """

        coord_string = ''  # initialize returning string
        coord_string += f"{self.natoms} \n\n"
        for atom in self.atoms:
            xyz = atom.coords()
            coord_string += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        if no_tabs:
            coord_string = coord_string.replace('\t', ' ' * 8)
        return coord_string

    def coordsvect(self):
        """
        Method to obtain array of coordinates in molecule.

        Returns
        -------
            list_of_coordinates : np.array
                Two dimensional numpy array of molecular coordinates.
                (N by 3) dimension, N is number of atoms.
        """

        list_of_coordinates = []
        for atom in self.atoms:
            xyz = atom.coords()
            list_of_coordinates.append(xyz)
        return np.array(list_of_coordinates)

    def copymol3D(self, mol0):
        """
        Copies properties and atoms of another existing mol3D object
        into current mol3D object. Should be performed on a new mol3D class
        instance. WARNING: NEVER EVER USE mol3D = mol0 to do this. It DOES NOT
        WORK. ONLY USE ON A FRESH INSTANCE OF MOL3D. Operates on fresh instance.

        Parameters
        ----------
            mol0 : mol3D
                mol3D of molecule to be copied.
        """

        # copy atoms
        for i, atom0 in enumerate(mol0.atoms):
            self.addAtom(atom3D(atom0.sym, atom0.coords(), atom0.name))
            if atom0.frozen:
                self.getAtom(i).frozen = True
        # copy other attributes
        self.cat = mol0.cat
        self.charge = mol0.charge
        self.denticity = mol0.denticity
        self.ident = mol0.ident
        self.ffopt = mol0.ffopt
        self.OBMol = mol0.OBMol
        self.name = mol0.name
        self.graph = mol0.graph
        self.bo_mat = mol0.bo_mat
        self.bo_dict = mol0.bo_dict
        self.use_atom_specific_cutoffs = mol0.use_atom_specific_cutoffs

    def count_atoms(self, exclude=['H', 'h', 'x', 'X']):
        """
        Count the number of atoms, excluding certain atoms.

        Parameters
        ----------
            exclude: list
                list of symbols for atoms to exclude.

        Returns
        -------
            count: integer
                the number of heavy atoms
        """

        count = 0
        for ii in range(self.natoms):
            if not self.getAtom(ii).symbol() in exclude:
                count += 1
        return count

    def count_electrons(self, charge=0):
        """
        Count the number of electrons in a molecule.

        Parameters
        ----------
            charge: int, optional
                Net charge of a molecule. Default is neutral.

        Returns
        -------
            count: integer
                The number of electrons in the system.
        """

        count = 0
        for ii in range(self.natoms):
            count += self.getAtom(ii).atno
        count = count-charge
        return count

    def count_nonH_atoms(self):
        """
        Count the number of heavy atoms.

        Returns
        -------
            count: integer
                the number of heavy atoms
        """

        count = 0
        for ii in range(self.natoms):
            if not self.getAtom(ii).symbol() in ["H", "h"]:
                count += 1
        return count

    def count_specific_atoms(self, atom_types=['x', 'X']):
        """
        Count the number of atoms, including only certain atoms.

        Parameters
        ----------
            atom_types: list
                list of symbols for atoms to include.

        Returns
        -------
            count: integer
                the number of heavy atoms
        """

        count = 0
        for ii in range(self.natoms):
            if self.getAtom(ii).symbol() in atom_types:
                count += 1
        return count

    def createMolecularGraph(self, oct=True, strict_cutoff=False, catom_list=None):
        """
        Create molecular graph of a molecule given X, Y, Z positions.
        Bond order is not interpreted by this. Updates graph attribute
        of the mol3D class.

        Parameters
        ----------
            oct : bool
                Defines whether a structure is octahedral. Default is True.
            strict_cutoff: bool, optional
                Strict bonding cutoff for fullerene and SACs.
            catom_list: list of int, optional
                List of indices of bonded atoms.
        """

        if not len(self.graph):
            index_set = list(range(0, self.natoms))
            A = np.zeros((self.natoms, self.natoms))
            catoms_metal = list()
            metal_ind = None
            for i in index_set:
                if oct:
                    if self.getAtom(i).ismetal():
                        this_bonded_atoms = self.get_fcs(strict_cutoff=strict_cutoff, catom_list=catom_list)
                        metal_ind = i
                        catoms_metal = this_bonded_atoms
                        if i in this_bonded_atoms:
                            this_bonded_atoms.remove(i)
                    else:
                        this_bonded_atoms = self.getBondedAtomsOct(i, debug=False,
                                                                   atom_specific_cutoffs=self.use_atom_specific_cutoffs,
                                                                   strict_cutoff=strict_cutoff)
                else:
                    this_bonded_atoms = self.getBondedAtoms(i)
                for j in index_set:
                    if j in this_bonded_atoms:
                        A[i, j] = 1
            if metal_ind is not None:
                for i in index_set:
                    if i not in catoms_metal:
                        A[i, metal_ind] = 0
                        A[metal_ind, i] = 0
            if catom_list is not None:
                geo_based_catoms = self.get_fcs(strict_cutoff=strict_cutoff)
                for ind in geo_based_catoms:
                    if ind not in catom_list:
                        A[ind, metal_ind] = 0
                        A[metal_ind, ind] = 0
            self.graph = A

    def create_mol_with_inds(self, inds):
        """
        Create molecule with indices.

        Parameters
        ----------
            inds : list
                The indices of the selected submolecule to SAVE

        Returns
        -------
            molnew : mol3D
                The new molecule built from the indices.
        """

        molnew = mol3D()
        inds = sorted(inds)
        for ind in inds:
            atom = atom3D(self.atoms[ind].symbol(
            ), self.atoms[ind].coords(), self.atoms[ind].name)
            molnew.addAtom(atom)
        if self.bo_dict:
            save_bo_dict = self.get_bo_dict_from_inds(inds)
            molnew.bo_dict = save_bo_dict
        if len(self.graph):
            delete_inds = [x for x in range(self.natoms) if x not in inds]
            molnew.graph = np.delete(
                np.delete(self.graph, delete_inds, 0), delete_inds, 1)
        if len(self.bo_mat):
            delete_inds = [x for x in range(self.natoms) if x not in inds]
            molnew.bo_mat = np.delete(
                np.delete(self.bo_mat, delete_inds, 0), delete_inds, 1)
        return molnew

    def deleteHs(self):
        """
        Delete all hydrogens from a molecule. Preserves heavy atom ordering.
        """

        hlist = []
        for i in range(self.natoms):
            if self.getAtom(i).sym == 'H':  # and i not in metalcons:
                hlist.append(i)
        self.deleteatoms(hlist)

    def deleteatom(self, atomIdx):
        """
        Delete a specific atom from the mol3D class given an index.

        Parameters
        ----------
            atomIdx : int
                Index for the atom3D to remove.
        """

        if atomIdx < 0:
            atomIdx = self.natoms + atomIdx
        if atomIdx >= self.natoms:
            raise IndexError(f'mol3D object cannot delete atom {atomIdx}' +
                             f' because it only has {self.natoms} atoms!')
        if self.getAtom(atomIdx).sym == 'X':
            self.atoms[atomIdx].sym = 'Fe'  # Switch to Iron temporarily
            self.atoms[atomIdx].name = 'Fe'
        if self.bo_dict:
            self.convert2OBMol2()
            save_inds = [x for x in range(self.natoms) if x != atomIdx]
            save_bo_dict = self.get_bo_dict_from_inds(save_inds)
            self.bo_dict = save_bo_dict
        else:
            self.convert2OBMol()
        print(atomIdx, 'from inside mol3d')
        self.OBMol.DeleteAtom(self.OBMol.GetAtom(atomIdx + 1))
        self.mass -= self.getAtom(atomIdx).mass
        self.natoms -= 1
        if len(self.graph):
            self.graph = np.delete(
                np.delete(self.graph, atomIdx, 0), atomIdx, 1)
        if len(self.bo_mat):
            self.bo_mat = np.delete(
                np.delete(self.bo_mat, atomIdx, 0), atomIdx, 1)
        self.metals = None
        del (self.atoms[atomIdx])

    def deleteatoms(self, Alist):
        """
        Delete a multiple atoms from the mol3D class given a set of indices.
        Preserves ordering, starts from largest index.

        Parameters
        ----------
            Alist : list of int
                List of indices for atom3D instances to remove.
        """

        for i in Alist:
            if i > self.natoms:
                raise IndexError(f'mol3D object cannot delete atom {i}' +
                                 f' because it only has {self.natoms} atoms!')
        # Convert negative indexes to positive indexes.
        Alist = [self.natoms+i if i < 0 else i for i in Alist]
        for atomIdx in Alist:
            if self.getAtom(atomIdx).sym == 'X':
                self.atoms[atomIdx].sym = 'Fe'  # Switch to Iron temporarily.
                self.atoms[atomIdx].name = 'Fe'
        if self.bo_dict:
            self.convert2OBMol2()
            save_inds = [x for x in range(self.natoms) if x not in Alist]
            save_bo_dict = self.get_bo_dict_from_inds(save_inds)
            self.bo_dict = save_bo_dict
        else:
            self.convert2OBMol()
        for h in sorted(Alist, reverse=True):
            self.OBMol.DeleteAtom(self.OBMol.GetAtom(int(h) + 1))
            self.mass -= self.getAtom(h).mass
            self.natoms -= 1
            del (self.atoms[h])
        if len(self.graph):
            self.graph = np.delete(np.delete(self.graph, Alist, 0), Alist, 1)
        if len(self.bo_mat):
            self.bo_mat = np.delete(np.delete(self.bo_mat, Alist, 0), Alist, 1)
        self.metals = None

    def dev_from_ideal_geometry(self, ideal_polyhedron: np.ndarray) -> Tuple[float, float]:
        """
        Return the minimum RMSD between a geometry and an ideal polyhedron (with the same average bond distances).
        Enumerates all possible indexing of the geometry. As such, only recommended for small systems.

        Parameters
        ----------
            ideal_polyhedron: np.array of 3-tuples of coordinates
                Reference list of points for an ideal geometry

        Returns
        -------
            rmsd: float
                Minimum root mean square distance between the fed geometry and the ideal polyhedron
            single_dev: float
                Maximum distance between any paired points in the fed geometry and the ideal polyhedron.
        """

        metal_idx = self.findMetal()
        if len(metal_idx) == 0:
            raise ValueError('No metal centers exist in this complex.')
        elif len(metal_idx) != 1:
            raise ValueError('Multimetal complexes are not yet handled.')
        temp_mol = self.get_first_shell()[0]
        fcs_indices = temp_mol.get_fcs(max6=False)
        # Remove metal index from first coordination shell.
        fcs_indices.remove(temp_mol.findMetal()[0])

        if len(fcs_indices) != len(ideal_polyhedron):
            raise ValueError('The coordination number differs between the two provided structures.')

        # Have to redo getting metal_idx with the new mol after running get_first_shell
        # Want to work with temp_mol since it has the edge and sandwich logic implemented to replace those with centroids.
        metal_atom = temp_mol.getAtoms()[temp_mol.findMetal()[0]]
        fcs_atoms = [temp_mol.getAtoms()[i] for i in fcs_indices]
        # Construct an np array of the non-metal atoms in the FCS.
        distances = []
        positions = np.zeros([len(fcs_indices), 3])
        for idx, atom in enumerate(fcs_atoms):
            distance = atom.distance(metal_atom)
            distances.append(distance)
            # Shift so the metal is at (0, 0, 0)
            positions[idx, :] = np.array(atom.coords()) - np.array(metal_atom.coords())

        current_min = np.inf
        orders = permutations(range(len(ideal_polyhedron)))
        max_dist = 0

        # If desired, make it so the ideal polyhedron has same average bond distance as the mol.
        # scaled_polyhedron = ideal_polyhedron * np.mean(np.array(distances))

        # For all possible assignments, find RMSD between ideal and actual structure.
        ideal_positions = np.zeros([len(fcs_indices), 3])
        for order in orders:
            for i in range(len(order)):
                # If you wanted to use the same average bond length for all, use the following
                # ideal_positions[i, :] = scaled_polyhedron[order[i]]
                # If you want to let each ligand scale its length independently, uncomment the following.
                ideal_positions[i, :] = ideal_polyhedron[order[i]] * distances[i]
            rmsd_calc = kabsch_rmsd(ideal_positions, positions)
            if rmsd_calc < current_min:
                current_min = rmsd_calc
                # Calculate and store the maximum pairwise distance.
                rot_ideal = kabsch_rotate(ideal_positions, positions)
                diff_matrix = rot_ideal - positions
                pairwise_dists = np.sum(diff_matrix**2, axis=1)
                max_dist = np.max(pairwise_dists)

        # Return minimum RMSD, maximum pairwise distance in that structure.
        return current_min, max_dist

    def dict_check_processing(self, dict_check, num_coord=6, debug=False, silent=False):
        """
        Process the self.geo_dict to get the flag_oct and flag_list, setting dict_check as the cutoffs.

        Parameters
        ----------
            dict_check : dict
                The cutoffs of each geo_check metrics we have.
            num_coord : int, optional
                Metal coordination number. Default is 6.
            debug : bool, optional
                Flag for extra printout. Default is False.
            silence : bool, optional
                Flag for warning suppression. Default is False.

        Returns
        -------
            flag_oct : int
                Good (1) or bad (0) structure.
            flag_list : list
                Metrics that are preventing a good geometry.
        """

        self.geo_dict['num_coord_metal'] = int(self.num_coord_metal)
        self.geo_dict.update(self.dict_lig_distort)
        self.geo_dict.update(self.dict_catoms_shape)
        self.geo_dict.update(self.dict_orientation)
        banned_sign = 'banned_by_user'
        if debug:
            print(('dict_oct_info', self.geo_dict))
        for ele in self.std_not_use:
            self.geo_dict[ele] = banned_sign
        self.geo_dict['atom_dist_max'] = banned_sign
        flag_list = []
        for key, values in list(dict_check.items()):
            if isinstance(self.geo_dict[key], (int, float)):
                if self.geo_dict[key] > values:
                    flag_list.append(key)
            elif not self.geo_dict[key] == banned_sign:
                flag_list.append(key)
        if self.geo_dict['num_coord_metal'] < num_coord:
            flag_list.append('num_coord_metal')
        if flag_list == ['num_coord_metal'] and \
                (self.geo_dict['num_coord_metal'] == -1 or self.geo_dict['num_coord_metal'] > num_coord):
            self.geo_dict['num_coord_metal'] = num_coord
            flag_list.remove('num_coord_metal')
        if len(flag_list):
            flag_oct = 0
            flag_list = '; '.join(flag_list)
            if not silent:
                print('------bad structure!-----')
                print(('flag_list:', flag_list))
        else:
            flag_oct = 1  # Good structure
            flag_list = 'None'

        self.flag_oct = flag_oct
        self.flag_list = flag_list
        return flag_oct, flag_list, self.geo_dict

    def distance(self, mol):
        """
        Measure the distance between center of mass of two molecules.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance of second molecule to measure distance to.

        Returns
        -------
            d_cm : float
                Distance between centers of mass of two molecules.
        """

        cm0 = self.centermass()
        cm1 = mol.centermass()
        d_cm = distance(cm0, cm1)
        return d_cm

    def draw_svg(self, filename):
        """
        Draw image of molecule and save to SVG.

        Parameters
        ----------
            filename : str
                Name of file to save SVG to.
        """

        obConversion = openbabel.OBConversion()
        obConversion.SetOutFormat("svg")
        obConversion.AddOption("i", obConversion.OUTOPTIONS, "")
        # Return the svg with atom labels as a string.
        svgstr = obConversion.WriteString(self.OBMol)
        namespace = "http://www.w3.org/2000/svg"
        ET.register_namespace("", namespace)
        tree = ET.fromstring(svgstr)
        svg = tree.find("{{{ns}}}g/{{{ns}}}svg".format(ns=namespace))
        newsvg = ET.tostring(svg).decode("utf-8")
        # Write unpacked svg file.
        fname = filename + '.svg'
        with open(fname, "w") as svg_file:
            svg_file.write(newsvg)
        print('SVG file written to directory.')

    def findAtomsbySymbol(self, sym: str) -> List[int]:
        """
        Find all elements with a given symbol in a mol3D class.

        Parameters
        ----------
            sym : str
                Symbol of the atom of interest.

        Returns
        -------
            atom_list : list of int
                List of indices of atoms in mol3D with a given symbol.
        """

        atomlist = []
        for i, atom in enumerate(self.atoms):
            if atom.sym == sym:
                atomlist.append(i)
        return atomlist

    def findMetal(self, transition_metals_only: bool = True,
        include_X: bool = False) -> List[int]:
        """
        Find metal(s) in a mol3D class.
        Also sets the metals instance attribute if it is empty.

        Parameters
        ----------
            transition_metals_only : bool, optional
                Only find transition metals.
                Default is True.
            include_X : bool, optional
                Whether "X" atoms are considered metals.
                Default is False.

        Returns
        -------
            metal_list : list of int
                List of indices of metal atoms in mol3D.
        """

        if self.metals is None:
            metal_list = []
            for i, atom in enumerate(self.atoms):
                if atom.ismetal(transition_metals_only=transition_metals_only, include_X=include_X):
                    metal_list.append(i)
            self.metals = metal_list.copy()
        else:
            metal_list = self.metals.copy()
        return metal_list

    def findcloseMetal(self, atom0):
        """
        Find the nearest metal to a given atom3D class.
        Returns heaviest element if no metal found.

        Parameters
        ----------
            atom_idx : atom3D
                atom3D class for atom of interest.

        Returns
        -------
            close_metal : int
                index of the nearest metal, or heaviest atom if no metal found.
        """

        close_metal = None
        mindist = 1000
        for i in self.findMetal():
            atom = self.getAtom(i)
            if distance(atom.coords(), atom0.coords()) < mindist:
                mindist = distance(atom.coords(), atom0.coords())
                close_metal = i
        # If no metal, find heaviest atom.
        if close_metal is None:
            maxaw = 0
            for i, atom in enumerate(self.atoms):
                if atom.atno > maxaw:
                    close_metal = i
        return close_metal

    def findsubMol(self, atom0, atomN, smart=False):
        """
        Finds a submolecule within the molecule given the starting atom and the separating atom.
        Illustration: H2A-B-C-DH2 will return C-DH2 if C is the starting atom and B is the separating atom.
        Alternatively, if C is the starting atom and D is the separating atom, returns H2A-B-C.

        Parameters
        ----------
            atom0 : int
                Index of starting atom.
            atomN : int
                Index of the separating atom.
            smart : bool, optional
                Decision of whether or not to use getBondedAtomsSmart. Default is False.

        Returns
        -------
            subm : list of int
                List of indices of atoms in submolecule.
        """

        if atom0 == atomN:
            raise ValueError("atom0 cannot be the same as atomN!")
        subm = []
        conatoms = [atom0]
        if smart:
            conatoms += self.getBondedAtomsSmart(atom0)
        else:
            conatoms += self.getBondedAtoms(atom0)  # Connected atoms to atom0

        if atomN in conatoms:
            conatoms.remove(atomN)  # Check for idxN and remove.
        subm += conatoms            # Add to submolecule.
        while len(conatoms) > 0:    # While list of atoms to check loop.
            for atidx in subm:      # Loop over initial connected atoms.
                if atidx != atomN:  # Check for separation atom.
                    if smart:
                        newcon = self.getBondedAtomsSmart(atidx)
                    else:
                        newcon = self.getBondedAtoms(atidx)

                    if atomN in newcon:
                        newcon.remove(atomN)
                    for newat in newcon:
                        if newat not in conatoms and newat not in subm:
                            conatoms.append(newat)
                            subm.append(newat)
                if atidx in conatoms:
                    conatoms.remove(atidx)  # Remove from list to check.
        return subm

    def flip_symmetry(self, verbose=True, max_allowed_dev=30, target_symmetry=None):
        """
        Flip octahedral transition metal complexes (TMCs) to opposite symmetry group.
        Example: cis to trans, fac to mer, etc.

        Parameters
        ----------
            verbose: bool
                Flag for returning warning when TMC exhibits high deviation from closest symmetry.
                Default=True
            max_allowed_dev: float
                Maximum allowed deviation before warning is triggered (degrees).
                Default=30
            target_symmetry: str
                Target symmetry for complex to be transformed to, only defined for num_unique_ligands == 3
                Default=None

        Returns
        -------
            self: mol3D
                returns self, a mol3D object with flipped symmetry
        """

        symmetry_dict, detailed_dict, = self.get_symmetry(verbose=verbose, max_allowed_dev=max_allowed_dev,
                                                          details=True)
        symmetry = symmetry_dict['symmetry']
        num_unique_ligands = detailed_dict['num_unique_ligands']
        unique_ligand_ratios = detailed_dict['unique_ligand_ratios']
        metal_idx = detailed_dict['metal_idx']
        lig1_atoms = detailed_dict['lig1_atoms']
        lig1_catoms = detailed_dict['lig1_catoms']
        lig2_atoms = detailed_dict['lig2_atoms']
        lig2_catoms = detailed_dict['lig2_catoms']
        lig3_atoms = detailed_dict['lig3_atoms']
        lig3_catoms = detailed_dict['lig3_catoms']
        target_symmetry = target_symmetry.upper() if target_symmetry else target_symmetry

        if num_unique_ligands == 1:
            raise ValueError('Function not defined for homoleptic complexes')
        # Two unique ligands: consider cis/trans and fac/mer conversions.
        elif num_unique_ligands == 2:
            if unique_ligand_ratios == 5:
                raise ValueError('Function not defined for monoheteroleptic complexes')
            # cis/trans conversion
            elif unique_ligand_ratios == 2:
                # idx of ligand type 1 to be swapped (only relevant for cis-->trans conversion)
                swap_idx_1 = np.argmin(
                    np.abs(np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                                     self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig2_catoms[1]),
                                     self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig2_catoms[1]),
                                     self.getAngle(idx0=lig1_catoms[3], idx1=metal_idx, idx2=lig2_catoms[1]))) - 180))
                # idx of ligand type 2 to be swapped (any ligand2 is valid as long as ligand1 is orthogonal)
                swap_idx_2 = 0
            # fac/mer conversion
            elif unique_ligand_ratios == 1:
                if symmetry == 'mer':
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmin(
                        np.abs(np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                                         self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]))) - 180)) + 1
                    # idx of ligand type 2 to be swapped
                    swap_idx_2 = np.argmin(
                        np.abs(np.array((self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                                         self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[2]))) - 180)) + 1
                elif symmetry == 'fac':
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmin(
                        np.abs(np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig2_catoms[0]),
                                         self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig2_catoms[0]),
                                         self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig2_catoms[0]))) - 90))
                    # idx of ligand type 2 to be swapped (any ligand2 is valid as long as ligand1 is orthogonal)
                    swap_idx_2 = 0
            lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
            lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
            # Define all atoms to be moved, i.e., all atoms in both ligands that will be moved.
            atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                      swap_indices=[swap_idx_1, swap_idx_2],
                                                      catoms=[lig1_catoms, lig2_catoms])
            self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                lig1_catom_coords=lig1_catom_coords,
                                lig2_catom_coords=lig2_catom_coords,
                                atoms_to_move=atoms_to_move)
        # Three unique ligands: consider cis asymmetric (CA)/trans asymmetric (TA),
        # double cis symmetric (DCS)/ double trans symmetric (DTS)/equatorial asymmetric (EA),
        # and fac asymmetric (FA)/mer asymmetric trans (MAT)/mer asymmetric cis (MAC) conversions.
        elif num_unique_ligands == 3:
            # CA/TA conversion
            if unique_ligand_ratios == [4, 1, 4]:
                # idx of ligand type 1 to be swapped
                # Only relevant for CA-->TA conversion, since TA-->CA can be accomplished by switching any two distinct ligands.
                swap_idx_1 = np.argmin(
                    np.abs(np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig3_catoms[0]),
                                     self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig3_catoms[0]),
                                     self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig3_catoms[0]),
                                     self.getAngle(idx0=lig1_catoms[3], idx1=metal_idx, idx2=lig3_catoms[0]))) - 180))
                # idx of ligand type 2 to be swapped
                swap_idx_2 = 0
                lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                          swap_indices=[swap_idx_1, swap_idx_2],
                                                          catoms=[lig1_catoms, lig2_catoms])
                self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                    lig1_catom_coords=lig1_catom_coords,
                                    lig2_catom_coords=lig2_catom_coords,
                                    atoms_to_move=atoms_to_move)
            # DCS/DTS/EA conversion
            elif unique_ligand_ratios == [1, 1, 1]:
                # Warning: moves L3 to axial position by default, using ligand sorting order from get_symmetry()
                symmetry_abbr = {'double cis symmetric': 'DCS', 'double trans symmetric': 'DTS',
                                 'equatorial asymmetric': 'EA'}
                allowed_symmetries = ['DCS', 'DTS', 'EA']
                allowed_symmetries.remove(symmetry_abbr[symmetry])
                if not target_symmetry or target_symmetry not in allowed_symmetries:
                    raise ValueError("target_symmetry must be either " + allowed_symmetries[0] + " or "
                                     + allowed_symmetries[1] + " for " + symmetry_abbr[symmetry] + " complexes")
                # DTS to EA
                elif target_symmetry == 'EA' and symmetry == 'double trans symmetric':
                    # idx of ligand types 1 and 2 to be swapped
                    swap_idx_1 = 0
                    swap_idx_2 = 0
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords,
                                        lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                # DCS to EA
                elif target_symmetry == 'EA' and symmetry == 'double cis symmetric':
                    # Warning: moves L3 to axial position by default, using ligand sorting order from get_symmetry()
                    # idx of ligand type 2 to be swapped (that which forms 90° angles with both ligands of type 1)
                    swap_idx_2 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig2_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig2_catoms[0]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig2_catoms[1]))) - 90)))))
                    # idx of ligand type 3 to be swapped (that which forms 90° angles with both ligands of type 2)
                    swap_idx_3 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig3_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig3_catoms[0]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig3_catoms[1]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig3_catoms[1]))) - 90)))))
                    lig1_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig2_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_2, swap_idx_3],
                                                              catoms=[lig2_catoms, lig3_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords,
                                        lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                # EA to DTS
                elif target_symmetry == 'DTS' and symmetry == 'equatorial asymmetric':
                    # Figure out which ligands are axial.
                    axial_idx = np.argmin(np.abs(np.array((
                        self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                        self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                        self.getAngle(idx0=lig3_catoms[0], idx1=metal_idx, idx2=lig3_catoms[1]))) - 180))
                    # Figure out which ligands are not axial (i.e., equatorial).
                    equatorial_idx = [val for val in range(3) if val != axial_idx]
                    all_ligand_catoms = [lig1_catoms, lig2_catoms, lig3_catoms]
                    all_ligand_atoms = [lig1_atoms, lig2_atoms, lig3_atoms]
                    # idx of equatorial ligand 1 to be swapped (choose arbitarily, then choose swap_idx_2 accordingly)
                    swap_idx_1 = 0
                    # idx of equatorial ligand 2 to be swapped
                    swap_idx_2 = np.argmin(np.abs(np.array((
                        self.getAngle(idx0=all_ligand_catoms[equatorial_idx[0]][swap_idx_1], idx1=metal_idx,
                                         idx2=all_ligand_catoms[equatorial_idx[1]][0]),
                        self.getAngle(idx0=all_ligand_catoms[equatorial_idx[0]][swap_idx_1], idx1=metal_idx,
                                         idx2=all_ligand_catoms[equatorial_idx[1]][1]))) - 90))

                    lig1_catom_coords = np.array(self.atoms[all_ligand_catoms[equatorial_idx[0]][swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[all_ligand_catoms[equatorial_idx[1]][swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[all_ligand_atoms[equatorial_idx[0]],
                                                                       all_ligand_atoms[equatorial_idx[1]]],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[all_ligand_catoms[equatorial_idx[0]],
                                                                       all_ligand_catoms[equatorial_idx[1]]])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords,
                                        lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                # DCS to DTS
                elif target_symmetry == 'DTS' and symmetry == 'double cis symmetric':
                    # idx of ligand type 1 to be swapped (that which forms 90° angles with both ligands of type 3)
                    swap_idx_1 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig3_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig3_catoms[1]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig3_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig3_catoms[1]))) - 90)))))
                    # idx of ligand type 2 to be swapped (that which forms 90° angles with both ligands of type 1)
                    swap_idx_2 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[1]))) - 90)))))
                    # idx of ligand type 3 to be swapped (that which forms 90° angles with both ligands of type 2)
                    swap_idx_3 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig3_catoms[0], idx1=metal_idx, idx2=lig2_catoms[0]),
                            self.getAngle(idx0=lig3_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig3_catoms[1], idx1=metal_idx, idx2=lig2_catoms[0]),
                            self.getAngle(idx0=lig3_catoms[1], idx1=metal_idx, idx2=lig2_catoms[1]))) - 90)))))
                    # first reflection
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                    # second reflection
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_3],
                                                              catoms=[lig1_catoms, lig3_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                # DTS to DCS
                elif target_symmetry == 'DCS' and symmetry == 'double trans symmetric':
                    # These operations can result in unique chiral structures.
                    # idx of ligand types 1, 2, and 3 to be swapped
                    swap_idx_1 = 0
                    swap_idx_2 = 0
                    swap_idx_3 = 0
                    # first reflection
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                    # second reflection
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_3],
                                                              catoms=[lig1_catoms, lig3_catoms])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
                # EA to DCS
                elif target_symmetry == 'DCS' and symmetry == 'equatorial asymmetric':
                    # These operations can result in unique chiral structures.
                    # Figure out which ligands are axial.
                    axial_idx = np.argmin(np.abs(np.array((
                        self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                        self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                        self.getAngle(idx0=lig3_catoms[0], idx1=metal_idx, idx2=lig3_catoms[1]))) - 180))
                    # figure out which ligands are not axial (i.e., equatorial)
                    equatorial_idx = [val for val in range(3) if val != axial_idx]
                    all_ligand_catoms = [lig1_catoms, lig2_catoms, lig3_catoms]
                    all_ligand_atoms = [lig1_atoms, lig2_atoms, lig3_atoms]
                    lig1_catom_coords = np.array(self.atoms[all_ligand_catoms[axial_idx][0]].coords())
                    lig2_catom_coords = np.array(self.atoms[all_ligand_catoms[equatorial_idx[0]][0]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[all_ligand_atoms[axial_idx],
                                                                       all_ligand_atoms[equatorial_idx[0]]],
                                                              swap_indices=[0, 0],
                                                              catoms=[all_ligand_catoms[axial_idx],
                                                                      all_ligand_catoms[equatorial_idx[0]]])
                    self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                        lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                        atoms_to_move=atoms_to_move)
            # FA/MAT/MAC conversion
            elif unique_ligand_ratios == [3 / 2, 2, 3]:
                symmetry_abbr = {'fac asymmetric': 'FA', 'mer asymmetric cis': 'MAC', 'mer asymmetric trans': 'MAT'}
                allowed_symmetries = ['FA', 'MAT', 'MAC']
                allowed_symmetries.remove(symmetry_abbr[symmetry])
                if not target_symmetry or target_symmetry not in allowed_symmetries:
                    raise ValueError("target_symmetry must be either " + allowed_symmetries[0] + " or "
                                     + allowed_symmetries[1] + " for " + symmetry_abbr[symmetry] + " complexes")
                # MAT to FA
                elif target_symmetry == 'FA' and symmetry == 'mer asymmetric trans':
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmax(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig1_catoms[1]))) - 90)))))
                    # idx of ligand type 2 to be swapped
                    swap_idx_2 = 0
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                # MAC to FA
                elif target_symmetry == 'FA' and symmetry == 'mer asymmetric cis':
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmax(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig1_catoms[1]))) - 90)))))
                    # idx of ligand type 2 to be swapped
                    swap_idx_2 = np.argmin(np.array((
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)))))
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                # FA to MAT
                elif target_symmetry == 'MAT' and symmetry == 'fac asymmetric':
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmin(np.abs(np.array((
                        self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig2_catoms[0]),
                        self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig2_catoms[0]),
                        self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig2_catoms[0]))) - 180))
                    # idx of ligand type 2 to be swapped
                    swap_idx_2 = 1
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig2_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_2],
                                                              catoms=[lig1_catoms, lig2_catoms])
                # MAC to MAT
                elif target_symmetry == 'MAT' and symmetry == 'mer asymmetric cis':
                    # idx of ligand type 2 to be swapped
                    swap_idx_2 = np.argmax(np.array(
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90)),
                        np.average(np.abs(np.array((
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[0]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[1]),
                            self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig1_catoms[2]))) - 90))))
                    # idx of ligand type 3 to be swapped
                    swap_idx_3 = 0
                    lig1_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig2_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_2, swap_idx_3],
                                                              catoms=[lig2_catoms, lig3_catoms])
                # FA to MAC
                elif target_symmetry == 'MAC' and symmetry == 'fac asymmetric':
                    # These operations can result in unique chiral structures.
                    # idx of ligand type 1 to be swapped
                    swap_idx_1 = np.argmin(np.abs(np.array((
                        self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig3_catoms[0]),
                        self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig3_catoms[0]),
                        self.getAngle(idx0=lig1_catoms[2], idx1=metal_idx, idx2=lig3_catoms[0]))) - 90))
                    # idx of ligand type 3 to be swapped
                    swap_idx_3 = 0
                    lig1_catom_coords = np.array(self.atoms[lig1_catoms[swap_idx_1]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig1_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_1, swap_idx_3],
                                                              catoms=[lig1_catoms, lig3_catoms])
                # MAT to MAC
                elif target_symmetry == 'MAC' and symmetry == 'mer asymmetric trans':
                    # idx of ligand types 2 and 3 to be swapped
                    swap_idx_2 = 0
                    swap_idx_3 = 0
                    lig1_catom_coords = np.array(self.atoms[lig2_catoms[swap_idx_2]].coords())
                    lig2_catom_coords = np.array(self.atoms[lig3_catoms[swap_idx_3]].coords())
                    atoms_to_move = self.choose_atoms_to_move(ligands=[lig2_atoms, lig3_atoms],
                                                              swap_indices=[swap_idx_2, swap_idx_3],
                                                              catoms=[lig2_catoms, lig3_catoms])
                self.reflect_coords(metal_coords=np.array(self.atoms[metal_idx].coords()),
                                    lig1_catom_coords=lig1_catom_coords, lig2_catom_coords=lig2_catom_coords,
                                    atoms_to_move=atoms_to_move)
        return self

    def freezeatom(self, atomIdx):
        """
        Set the freeze attribute to be true for a given atom3D class.

        Parameters
        ----------
            atomIdx : int
                Index for atom to be frozen.
        """

        self.atoms[atomIdx].frozen = True

    def freezeatoms(self, Alist):
        """
        Set the freeze attribute to be true for a given set of atom3D objects,
        given their indices. Preserves ordering, starts from largest index.

        Parameters
        ----------
            Alist : list of int
                List of indices for atom3D instances to remove.
        """

        for h in sorted(Alist, reverse=True):
            self.freezeatom(h)

    @classmethod
    def from_smiles(cls, smiles, gen3d: bool = True):
        """
        Generate a mol3D object from a SMILES string.
        """

        mol = cls()
        mol.getOBMol(smiles, "smistring", gen3d=gen3d)

        elem = globalvars().elementsbynum()
        # Add atoms
        for atom in openbabel.OBMolAtomIter(mol.OBMol):
            # Get coordinates
            pos = [atom.GetX(), atom.GetY(), atom.GetZ()]
            # Get atomic symbol
            sym = elem[atom.GetAtomicNum() - 1]
            # Add atom to molecule
            # atom3D_list.append(atom3D(sym, pos))
            mol.addAtom(atom3D(sym, pos))

        # Add bonds
        mol.graph = np.zeros([mol.natoms, mol.natoms])
        mol.bo_mat = np.zeros([mol.natoms, mol.natoms])
        for bond in openbabel.OBMolBondIter(mol.OBMol):
            i = bond.GetBeginAtomIdx() - 1
            j = bond.GetEndAtomIdx() - 1
            bond_order = bond.GetBondOrder()
            if bond.IsAromatic():
                bond_order = 1.5
            mol.graph[i, j] = mol.graph[j, i] = 1
            mol.bo_mat[i, j] = mol.bo_mat[j, i] = bond_order
            mol.bo_dict[tuple(sorted([i, j]))] = bond_order
        return mol

    def geo_dict_initialization(self):
        """
        Initialization of geometry check dictionaries according to dict_oct_check_st.
        """

        for key in self.dict_oct_check_st[list(self.dict_oct_check_st.keys())[0]]:
            self.geo_dict[key] = -1
        self.dict_lig_distort = {'rmsd_max': -1, 'atom_dist_max': -1}
        self.dict_catoms_shape = {
            'oct_angle_devi_max': -1,
            'max_del_sig_angle': -1,
            'dist_del_eq': 0,
            'dist_del_all': -1,
            'dist_del_eq_relative': 0,
            'dist_del_all_relative': -1,
        }
        self.dict_orientation = {'devi_linear_avrg': -1, 'devi_linear_max': -1}

    def geo_maxatomdist(self, mol2):
        """
        Compute the max atom distance between two molecules.
        Does not align molecules. For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            dist_max : float
                Maximum atom distance between two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        if (Nat0 != Nat1):
            print(
                "ERROR: RMSD can be calculated only for molecules with the same number of atoms..")
            return float('NaN')
        else:
            maxdist = 0
            availabel_set = list(range(Nat1))
            for atom0 in self.getAtoms():
                dist = 1000
                ind1 = False
                atom0_sym = atom0.symbol()
                for _ind1 in availabel_set:
                    atom1 = mol2.getAtom(_ind1)
                    if atom1.symbol() == atom0_sym:
                        _dist = atom0.distance(atom1)
                        if _dist < dist:
                            dist = _dist
                            ind1 = _ind1
                if dist > maxdist:
                    maxdist = dist
                availabel_set.remove(ind1)
            return maxdist

    def geo_rmsd(self, mol2):
        """
        Compute the RMSD between two molecules. Does not align molecules.
        For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            rmsd : float
                RMSD between the two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        if Nat0 == Nat1:
            rmsd = 0
            availabel_set = list(range(Nat1))
            for ii, atom0 in enumerate(self.getAtoms()):
                dist = 1000
                ind1 = False
                atom0_sym = atom0.symbol()
                for _ind1 in availabel_set:
                    atom1 = mol2.getAtom(_ind1)
                    if atom1.symbol() == atom0_sym:
                        _dist = atom0.distance(atom1)
                        if _dist < dist:
                            dist = _dist
                            ind1 = _ind1
                rmsd += dist ** 2
                availabel_set.remove(ind1)
            if Nat0 == 0:
                rmsd = 0
            else:
                rmsd /= Nat0
            return np.sqrt(rmsd)
        else:
            raise ValueError("Number of atom does not match between two mols.")

    def getAngle(self, idx0, idx1, idx2):
        """
        Get angle between three atoms identified by their indices.
        Specifically, get angle between vectors formed by atom0->atom1 and atom2->atom1.

        Parameters
        ----------
            idx0 : int
                Index of first atom.
            idx1 : int
                Index of second (middle) atom.
            idx2 : int
                Index of third atom.

        Returns
        -------
            angle : float
                Angle in degrees.
        """

        coords0 = self.getAtomCoords(idx0)
        coords1 = self.getAtomCoords(idx1)
        coords2 = self.getAtomCoords(idx2)
        v1 = (np.array(coords0) - np.array(coords1)).tolist()
        v2 = (np.array(coords2) - np.array(coords1)).tolist()
        angle = vecangle(v1, v2)
        return angle

    def getAtom(self, idx):
        """
        Get atom with a given index.

        Parameters
        ----------
            idx : int
                Index of desired atom.

        Returns
        -------
            atom : atom3D
                atom3D class for element at given index.
        """

        return self.atoms[idx]

    def getAtomCoords(self, idx):
        """
        Get atom coordinates with a given index.

        Parameters
        ----------
            idx : int
                Index of desired atom.

        Returns
        -------
            coords : list
                List of coordinates (length 3: [X, Y, Z]) for element at given index.
        """

        return self.atoms[idx].coords()

    def getAtomTypes(self):
        """
        Get unique elements in a molecule.
        Now somewhat redundant with get_element_list

        Returns
        -------
            unique_atoms_list : list
                List of unique elements in molecule by symbol.
        """

        unique_atoms_list = list()
        for atoms in self.getAtoms():
            if atoms.symbol() not in unique_atoms_list:
                unique_atoms_list.append(atoms.symbol())
        return unique_atoms_list

    def getAtoms(self):
        """
        Get all atoms within a molecule.

        Parameters
        ----------
            None

        Returns
        -------
            atom_list : list
                List of atom3D objects for all elements in a mol3D.
        """

        return self.atoms

    def getAtomwithSyms(self, syms=['X'], return_index=False):
        """
        Get atoms with a given list of symbols.

        Parameters
        ----------
            idx : list
                List of desired atom symbols.
            return_index : bool
                True or false for returning the atom indices instead of atom3D objects. Returns indices if True.

        Returns
        -------
            atom_list : list
                List of atom3D objects for elements with given symbols.
        """

        temp_list = []
        for i, atom in enumerate(self.atoms):
            if atom.symbol() in syms:
                temp_list.append(i)
        if return_index:
            return temp_list
        else:
            return [self.atoms[idx] for idx in temp_list]

    def getAtomwithinds(self, inds):
        """
        Get atoms with a given list of indices.

        Parameters
        ----------
            idx : list of int
                List of indices of desired atoms.

        Returns
        -------
            atom_list : list
                List of atom3D objects for elements at given indices.
        """

        return [self.atoms[idx] for idx in inds]

    def getBondCutoff(self, atom: atom3D, ratom: atom3D) -> float:
        """
        Get cutoff based on two atoms.

        Parameters
        ----------
            atom : atom3D
                atom3D class of first atom.
            ratom : atom3D
                atom3D class of second atom.

        Returns
        -------
            distance_max : float
                Cutoff based on atomic radii scaled by a factor.
        """

        distance_max = 1.15 * (atom.rad + ratom.rad)
        if atom.symbol() == "C" and not ratom.symbol() == "H":
            distance_max = min(2.75, distance_max)  # 2.75 by 07/22/2021
        if ratom.symbol() == "C" and not atom.symbol() == "H":
            distance_max = min(2.75, distance_max)  # 2.75 by 07/22/2021
        if ratom.symbol() == "H" and atom.ismetal():
            # Tight cutoff for metal-H bonds.
            distance_max = 1.1 * (atom.rad + ratom.rad)
        if atom.symbol() == "H" and ratom.ismetal():
            # Tight cutoff for metal-H bonds.
            distance_max = 1.1 * (atom.rad + ratom.rad)
        return distance_max

    def getBondedAtoms(self, idx: int) -> List[int]:
        """
        Gets atoms bonded to a specific atom. This is determined based on
        element-specific distance cutoffs, rather than predefined valences.
        This method is ideal for metals because bond orders are ill-defined.
        For pure organics, the OBMol class provides better functionality.

        Parameters
        ----------
            idx : int
                Index of reference atom.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        if len(self.graph):  # The graph exists.
            nats = list(np.nonzero(np.ravel(self.graph[idx]))[0])
        else:
            ratom = self.getAtom(idx)
            # Calculates adjacent number of atoms.
            nats = []
            for i, atom in enumerate(self.atoms):
                d = distance(ratom.coords(), atom.coords())
                distance_max = self.getBondCutoff(atom, ratom)
                if d < distance_max and i != idx:
                    nats.append(i)
        return nats

    def getBondedAtomsBOMatrix(self, idx):
        """
        Get atoms bonded by an atom referenced by index, using the BO matrix.

        Parameters
        ----------
            idx : int
                Index of reference atom.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        self.convert2OBMol()
        OBMatrix = self.populateBOMatrix()
        # Calculates adjacent number of atoms.
        nats = []
        for i in range(len(OBMatrix[idx])):
            if OBMatrix[idx][i] > 0:
                nats.append(i)
        return nats

    def getBondedAtomsBOMatrixAug(self, idx):
        """
        Get atoms bonded by an atom referenced by index, using the augmented BO matrix.

        Parameters
        ----------
            idx : int
                Index of reference atom.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        self.convert2OBMol()
        OBMatrix = self.populateBOMatrixAug()
        # Calculates adjacent number of atoms.
        nats = []
        for i in range(len(OBMatrix[idx])):
            if OBMatrix[idx][i] > 0:
                nats.append(i)
        return nats

    def getBondedAtomsByCoordNo(self, idx, CoordNo=6):
        """
        Gets atoms bonded to a specific atom by coordination number.

        Parameters
        ----------
            idx : int
                Index of reference atom.
            CoordNo : int, optional
                Coordination number of reference atom of interest. Default is 6.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        # Calculates adjacent number of atoms.
        nats = []
        thresholds = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]
        for i, threshold in enumerate(thresholds):
            nats = self.getBondedAtomsByThreshold(idx, threshold)
            if len(nats) == CoordNo:
                break
        if len(nats) != CoordNo:
            print(
                'Could not find the number of bonded atoms specified coordinated to the atom specified.')
            print(
                'Please either adjust the number of bonded atoms or the index of the center atom.')
            print('A list of bonded atoms is still returned. Be cautious with the list')

        return nats

    def getBondedAtomsByThreshold(self, idx, threshold=1.15):
        """
        Gets atoms bonded to a specific atom. This method uses a threshold
        for determination of a bond.

        Parameters
        ----------
            idx : int
                Index of reference atom.
            threshold : float, optional
                Scale factor for sum of covalent radii based cutoff. Default is 1.15.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        ratom = self.getAtom(idx)
        # Calculates adjacent number of atoms.
        nats = []
        for i, atom in enumerate(self.atoms):
            d = distance(ratom.coords(), atom.coords())
            distance_max = threshold * (atom.rad + ratom.rad)
            if atom.symbol() == "C" and not ratom.symbol() == "H":
                distance_max = min(2.75, distance_max)
            if ratom.symbol() == "C" and not atom.symbol() == "H":
                distance_max = min(2.75, distance_max)
            if ratom.symbol() == "H" and atom.ismetal:
                # Tight cutoff for metal-H bonds.
                distance_max = 1.1 * (atom.rad + ratom.rad)
            if atom.symbol() == "H" and ratom.ismetal:
                # Tight cutoff for metal-H bonds.
                distance_max = 1.1 * (atom.rad + ratom.rad)
            if atom.symbol() == "I" or ratom.symbol() == "I" and not (atom.symbol() == "I" and ratom.symbol() == "I"):
                distance_max = 1.05 * (atom.rad + ratom.rad)
            if atom.symbol() == "I" or ratom.symbol() == "I":
                distance_max = 0
            if d < distance_max and i != idx:
                nats.append(i)
        return nats

    def getBondedAtomsH(self, idx):
        """
        Get bonded atom with a given index, but ONLY count hydrogens.

        Parameters
        ----------
            idx : int
                Index of reference atom.

        Returns
        -------
            nats : list of int
                List of indices of bonded hydrogens.
        """

        ratom = self.getAtom(idx)
        # Calculates adjacent number of atoms.
        nats = []
        for i, atom in enumerate(self.atoms):
            if not atom.sym == 'H':
                continue
            d = distance(ratom.coords(), atom.coords())
            if atom.ismetal() or ratom.ismetal():
                distance_max = 1.35 * (atom.rad + ratom.rad)
            else:
                distance_max = 1.15 * (atom.rad + ratom.rad)
            if d < distance_max and i != idx:
                nats.append(i)
        return nats

    def getBondedAtomsOct(self, ind, CN=6, debug=False, flag_loose=False, atom_specific_cutoffs=False,
                          strict_cutoff=False):
        """
        Gets atoms bonded to an octahedrally coordinated metal. Specifically limits intruder
        C and H atoms that would otherwise be considered bonded in the distance cutoffs. Limits
        bonding to the CN closest atoms (CN = coordination number).

        Parameters
        ----------
            ind : int
                Index of reference atom.
            CN : int, optional
                Coordination number of reference atom of interest. Default is 6.
            debug : bool, optional
                Produce additional outputs for debugging. Default is False.
            flag_loose : bool, optional
                Use looser cutoffs to determine bonding. Default is False.
            atom_specific_cutoffs: bool, optional
                Use atom specific cutoffs to determing bonding. Default is False.
            strict_cutoff: bool, optional
                Strict bonding cutoff for fullerene and SACs.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        ratom = self.getAtom(ind)
        nats = []
        if len(self.graph):
            nats = list(np.nonzero(np.ravel(self.graph[ind]))[0])
        else:
            for i, atom in enumerate(self.atoms):
                valid = True  # flag
                d = distance(ratom.coords(), atom.coords())
                # default interatomic radius
                # for non-metalics
                if atom_specific_cutoffs:
                    distance_max = self.getBondCutoff(atom, ratom)
                else:
                    distance_max = 1.15 * (atom.rad + ratom.rad)
                if atom.ismetal() or ratom.ismetal():
                    if flag_loose:
                        distance_max = min(3.5, 1.75 * (atom.rad + ratom.rad))
                    elif strict_cutoff:
                        distance_max = 1.2 * (atom.rad + ratom.rad)
                    else:
                        distance_max = 1.37 * (atom.rad + ratom.rad)  # 1.37 by 07/22/2021
                    if debug:
                        print(f'metal in cat {atom.symbol()} and rat {ratom.symbol()}')
                        print(f'maximum bonded distance is {distance_max}')
                    if atom.symbol() == 'He' or ratom.symbol() == 'He':
                        distance_max = 1.6 * (atom.rad + ratom.rad)
                    if d < distance_max and i != ind:
                        # Trim hydrogens.
                        if atom.symbol() == 'H' or ratom.symbol() == 'H':
                            if debug:
                                print('invalid due to hydrogens: ')
                                print(atom.symbol())
                                print(ratom.symbol())
                            valid = False  # Hydrogen catom control
                        if d < distance_max and i != ind and valid:
                            if atom.symbol() in ["C", "S", "N"]:
                                if debug:
                                    print('\n')
                                    print(f'this atom in is {i}')
                                    print(f'this atom sym is {atom.symbol()}')
                                    print(f'this ratom in is {self.getAtom(i).symbol()}')
                                    print(f'this ratom sym is {ratom.symbol()}')
                                # In this case, atom might be intruder C!
                                possible_idxs = self.getBondedAtomsnotH(ind)  # bonded to metal
                                if debug:
                                    print(f'poss inds are {possible_idxs}')
                                if len(possible_idxs) > CN:
                                    metal_prox = sorted(
                                        possible_idxs,
                                        key=lambda x: self.get_pair_distance(x, ind))
                                    allowed_idxs = metal_prox[0:CN]
                                    if debug:
                                        print(f'ind: {ind}')
                                        print(f'metal prox: {metal_prox}')
                                        print(f'trimmed to: {allowed_idxs}')
                                        print(allowed_idxs)
                                        print(f'CN is {CN}')

                                    if i not in allowed_idxs:
                                        valid = False
                                        if debug:
                                            print(f'bond rejected based on atom: {i} not in {allowed_idxs}')
                                    else:
                                        if debug:
                                            print('Ok based on atom')
                            if ratom.symbol() in ["C", "S", "N"]:
                                # In this case, ratom might be intruder C or S
                                possible_idxs = self.getBondedAtomsnotH(i)  # bonded to metal
                                metal_prox = sorted(
                                    possible_idxs, key=lambda x: self.get_pair_distance(x, i))
                                if len(possible_idxs) > CN:
                                    allowed_idxs = metal_prox[0:CN]
                                    if debug:
                                        print(f'ind: {ind}')
                                        print(f'metal prox: {metal_prox}')
                                        print(f'trimmed to {allowed_idxs}')
                                        print(allowed_idxs)
                                    if ind not in allowed_idxs:
                                        valid = False
                                        if debug:
                                            print(f'bond rejected based on ratom {ind} with symbol {ratom.symbol()}')
                                    else:
                                        if debug:
                                            print('ok based on ratom...')
                    else:
                        if debug:
                            print('distance too great')
                if (d < distance_max and i != ind):
                    if valid:
                        if debug:
                            print(f'Valid atom ind {i} ({atom.symbol()}) and {ind} ({ratom.symbol()})')
                            print(f' at distance {d} (which is less than {distance_max})')
                        nats.append(i)
                    else:
                        if debug:
                            print(f'atom ind {i} ({atom.symbol()})')
                            print(f'has been disallowed from bond with {ind} ({ratom.symbol()})')
                            print(f' at distance {d} (which would normally be less than {distance_max})')
                        if d < 2 and not atom.symbol() == 'H' and not ratom.symbol() == 'H':
                            print(
                                'Error, mol3D could not understand connectivity in mol')
        return nats

    def getBondedAtomsSmart(self, idx, oct=False, strict_cutoff=False, catom_list=None):
        """
        Get the atoms bonded with the atom specified with the given index, using the molecular graph.
        Creates graph if it does not exist.

        Parameters
        ----------
            idx : int
                Index of reference atom.
            oct : bool, optional
                Flag for turning on octahedral bonding routines.
            strict_cutoff: bool, optional
                Strict bonding cutoff for fullerene and SACs.
            catom_list: list of int, optional
                List of indices of bonded atoms.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        if not len(self.graph):
            self.createMolecularGraph(oct=oct, strict_cutoff=strict_cutoff, catom_list=catom_list)
        return list(np.nonzero(np.ravel(self.graph[idx]))[0])

    def getBondedAtomsnotH(self, idx, metal_multiplier=1.35, nonmetal_multiplier=1.15):
        """
        Get bonded atom with a given index, but do not count hydrogens.

        Parameters
        ----------
            idx : int
                Index of reference atom.
            metal_multiplier : float, optional
                Multiplier for sum of covalent radii of two elements containing metal.
            nonmetal_multiplier : float, optional
                Multiplier for sum of covalent radii of two elements not containing metal.

        Returns
        -------
            nats : list of int
                List of indices of bonded atoms.
        """

        ratom = self.getAtom(idx)
        # Calculates adjacent number of atoms.
        nats = []
        for i, atom in enumerate(self.atoms):
            if atom.sym == 'H':
                continue
            d = distance(ratom.coords(), atom.coords())
            if atom.ismetal() or ratom.ismetal():
                distance_max = metal_multiplier * (atom.rad + ratom.rad)
            else:
                distance_max = nonmetal_multiplier * (atom.rad + ratom.rad)
            if d < distance_max and i != idx:
                nats.append(i)
        return nats

    def getClosestAtom(self, ratom):
        """
        Get hydrogens bonded to a specific atom3D class.

        Parameters
        ----------
            ratom : atom3D
                Reference atom3D class.

        Returns
        -------
            idx : int
                Index of atom closest to reference atom.
        """

        idx = 0
        cdist = 1000
        for iat, atom in enumerate(self.atoms):
            ds = atom.distance(ratom)
            if (ds < cdist):
                idx = iat
                cdist = ds
        return idx

    def getClosestAtomlist(self, atom_idx, cdist=3.0):
        """
        Get hydrogens bonded to a specific atom3D class.

        Parameters
        ----------
            atom_idx : int
                Reference atom index.
            cdist : float, optional
                Cutoff of neighbor distance in angstroms.

        Returns
        -------
            neighbor_list : list
                List of neighboring atoms.
        """

        neighbor_list = []
        for iat, atom in enumerate(self.atoms):
            ds = atom.distance(self.atoms[atom_idx])
            if (ds < cdist):
                neighbor_list.append(neighbor_list)
        return neighbor_list

    def getClosestAtomnoHs(self, ratom):
        """
        Get atoms bonded to a specific atom3D class that are not hydrogen.

        Parameters
        ----------
            ratom : atom3D
                Reference atom3D class.

        Returns
        -------
            idx : int
                Index of atom closest to reference atom.
        """

        idx = 0
        cdist = 1000
        for iat, atom in enumerate(self.atoms):
            ds = atom.distance(ratom)
            if (ds < cdist) and atom.sym != 'H':
                idx = iat
                cdist = ds
        return idx

    def getFarAtom(self, reference, atomtype=False):
        """
        Get atom furthest from a reference atom.

        Parameters
        ----------
            reference : int
                Index of a reference atom.
            atomtype : bool, optional
                An element name for finding the furthest atom of a given element. Default is False.

        Returns
        -------
            dist : float
                Distance of atom from center of mass in angstroms.
        """

        referenceCoords = self.getAtom(reference).coords()
        dd = 0.00
        farIndex = reference
        for ind, atom in enumerate(self.atoms):
            allow = False
            if atomtype:
                if atom.sym == atomtype:
                    allow = True
                else:
                    allow = False
            else:
                allow = True
            d0 = distance(atom.coords(), referenceCoords)
            if d0 > dd and allow:
                dd = d0
                farIndex = ind
        return farIndex

    def getHs(self):
        """
        Get all hydrogens in a mol3D class instance.

        Returns
        -------
            hlist : list of int
                List of indices of hydrogen atoms.
        """

        hlist = []
        for i in range(self.natoms):
            if self.getAtom(i).sym == 'H':
                hlist.append(i)
        return hlist

    def getHsbyAtom(self, ratom):
        """
        Get hydrogens bonded to a specific atom3D class.

        Parameters
        ----------
            ratom : atom3D
                Reference atom3D class.

        Returns
        -------
            nHs : list of int
                List of indices of hydrogen atoms bound to reference atom3D.
        """

        nHs = []
        for i, atom in enumerate(self.atoms):
            if atom.sym == 'H':
                d = distance(ratom.coords(), atom.coords())
                if (d < 1.2 * (atom.rad + ratom.rad) and d > 0.01):
                    nHs.append(i)
        return nHs

    def getHsbyIndex(self, idx):
        """
        Get all hydrogens bonded to a given atom with an index.

        Parameters
        ----------
            idx : index of reference atom.

        Returns
        -------
            nHs : list of int
                List of indices of hydrogen atoms bound to reference atom.
        """

        nHs = []
        for i, atom in enumerate(self.atoms):
            if atom.sym == 'H':
                d = distance(atom.coords(), self.getAtom(idx).coords())
                if (d < 1.2 * (atom.rad + self.getAtom(idx).rad) and d > 0.01):
                    nHs.append(i)
        return nHs

    def getMLBondLengths(self):
        """
        Outputs the metal-ligand bond lengths in the complex.

        Returns
        -------
            bls : dictionary
                keyed by ID of metal M and valued by dictionary of M-L bond lengths and relative bond lengths
        """

        metals = self.findMetal()  # Get the metals in the complex.
        bls = {}  # Initialize empty dictionary of metal-ligand bond lengths.
        if len(metals) == 0:
            return {}  # We don't have a metal, so there are no M-L bonds.
        for m_id in metals:
            m = self.getAtom(m_id)  # Get the actual metal.
            ligands = self.getBondedAtomsSmart(m_id)  # Gets all atoms/ligands bound to metal.
            ml_bls = []   # Normal bond lengths
            rel_bls = []  # Relative bond lengths
            for l_id in ligands:
                a = self.getAtom(l_id)  # Get the ligand from its ID.
                bl = m.distance(a)      # Normal bond length
                ml_bls.append(bl)
                rel_bls.append(bl / (m.rad + a.rad))  # Append the relative bond length.
            bls[m_id] = {"M-L bond lengths": ml_bls, "relative bond lengths": rel_bls}
        return bls

    def getNumAtoms(self):
        """
        Get the number of atoms within a molecule.

        Returns
        -------
            self.natoms : int
                The number of atoms in the mol3D object.
        """

        return self.natoms

    def getOBMol(self, fst, convtype, ffclean=False, gen3d=True):
        """
        Get OBMol object from a file or SMILES string. If you have a mol3D,
        then use convert2OBMol instead.

        Parameters
        ----------
            fst : str
                Name of input file.
            convtype : str
                Input filetype (xyz,mol,smi).
            ffclean : bool, optional
                Flag for forcefield cleanup of structure. Default is False.
            gen3d: bool, optional
                Flag for 3D structure generation using openbabel.OBBuilder

        Returns
        -------
            OBMol : OBMol
                OBMol class instance to be used with openbabel. Bound as .OBMol attribute.
        """

        obConversion = openbabel.OBConversion()
        OBMol = openbabel.OBMol()
        if convtype == 'smistring':
            obConversion.SetInFormat('smi')
            obConversion.ReadString(OBMol, fst)
        else:
            obConversion.SetInFormat(convtype[:-1])
            obConversion.ReadFile(OBMol, fst)
        if 'smi' in convtype:
            OBMol.AddHydrogens()
            if gen3d:
                b = openbabel.OBBuilder()
                b.Build(OBMol)
        if ffclean:
            forcefield = openbabel.OBForceField.FindForceField('mmff94')
            forcefield.Setup(OBMol)
            forcefield.ConjugateGradients(200)
            forcefield.GetCoordinates(OBMol)
        self.OBMol = OBMol
        return OBMol

    def get_bo_dict_from_inds(self, inds):
        """
        Recreate bo_dict with correct indices.

        Parameters
        ----------
            inds : list
                The indices of the selected submolecule to SAVE.

        Returns
        -------
            new_bo_dict : dict
                The ported over dictionary with new indices (bonds deleted).
        """

        if not self.bo_dict:
            self.convert2OBMol2()
        c_bo_dict = self.bo_dict.copy()
        delete_inds = np.array(
            [x for x in range(self.natoms) if x not in inds])
        for key in list(self.bo_dict.keys()):
            if any([True for x in key if x in delete_inds]):
                del c_bo_dict[key]
        new_bo_dict = dict()
        for key, val in list(c_bo_dict.items()):
            ind1 = key[0]
            ind2 = key[1]
            ind1 = ind1 - len(np.where(delete_inds < ind1)[0])
            ind2 = ind2 - len(np.where(delete_inds < ind2)[0])
            new_bo_dict[(ind1, ind2)] = val
        return new_bo_dict

    def get_coordinate_array(self):
        """
        Get the coordinate array of the molecule.
        Same as coordsvect.

        Parameters
        ----------
            None

        Returns
        -------
            coord_array : np.array
                The coordinates of each atom.
                Shape is (number of atoms, 3).
        """

        num_atoms = self.getNumAtoms()
        coord_array = np.zeros((num_atoms, 3))

        for idx, atom in enumerate(self.getAtoms()):
            coord_array[idx] = atom.coords()

        return coord_array

    def get_element_list(self):
        """
        Get the element list of the molecule.
        Nearly the same as symvect.

        Parameters
        ----------
            None

        Returns
        -------
            element_list : list
                The element symbol of each atom.
        """

        element_list = []
        for idx, atom in enumerate(self.getAtoms()):
            element_list.append(atom.symbol())
        return element_list

    def get_fcs(self, strict_cutoff=False, catom_list=None, max6=True):
        """
        Get first coordination shell of a transition metal complex.

        Parameters
        ----------
            strict_cutoff : bool, optional
                Strict bonding cutoff for fullerene and SACs.
            catom_list : list of int, optional
                List of indices of coordinating atoms.
            max6 : bool, optional
                If True, will return catoms from oct_comp.

        Returns
        -------
            fcs : list
                List of first coordination shell indices.
        """

        metalind = self.findMetal()[0]
        self.get_num_coord_metal(debug=False, strict_cutoff=strict_cutoff, catom_list=catom_list)
        catoms = self.catoms
        if max6 and len(catoms) > 6:
            _, catoms = self.oct_comp(debug=False)
        fcs = [metalind] + catoms
        return fcs

    def get_features(self, lac=True, force_generate=False, eq_sym=False,
                     use_dist=False, NumB=False, Gval=False, size_normalize=False,
                     alleq=False, strict_cutoff=False, catom_list=None, custom_property_dict={},
                     depth=3, loud=False, two_key=False, non_trivial=False):
        """
        Get geo-based RAC features for this transition metal complex (if octahedral).

        Parameters
        ----------
            lac : bool, optional
                Use lac for ligand_assign_consistent behavior. Default is True
            force_generate : bool, optional
                Force the generation of features.
            eq_sym : bool, optional
                Force equatorial plane to have same chemical symbols if possible.
            use_dist : bool, optional
                Whether or not CD-RACs used.
            NumB : bool, optional
                Whether or not the number of bonds RAC features are generated.
            Gval : bool, optional
                Whether or not the group number RAC features are generated.
            size_normalize : bool, optional
                Whether or not to normalize by the number of atoms in molecule.
            alleq : bool, optional
                Whether or not all ligands are equatorial.
            strict_cutoff : bool, optional
                Strict bonding cutoff for fullerene and SACs.
            catom_list : list of int, optional
                List of indices of coordinating atoms.
            custom_property_dict : dict, optional
                Keys are custom property names (str),
                values are dictionaries mapping atom symbols (str, e.g., "H", "He") to
                the numerical property (float) for that atom.
                If provided, other property RACs (e.g., Z, S, T)
                will not be made.
            depth : int, optional
                The maximum depth of the RACs (how many bonds out the RACs go).
                For example, if set to 3, depths considered will be 0, 1, 2, and 3.
            loud : bool
                Whether to generate print statements.
                Default is False.
            two_key : bool
                Whether return dictionary should only have two keys,
                'colnames' and 'results', with values that are
                lists of feature names and values, respectively.
            non_trivial : bool, optional
                Flag to exclude difference RACs of I, and depth zero difference
                RACs. These RACs are always zero. By default False.

        Returns
        -------
            results : dict
                Dictionary of {'RACname':RAC} for all geo-based RACs
        """

        if depth < 0:
            raise Exception('depth must be a non-negative integer.')

        metals = self.findMetal()
        if len(metals) != 1:
            raise Exception('Molecule does not have the expected number of transition metals (1).')

        results = dict()
        from molSimplify.Informatics.lacRACAssemble import get_descriptor_vector
        if not len(self.graph):
            self.createMolecularGraph(strict_cutoff=strict_cutoff, catom_list=catom_list)
        if not force_generate:
            geo_type = self.get_geometry_type()
            if loud:
                print("geotype: ", geo_type)
        if force_generate or geo_type['geometry'] == 'octahedral':
            names, racs = get_descriptor_vector(self, lacRACs=lac, eq_sym=eq_sym, use_dist=use_dist,
                                                NumB=NumB, Gval=Gval, size_normalize=size_normalize,
                                                alleq=alleq, custom_property_dict=custom_property_dict,
                                                depth=depth, non_trivial=non_trivial)
            if two_key:
                results = {
                'colnames': names,
                'results': racs,
                }
            else:
                results = dict(zip(names, racs))
        else:
            print("Warning: Featurization not yet implemented for non-octahedral complexes. Return a empty dict.")
        return results

    def get_first_shell(self, check_hapticity=True):
        '''
        Get the first coordination shell of a mol3D object with a single transition metal (read from CSD mol2 file)
        if check_hapticity is True updates the first shell of multiheptate ligand to be hydrogen set at the geometric mean

        Parameters
        ----------
            check_hapticity: boolean
                Whether to update multiheptate ligands to their geometric centroid.

        Returns
        -------
            mol 3D object: First coordination shell with metal (can change based on check_hapticity).
            list: List of hapticity.
        '''
        from molSimplify.Informatics.graph_analyze import obtain_truncation_metal
        import networkx as nx
        mol_fcs = obtain_truncation_metal(self, hops=1)
        M_coord = mol_fcs.getAtomCoords(mol_fcs.findMetal()[0])
        M_sym = mol_fcs.getAtom(mol_fcs.findMetal()[0]).symbol()
        G = nx.from_numpy_array(mol_fcs.graph)
        G.remove_node(mol_fcs.findMetal()[0])
        coord_list = [c for c in sorted(nx.connected_components(G), key=len, reverse=True)]
        hapticity_list = [len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
        new_coords_mol = []
        new_coords_sym = []
        if len(coord_list) == G.number_of_nodes():
            new_mol = mol3D()
            new_mol.copymol3D(mol_fcs)
        else:
            for i in range(len(coord_list)):
                if len(coord_list[i]) == 1:
                    coord_index = list(coord_list[i])[0]
                    coord = mol_fcs.getAtomCoords(coord_index)
                    sym = mol_fcs.getAtom(coord_index).symbol()
                    new_coords_mol.append(coord)
                    new_coords_sym.append(sym)
                else:
                    get_centroid = []
                    for j in coord_list[i]:
                        get_centroid.append(mol_fcs.getAtomCoords(j))
                    coordinating = np.array(get_centroid)
                    coord = np.mean(coordinating, axis=0)
                    new_coords_mol.append(coord.tolist())
                    new_coords_sym.append('H')
            new_mol = mol3D()
            new_mol.bo_dict = {}
            new_mol.addAtom(atom3D(M_sym, M_coord))
            for i in range(len(new_coords_mol)):
                new_mol.addAtom(atom3D(new_coords_sym[i], new_coords_mol[i]))
            new_mol.graph = np.zeros([new_mol.natoms, new_mol.natoms])
            for i in range(new_mol.natoms):
                if i != new_mol.findMetal()[0]:
                    new_mol.add_bond(new_mol.findMetal()[0], i, 1)

        if check_hapticity:
            return new_mol, hapticity_list
        else:
            return mol_fcs, hapticity_list

    def get_geometry_type(self, dict_check=False, angle_ref=False,
                          flag_catoms=False, catoms_arr=None, debug=False,
                          skip=False):
        """
        Get the type of the geometry (linear(2), trigonal planar(3), tetrahedral(4), square planar(4),
        trigonal bipyramidal(5), square pyramidal(5, one-empty-site),
        octahedral(6), pentagonal bipyramidal(7)).

        Uses hapticity truncated first coordination shell.

        Parameters
        ----------
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            flag_catoms : bool, optional
                Whether or not to return the catoms arr. Default as False.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            debug : bool, optional
                Flag for extra printout. Default is False.
            skip : list, optional
                Geometry checks to skip. Default is False.

        Returns
        -------
            results : dictionary
                Measurement of deviations from arrays.
        """

        first_shell, hapt = self.get_first_shell()
        num_coord = first_shell.natoms - 1
        all_geometries = globalvars().get_all_geometries()
        all_angle_refs = globalvars().get_all_angle_refs()
        summary = {}

        if len(first_shell.graph):  # Find num_coord based on metal_cn if graph is assigned.
            if len(first_shell.findMetal()) > 1:
                raise ValueError('Multimetal complexes are not yet handled.')
            elif len(first_shell.findMetal()) == 1:
                num_coord = len(first_shell.getBondedAtomsSmart(first_shell.findMetal()[0]))
            else:
                raise ValueError('No metal centers exist in this complex.')

        if catoms_arr is not None and len(catoms_arr) != num_coord:
            raise ValueError("num_coord and the length of catoms_arr do not match.")

        if num_coord not in [2, 3, 4, 5, 6, 7]:
            results = {
                "geometry": "unknown",
                "angle_devi": False,
                "summary": {},
                "hapticity": hapt,
            }
            return results
        elif num_coord == 2:
            if first_shell.findMetal()[0] == 2:
                angle = first_shell.getAngle(0, 2, 1)
            elif first_shell.findMetal()[0] == 1:
                angle = first_shell.getAngle(0, 1, 2)
            else:
                angle = first_shell.getAngle(1, 0, 2)
            results = {
                "geometry": "linear",
                "angle_devi": 180 - angle,
                "summary": {},
                "hapticity": hapt,
            }
            return results

        possible_geometries = all_geometries[num_coord]
        for geotype in possible_geometries:
            dict_catoms_shape, catoms_assigned = first_shell.oct_comp(
                angle_ref=all_angle_refs[geotype], catoms_arr=None, debug=debug)
            if debug:
                print("Geocheck assigned catoms: ", catoms_assigned,
                      [first_shell.getAtom(ind).symbol() for ind in catoms_assigned])
            summary.update({geotype: dict_catoms_shape})

        angle_devi, geometry = 10000, None
        for geotype in summary:
            if summary[geotype]["oct_angle_devi_max"] < angle_devi:
                angle_devi = summary[geotype]["oct_angle_devi_max"]
                geometry = geotype
        results = {
            "geometry": geometry,
            "angle_devi": angle_devi,
            "summary": summary,
            "hapticity": hapt,
        }
        return results

    def get_geometry_type_distance(
            self, max_dev=1e6, close_dev=1e-2,
            flag_catoms=False, catoms_arr=None,
            skip=False, transition_metals_only=False,
            cshm=False) -> Dict[str, Any]:
        """
        Get the type of the geometry (available options in globalvars all_geometries).

        Uses hapticity truncated first coordination shell.
        Does not require the input of num_coord.

        Parameters
        ----------
            max_dev : float, optional
                Maximum RMSD allowed between a structure and an ideal geometry before it is classified as unknown. Default is 1e6.
            close_dev : float, optional
                Maximum difference in RMSD between two classifications allowed before they are compared by maximum single-atom deviation as well.
            flag_catoms : bool, optional
                Whether or not to return the catoms arr. Default as False.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            skip : list, optional
                Geometry checks to skip. Default is False.
            transition_metals_only : bool, optional
                Flag if only transition metals counted as metals. Default is False.
            cshm: bool, optional
                Whether or not to return continuous shape measures for each geometry.

        Returns
        -------
            results : dictionary
                Contains the classified geometry and the RMSD from an ideal structure.
                Summary contains a list of the RMSD, the maximum single-atom deviation,
                and a continuous shape measure for all considered geometry types.
        """

        first_shell, hapt = self.get_first_shell()
        num_coord = first_shell.natoms - 1
        all_geometries = globalvars().get_all_geometries()
        all_polyhedra = globalvars().get_all_polyhedra()
        summary = {}

        if len(first_shell.graph):  # Find num_coord based on metal_cn if graph is assigned.
            if len(first_shell.findMetal()) > 1:
                raise ValueError('Multimetal complexes are not yet handled.')
            elif len(first_shell.findMetal(transition_metals_only=transition_metals_only)) == 1:
                # Use oct=False to ensure coordination number based on radius cutoffs only
                num_coord = len(first_shell.getBondedAtomsSmart(first_shell.findMetal(transition_metals_only=transition_metals_only)[0], oct=False))
            else:
                raise ValueError('No metal centers exist in this complex.')
        if catoms_arr is not None and len(catoms_arr) != num_coord:
            raise ValueError("num_coord and the length of catoms_arr do not match.")

        if num_coord not in list(all_geometries.keys()):
            # Should we indicate somehow that these are unknown due to a different coordination number?
            results = {
                "geometry": "unknown",
                "rmsd": np.NAN,
                "summary": {},
                "hapticity": hapt,
                "close_rmsds": False
            }
            return results

        possible_geometries = all_geometries[num_coord]

        # for each same-coordinated geometry, get the minimum RMSD and the maximum single-atom deviation in that pairing
        for geotype in possible_geometries:
            rmsd_calc, max_dist = self.dev_from_ideal_geometry(all_polyhedra[geotype])
            if cshm:
                cshm = self.continuous_shape_measure(all_polyhedra[geotype])
                summary.update({geotype: {'rmsd': rmsd_calc, 'max_single_atom_deviation': max_dist, 'continuous_shape_measure': cshm}})
            else:
                summary.update({geotype: {'rmsd': rmsd_calc, 'max_single_atom_deviation': max_dist}})

        close_rmsds = False
        current_rmsd, geometry = max_dev, "unknown"
        for geotype in summary:
            # if the RMSD for this structure is the lowest seen so far (within a threshold)
            if summary[geotype]['rmsd'] < (current_rmsd + close_dev):
                # if the RMSDs are close, flag this in the summary and classify on second criterion
                if np.abs(summary[geotype]['rmsd'] - current_rmsd) < close_dev:
                    close_rmsds = True
                    if summary[geotype]['max_single_atom_deviation'] < summary[geometry]['max_single_atom_deviation']:
                        # classify based on largest singular deviation
                        current_rmsd = summary[geotype]['rmsd']
                        geometry = geotype
                else:
                    current_rmsd = summary[geotype]['rmsd']
                    geometry = geotype

        results = {
            "geometry": geometry,
            "rmsd": current_rmsd,
            "summary": summary,
            "hapticity": hapt,
            "close_rmsds": close_rmsds
        }
        return results

    def get_geometry_type_old(self, dict_check=False, angle_ref=False, num_coord=None,
                          flag_catoms=False, catoms_arr=None, debug=False,
                          skip=False, transition_metals_only=False, num_recursions=[0, 0]):
        """
        Get the type of the geometry (trigonal planar(3), tetrahedral(4), square planar(4),
        trigonal bipyramidal(5), square pyramidal(5, one-empty-site),
        octahedral(6), pentagonal bipyramidal(7)).

        Parameters
        ----------
            dict_check : dict, optional
                The cutoffs of each geo_check metrics we have. Default is False
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            num_coord : int, optional
                Expected coordination number.
            flag_catoms : bool, optional
                Whether or not to return the catoms arr. Default as False.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            debug : bool, optional
                Flag for extra printout. Default is False.
            skip : list, optional
                Geometry checks to skip. Default is False.
            transition_metals_only : bool, optional
                Flag if only transition metals counted as metals. Default is False.
            num_recursions : list, optional
                Counter to track number of ligands classified as 'sandwich' and 'edge' in original structure.

        Returns
        -------
            results : dictionary
                Measurement of deviations from arrays.
        """

        all_geometries = globalvars().get_all_geometries()
        all_angle_refs = globalvars().get_all_angle_refs()
        summary = {}

        if len(self.graph):  # Find num_coord based on metal_cn if graph is assigned
            if len(self.findMetal()) > 1:
                raise ValueError('Multimetal complexes are not yet handled.')
            elif len(self.findMetal(transition_metals_only=transition_metals_only)) == 1:
                num_coord = len(self.getBondedAtomsSmart(self.findMetal(transition_metals_only=transition_metals_only)[0]))
            else:
                raise ValueError('No metal centers exist in this complex.')

        if num_coord is None:
            # TODO: Implement the case where we don't know the coordination number.
            raise NotImplementedError(
                "Not implemented yet. Please at least provide the coordination number.")

        if catoms_arr is not None and len(catoms_arr) != num_coord:
            raise ValueError("num_coord and the length of catoms_arr do not match.")

        num_sandwich_lig, info_sandwich_lig, aromatic, allconnect, sandwich_lig_atoms = self.is_sandwich_compound(transition_metals_only=transition_metals_only)
        num_edge_lig, info_edge_lig, edge_lig_atoms = self.is_edge_compound(transition_metals_only=transition_metals_only)

        if num_sandwich_lig:
            mol_copy = mol3D()
            mol_copy.copymol3D(mol0=self)
            catoms = mol_copy.getBondedAtoms(idx=self.findMetal()[0])
            centroid_coords = []
            sandwich_lig_catom_idxs = []
            for idx in range(num_sandwich_lig):
                sandwich_lig_catoms = np.array(list(sandwich_lig_atoms[idx]['atom_idxs']))-1
                sandwich_lig_catom_idxs.extend([catoms[i] for i in sandwich_lig_catoms])
                atom_coords = np.array([mol_copy.getAtomCoords(idx=atom_idx) for atom_idx in [catoms[i] for i in sandwich_lig_catoms]])
                centroid_coords.append([np.mean(atom_coords[:, 0]), np.mean(atom_coords[:, 1]), np.mean(atom_coords[:, 2])])
            mol_copy.deleteatoms(sandwich_lig_catom_idxs)
            for idx in range(num_sandwich_lig):
                atom = atom3D()
                atom.setcoords(xyz=centroid_coords[idx])
                mol_copy.addAtom(atom)
                mol_copy.add_bond(idx1=mol_copy.findMetal()[0], idx2=mol_copy.natoms-1, bond_type=1)
            return mol_copy.get_geometry_type_old(num_recursions=[num_sandwich_lig, num_edge_lig])

        if num_edge_lig:
            mol_copy = mol3D()
            mol_copy.copymol3D(mol0=self)
            catoms = mol_copy.getBondedAtoms(idx=self.findMetal()[0])
            centroid_coords = []
            edge_lig_catom_idxs = []
            for idx in range(num_edge_lig):
                edge_lig_catoms = np.array(list(edge_lig_atoms[idx]['atom_idxs']))-1
                edge_lig_catom_idxs.extend([catoms[i] for i in edge_lig_catoms])
                atom_coords = np.array([mol_copy.getAtomCoords(idx=atom_idx) for atom_idx in [catoms[i] for i in edge_lig_catoms]])
                centroid_coords.append([np.mean(atom_coords[:, 0]), np.mean(atom_coords[:, 1]), np.mean(atom_coords[:, 2])])
            mol_copy.deleteatoms(edge_lig_catom_idxs)
            for idx in range(num_edge_lig):
                atom = atom3D()
                atom.setcoords(xyz=centroid_coords[idx])
                mol_copy.addAtom(atom)
                mol_copy.add_bond(idx1=mol_copy.findMetal()[0], idx2=mol_copy.natoms-1, bond_type=1)
            return mol_copy.get_geometry_type_old(num_recursions=[num_sandwich_lig, num_edge_lig])

        if num_coord not in all_geometries:
            geometry = "unknown"
            results = {
                "geometry": geometry,
                "angle_devi": False,
                "summary": {},
                "num_sandwich_lig": num_recursions[0],
                "aromatic": aromatic,
                "allconnect": allconnect,
                "num_edge_lig": num_recursions[1]
            }
            return results

        possible_geometries = all_geometries[num_coord]
        for geotype in possible_geometries:
            dict_catoms_shape, catoms_assigned = self.oct_comp(angle_ref=all_angle_refs[geotype],
                                                               catoms_arr=None,
                                                               debug=debug)
            if debug:
                print("Geocheck assigned catoms: ", catoms_assigned,
                      [self.getAtom(ind).symbol() for ind in catoms_assigned])
            summary.update({geotype: dict_catoms_shape})

        angle_devi, geometry = 10000, None
        for geotype in summary:
            if summary[geotype]["oct_angle_devi_max"] < angle_devi:
                angle_devi = summary[geotype]["oct_angle_devi_max"]
                geometry = geotype
        results = {
            "geometry": geometry,
            "angle_devi": angle_devi,
            "summary": summary,
            "num_sandwich_lig": num_recursions[0],
            "info_sandwich_lig": info_sandwich_lig,
            "aromatic": aromatic,
            "allconnect": allconnect,
            "num_edge_lig": num_recursions[1],
            "info_edge_lig": info_edge_lig,
        }
        return results

    def get_graph(self):
        """
        Return the graph attribute of the molecule.
        It is faster to just use mol.graph though,
        where mol is the mol3D object.

        Parameters
        ----------
            None

        Returns
        -------
            self.graph : np.array
                The graph.

        """

        return self.graph

    def get_graph_hash(self, attributed_flag=True, oct=False, loud=True):
        """
        Calculate the graph hash of a molecule.
        Note: Not useful for distinguishing betweeen molecules
        that are just a single atom.

        Parameters
        ----------
            attributed_flag : bool
                Whether the graph hash takes into account element symbols.
                Default is True.
            oct : bool
                Defines whether a structure is octahedral.
                Default is False.
            loud : bool
                Whether to generate print statements.
                Default is True.

        Returns
        -------
            gh : str
                The graph hash.
        """

        if not len(self.graph):
            if loud:
                print('graph attribute not set. Setting it.')
            self.createMolecularGraph(oct=oct)

        G = nx.Graph()
        attributed = []
        for i, row in enumerate(self.graph):
            for j, column in enumerate(row):
                if self.graph[i][j] == 1:
                    temp_label = [self.getAtom(i).symbol(), self.getAtom(j).symbol()]
                    temp_label.sort()
                    temp_label = ''.join(temp_label)
                    attributed.append((i, j, {'label': temp_label}))
        G.add_edges_from(attributed)

        if attributed_flag:
            gh = nx.weisfeiler_lehman_graph_hash(G, edge_attr="label")
        else:
            gh = nx.weisfeiler_lehman_graph_hash(G)

        return gh

    def get_linear_angle(self, ind):
        """
        Get linear ligand angle.

        Parameters
        ----------
            ind : int
                Index for one of the metal-coordinating atoms.

        Returns
        -------
            flag : bool
                True if the ligand is linear.
            ang : float
                Get angle of linear ligand. 0 if not linear.
        """

        flag, catoms = self.is_linear_ligand(ind)
        if flag:
            vec1 = np.array(self.getAtomCoords(
                catoms[0])) - np.array(self.getAtomCoords(ind))
            vec2 = np.array(self.getAtomCoords(
                catoms[1])) - np.array(self.getAtomCoords(ind))
            ang = vecangle(vec1, vec2)
        else:
            ang = 0
        return flag, ang

    def get_mol_graph_det(self, oct=True, use_bo_mat=False):
        """
        Get molecular graph determinant.

        Parameters
        ----------
            oct : bool, optional
                Flag for whether the geometry is octahedral. Default is True.
            use_bo_mat : bool, optional
                Use bond order matrix in determinant computation.

        Returns
        -------
            safedet : str
                String containing the molecular graph determinant.
        """

        globs = globalvars()
        amassdict = globs.amass()
        if not len(self.graph):
            self.createMolecularGraph(oct=oct)
        if use_bo_mat:
            if self.bo_mat.size == 0 and len(self.bo_dict) == 0:
                raise AssertionError('This mol does not have BO information.')
            elif isinstance(self.bo_dict, dict):
                # bo_dict will be prioritized over bo_mat
                tmpgraph = np.copy(self.graph)
                for key_val, value in list(self.bo_dict.items()):
                    if str(value).lower() == 'ar':
                        value = 1.5
                    elif str(value).lower() == 'am':
                        value = 1.5
                    elif str(value).lower() == 'un':
                        value = 4
                    else:
                        value = int(value)
                    # This assigns the bond order in the BO dict
                    # to the graph, then the determinant can be taken
                    # for that graph.
                    tmpgraph[key_val[0], key_val[1]] = value
                    tmpgraph[key_val[1], key_val[0]] = value
            else:
                tmpgraph = np.copy(self.bo_mat)
        else:
            tmpgraph = np.copy(self.graph)
        syms = self.symvect()
        weights = [amassdict[x][0] for x in syms]
        # Add hydrogen tolerance?
        inds = np.nonzero(tmpgraph)
        for j in range(len(syms)):
            tmpgraph[j, j] = weights[j]
        for i, x in enumerate(inds[0]):
            y = inds[1][i]
            tmpgraph[x, y] = weights[x]*weights[y]*tmpgraph[x, y]
        with np.errstate(over='raise'):
            try:
                det = np.linalg.det(tmpgraph)
            except (np.linalg.LinAlgError, FloatingPointError):
                (sign, det) = np.linalg.slogdet(tmpgraph)
                if sign != 0:
                    det = sign*det
        if 'e+' in str(det):
            safedet = str(det).split(
                'e+')[0][0:12]+'e+'+str(det).split('e+')[1]
        else:
            safedet = str(det)[0:12]
        return safedet

    def get_molecular_mass(self):
        """
        Computes the molecular mass, or weight, of a mol3D.

        Parameters
        ----------
            None

        Returns
        -------
            mol_mass : float
                The molecular mass. Units of amu.
        """

        globs = globalvars()
        amassdict = globs.amass()

        mol_mass = 0
        for i in self.atoms:
            mol_mass += amassdict[i.symbol()][0] # atomic mass

        # Adjusting the mass attribute if it is incorrect.
        if self.mass != mol_mass:
            self.mass = mol_mass

        return mol_mass

    def get_num_coord_metal(self, debug=False, strict_cutoff=False, catom_list=None):
        """
        Get metal coordination based on get bonded atoms. Store this info.

        Parameters
        ----------
            debug : bool, optional
                Flag for whether extra output should be printed. Default is False.
            strict_cutoff : bool, optional
                Strict bonding cutoff for fullerene and SACs.
            catom_list : list of int, optional
                List of indices of coordinating atoms.
        """

        metal_list = self.findMetal()
        metal_ind = self.findMetal()[0]
        metal_coord = self.getAtomCoords(metal_ind)
        if len(self.graph):
            catoms = self.getBondedAtomsSmart(metal_ind)
        elif catom_list is not None:
            catoms = catom_list
        elif len(metal_list) > 0:
            _catoms = self.getBondedAtomsOct(ind=metal_ind, strict_cutoff=strict_cutoff)
            if debug:
                print("_catoms: ", _catoms)
            dist2metal = {}
            dist2catoms = {}
            for ind in _catoms:
                tmpd = {}
                coord = self.getAtom(ind).coords()
                dist = np.linalg.norm(np.array(coord) - np.array(metal_coord))
                dist2metal.update({ind: dist})
                for _ind in _catoms:
                    _coord = self.getAtom(_ind).coords()
                    dist = np.linalg.norm(np.array(coord) - np.array(_coord))
                    tmpd.update({_ind: dist})
                dist2catoms.update({ind: tmpd})
            _catoms_set = set()
            for ind in _catoms:
                tmp = {}
                distind = np.linalg.norm(
                    np.array(self.getAtom(ind).coords()) - np.array(metal_coord))
                tmp.update({ind: distind})
                for _ind in _catoms:
                    if dist2catoms[ind][_ind] < 1.3:
                        tmp.update({_ind: dist2metal[_ind]})
                _catoms_set.add(min(list(tmp.items()), key=lambda x: x[1])[0])
            _catoms = list(_catoms_set)
            min_bond_dist = 2.0
            if len(dist2metal) > 0:
                dists = np.array(list(dist2metal.values()))
                inds = np.where(dists > min_bond_dist)[0]
                if inds.shape[0] > 0:
                    min_bond_dist = min(dists[inds])
            max_bond_dist = min_bond_dist + 1.5  # This is an adjustable param.
            catoms = []
            for ind in _catoms:
                if dist2metal[ind] <= max_bond_dist:
                    catoms.append(ind)
        else:
            metal_ind = []
            metal_coord = []
            catoms = []
        if debug:
            print(('metal coordinate:', metal_coord,
                   self.getAtom(metal_ind).symbol()))
            print(('coordinations: ', catoms, len(catoms)))
        self.catoms = catoms
        self.num_coord_metal = len(catoms)
        if debug:
            print(("self.catoms: ", self.catoms))
            print(("self.num_coord_metal: ", self.num_coord_metal))

    def get_octetrule_charge(self, debug=False):
        '''
        Get the octet-rule charge provided a mol3D object with bo_graph (read from CSD mol2 file).
        Note that currently this function should only be applied to ligands (organic molecules).

        Parameters
        ----------
            debug: boolean
                Whether to have more printouts.

        Returns
        -------
            charge : float
                The overall charge of the molecule.
            arom_charge : int
                The charge of the aromatic rings.
        '''

        octet_bo = {"H": 1, "C": 4, "N": 3, "O": 2, "F": 1,
                    "Si": 4, "P": 3, "S": 2, "Cl": 1,
                    "Ge": 4, "As": 3, "Se": 2, "Br": 1,
                    "Sn": 4, "Sb": 3, "Te": 2, "I": 1}
        self.deleteatoms(self.findAtomsbySymbol("X"))
        self.convert2OBMol2()
        ringlist = self.OBMol.GetSSSR()
        ringinds = []
        charge = 0
        for obmol_ring in ringlist:
            _inds = []
            for ii in range(1, self.natoms+1):
                if obmol_ring.IsInRing(ii):
                    _inds.append(ii-1)
            ringinds.append(_inds)
            charge += self.aromatic_charge(self.bo_mat[_inds, :][:, _inds])
        arom_charge = charge
        for ii in range(self.natoms):
            sym = self.getAtom(ii).symbol()
            try:
                if sym in ["N", "P", "As", "Sb"] and np.sum(self.bo_mat[ii]) >= 5:
                    _c = int(np.sum(self.bo_mat[ii]) - 5)
                elif (sym in ["N", "P", "As", "Sb"]) and (np.count_nonzero(self.bo_mat[ii] == 2) >= 1) and \
                     ("O" in [self.getAtom(x).symbol() for x in np.where(self.bo_mat[ii] == 2)[0]]) and \
                     (np.sum(self.bo_mat[ii]) == 4):
                    _c = int(np.sum(self.bo_mat[ii]) - 5)
                # Double Bonds == 3, Double bonded atom is O or N, Total BO == 6
                elif sym in ["O", "S", "Se", "Te"] and np.count_nonzero(self.bo_mat[ii] == 2) == 3 and \
                        (self.getAtom(np.where(self.bo_mat[ii] == 2)[0][0]).symbol() in ["O", "N"]) and \
                        np.sum(self.bo_mat[ii]) == 6:
                    _c = -int(np.sum(self.bo_mat[ii]) - 4)
                elif sym in ["O", "S", "Se", "Te"] and np.sum(self.bo_mat[ii]) >= 5:
                    _c = -int(np.sum(self.bo_mat[ii]) - 6)
                elif sym in ["O", "S", "Se", "Te"] and np.sum(self.bo_mat[ii]) == 4:
                    _c = int(np.sum(self.bo_mat[ii]) - 4)
                elif sym in ["F", "Cl", "Br", "I"] and np.sum(self.bo_mat[ii]) >= 6:
                    _c = int(np.sum(self.bo_mat[ii]) - 7)
                elif sym in ["H"] and np.sum(self.bo_mat[ii]) == 2:
                    _c = 0
                else:
                    _c = int(np.sum(self.bo_mat[ii]) - octet_bo[sym])
                if debug:
                    print(ii, sym, _c)
                charge += _c
            except ValueError:
                return np.nan, np.nan
        return charge, arom_charge

    def get_pair_distance(self, idx1, idx2):
        """
        Get distance between two atoms in a molecule.

        Parameters
        ----------
            idx : int
                Index of reference atom.
            idx2 : int
                Index of the second atom.

        Returns
        -------
            d : float
                Distance between atoms in angstroms.
        """

        d = self.getAtom(idx1).distance(self.getAtom(idx2))
        return d

    def get_smiles(self, canonicalize=False, use_mol2=False) -> str:
        """
        Returns the SMILES string representing the mol3D object.

        Parameters
        ----------
            canonicalize : bool, optional
                Openbabel canonicalization of smiles. Default is False.
            use_mol2 : bool, optional
                Use graph in mol2 instead of interpreting it. Default is False.

        Returns
        -------
            smiles : str
                SMILES from a mol3D object. Watch out for charges.
        """

        # Used to get the SMILES string of a given mol3D object.
        conv = openbabel.OBConversion()
        conv.SetOutFormat('smi')
        if canonicalize:
            conv.SetOutFormat('can')
        if not self.OBMol:
            if use_mol2:
                # Produces a smiles with the enforced BO matrix,
                # which is needed for correct behavior for fingerprints.
                self.convert2OBMol2(ignoreX=True)
            else:
                self.convert2OBMol()
        smi = conv.WriteString(self.OBMol).split()[0]
        return smi

    def get_smilesOBmol_charge(self):
        """
        Get the charge of a mol3D object through adjusted OBmol hydrogen/smiles conversion.
        Note that currently this function should only be applied to ligands (organic molecules).
        """

        # Use this as dummy mol3D class. Shouldn't interfere with other functionality.
        self.my_mol_trunc = mol3D()
        nh = len([x for x in self.symvect() if x == 'H'])  # Get initial hydrogens count.
        smi = self.get_smiles(use_mol2=True, canonicalize=True)
        self.my_mol_trunc.read_smiles(smi, steps=0, ff=False)
        charge = self.my_mol_trunc.OBMol.GetTotalCharge()
        formula = self.my_mol_trunc.OBMol.GetFormula()
        if 'H' in formula:
            hs_tmp = formula.split('H')[1]
            nh_obmol = ''
            if len(hs_tmp) > 0:
                if hs_tmp[0].isnumeric():
                    for x in hs_tmp:
                        if x.isnumeric():
                            nh_obmol += x
                        else:
                            break
                else:
                    nh_obmol += '1'
            else:
                nh_obmol += '1'
        else:
            nh_obmol = '0'
        nh_obmol = int(nh_obmol)
        charge = charge - nh_obmol + nh
        return charge

    def get_submol_noHs(self):
        """
        Get the heavy atom only submolecule, with no hydrogens.

        Returns
        -------
            mol_noHs : mol3D
                mol3D class instance with no hydrogens.
        """

        keep_list = []
        for i in range(self.natoms):
            if self.getAtom(i).symbol() == 'H':
                continue
            else:
                keep_list.append(i)
        mol_noHs = self.create_mol_with_inds(keep_list)
        return mol_noHs

    def get_symmetry(self, verbose=True, max_allowed_dev=30, details=False):
        """
        Classify octahedral transition metal complexes (TMCs) according to symmetry.

        Parameters
        ----------
            verbose: bool
                Flag for returning warning when TMC exhibits high deviation from closest symmetry.
                Default=True
            max_allowed_dev: float
                Maximum allowed deviation before warning is triggered (degrees).
                Default=30
            details: bool
                Flag for returning detailed lists of unique ligands and coordinating atoms, intended for use with flip_symmetry().
                Default=False

        Returns
        -------
            symmetry_dict: dict
                Dictionary storing assigned symmetry class and deviations from all possible symmetry classes.
            detailed_dict: dict
                Dictionary storing indices of metal, ligand atoms, and ligand coordinating atoms, only returned if details=True
        """

        from molSimplify.Classes.ligand import ligand_breakdown
        from molSimplify.Classes.mol2D import Mol2D
        metal_idx = self.findMetal()
        if len(metal_idx) != 1:
            raise ValueError('Function only supported for mononuclear TMCs.')

        metal_idx = metal_idx[0]
        tmc_atoms = [i for i in range(self.natoms)]
        lig_list, lig_dents, lig_catoms = ligand_breakdown(self)

        geometry_type = self.get_geometry_type_distance()['geometry']
        if geometry_type != 'octahedral':
            raise ValueError(f'Function only supported for octahedral TMCs. Detected geometry is {geometry_type}.')

        # Get graph hash of each ligand to identify number of unique ligands.
        ligand_hashes = []
        ligand_dict = {}
        for idx, ligand in enumerate(lig_list):
            ligand_mol = mol3D()
            ligand_mol.copymol3D(self)
            ligand_mol.deleteatoms(Alist=[i for i in tmc_atoms if i not in ligand])
            ligand_hash = Mol2D().from_mol3d(mol3d=ligand_mol).graph_hash()
            ligand_hashes.append(ligand_hash)
            if ligand_hash not in ligand_dict:
                ligand_dict[ligand_hash] = lig_dents[idx]
            else:
                ligand_dict[ligand_hash] += lig_dents[idx]
        # Determine number of unique ligands, sorted in ascending order.
        # Sort is stable, so in the case of ties, original order is preserved.
        ligand_dict = dict(sorted(Counter(ligand_dict).items(), key=lambda x: x[1]))
        if len(ligand_dict) > 3:
            raise ValueError('Function only supported for TMCs with up to 3 unique ligands.')

        # One unique ligand: assign as homoleptic.
        if len(ligand_dict) == 1:
            unique_ligand_ratios = 1
            lig1_atoms = lig_list
            lig1_catoms = lig_catoms
            lig2_atoms = None
            lig2_catoms = None
            lig3_atoms = None
            lig3_catoms = None
            symmetry = 'homoleptic'
            symmetry_dict = {'symmetry': symmetry}

        # Two unique ligands: consider cis, trans, fac, mer, and monoheteroleptic symmetry groups.
        elif len(ligand_dict) == 2:
            # Calculate ratio between ligands.
            unique_ligand_ratios = list(ligand_dict.values())[1] / list(ligand_dict.values())[0]
            lig2_indices = [index for index, value in enumerate(ligand_hashes) if value == list(ligand_dict.keys())[0]]
            lig2_atoms = [lig_list[idx] for idx in lig2_indices]
            lig2_catoms = np.concatenate([lig_catoms[idx] for idx in lig2_indices])

            lig1_indices = [index for index, value in enumerate(ligand_hashes) if value == list(ligand_dict.keys())[1]]
            lig1_atoms = [lig_list[idx] for idx in lig1_indices]
            lig1_catoms = np.concatenate([lig_catoms[idx] for idx in lig1_indices])

            lig3_atoms = None
            lig3_catoms = None

            # Check for monoheteroleptics, only possible for TMCs with all monodentate or 1 monodentate 1 pentadentate.
            if unique_ligand_ratios == 5:
                symmetry = 'monoheteroleptic'
                symmetry_dict = {'symmetry': symmetry}

            elif unique_ligand_ratios == 2:
                # Find angle between coordinating atoms of less represented (i.e., minority) ligand and metal.
                lig2_angle = self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1])
                # Classify complex as cis or trans based on deviation from ideal angle.
                cis_dev = np.abs(lig2_angle - 90)
                trans_dev = np.abs(lig2_angle - 180)
                if cis_dev < trans_dev:
                    symmetry = 'cis'
                else:
                    symmetry = 'trans'
                if verbose and min(cis_dev, trans_dev) > max_allowed_dev:
                    print('Warning: high deviation from ideal symmetry, manual inspection recommended')
                symmetry_dict = {'symmetry': symmetry, 'cis_dev': cis_dev, 'trans_dev': trans_dev}

            elif unique_ligand_ratios == 1:
                # Find angle between coordinating atoms of first ligand and metal.
                lig2_angles = np.array((self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                                        self.getAngle(idx0=lig2_catoms[1], idx1=metal_idx, idx2=lig2_catoms[2]),
                                        self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[2])))
                lig2_angles.sort()
                # Classify complex as fac or mer based on deviation from ideal angle.
                fac_dev_avg = np.average(np.abs(lig2_angles - 90))
                mer_dev_avg = np.average(np.abs(
                    np.concatenate((np.array(lig2_angles)[0:2] - 90, np.array([np.array(lig2_angles)[2] - 180])))))
                if fac_dev_avg < mer_dev_avg:
                    symmetry = 'fac'
                else:
                    symmetry = 'mer'
                if verbose and min(fac_dev_avg, mer_dev_avg) > max_allowed_dev:
                    print('Warning: high deviation from ideal symmetry, manual inspection recommended')
                symmetry_dict = {'symmetry': symmetry, 'fac_dev': fac_dev_avg, 'mer_dev': mer_dev_avg}

        # Three unique ligands: consider cis asymmetric (CA), double cis symmetric (DCS), trans asymmetric (TA),
        # double trans symmetric (DTS), equatorial asymmetric (EA), fac asymmetric (FA), mer asymmetric trans (MAT),
        # and mer asymmetric cis (MAC) symmetry groups.
        elif len(ligand_dict) == 3:
            # Calculate ratio between ligands sorted in ascending order (L1 = ligand_dict[2] = most abundant).
            # Ratios stored as follows: L1:L2, L2:L3, L1:L3
            unique_ligand_ratios = [list(ligand_dict.values())[2] / list(ligand_dict.values())[1],
                                    list(ligand_dict.values())[1] / list(ligand_dict.values())[0],
                                    list(ligand_dict.values())[2] / list(ligand_dict.values())[0]]

            lig1_indices = [index for index, value in enumerate(ligand_hashes) if value == list(ligand_dict.keys())[2]]
            lig1_atoms = [lig_list[idx] for idx in lig1_indices]
            lig1_catoms = np.concatenate([lig_catoms[idx] for idx in lig1_indices])

            lig2_indices = [index for index, value in enumerate(ligand_hashes) if value == list(ligand_dict.keys())[1]]
            lig2_atoms = [lig_list[idx] for idx in lig2_indices]
            lig2_catoms = np.concatenate([lig_catoms[idx] for idx in lig2_indices])

            lig3_indices = [index for index, value in enumerate(ligand_hashes) if value == list(ligand_dict.keys())[0]]
            lig3_atoms = [lig_list[idx] for idx in lig3_indices]
            lig3_catoms = np.concatenate([lig_catoms[idx] for idx in lig3_indices])

            if unique_ligand_ratios == [4, 1, 4]:
                # Find angle between coordinating atoms of less represented (i.e., minority) ligand and metal.
                lig23_angle = self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig3_catoms[0])
                # Classify complex as CA or TA based on deviation from ideal angle.
                CA_dev = np.abs(lig23_angle - 90)
                TA_dev = np.abs(lig23_angle - 180)
                if CA_dev < TA_dev:
                    symmetry = 'cis asymmetric'
                else:
                    symmetry = 'trans asymmetric'
                if verbose and min(CA_dev, TA_dev) > max_allowed_dev:
                    print('Warning: high deviation from ideal symmetry, manual inspection recommended')
                symmetry_dict = {'symmetry': symmetry, 'cis_asymmetric_dev': CA_dev, 'trans_asymmetric_dev': TA_dev}

            elif unique_ligand_ratios == [1, 1, 1]:
                # Find all angles between coordinating atoms of all ligands and metal.
                lig_angles = np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                                       self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1]),
                                       self.getAngle(idx0=lig3_catoms[0], idx1=metal_idx, idx2=lig3_catoms[1])))
                lig_angles.sort()
                # Classify complex as DCS, DCT, or EA based on deviation from ideal angle.
                DCS_dev_avg = np.average(np.abs(lig_angles - 90))
                DTS_dev_avg = np.average(np.abs(lig_angles - 180))
                EA_dev_avg = np.average(
                    np.abs(np.concatenate((np.array(lig_angles)[0:2] - 90, np.array([lig_angles[2] - 180])))))
                if min(DCS_dev_avg, DTS_dev_avg, EA_dev_avg) == DCS_dev_avg:
                    symmetry = 'double cis symmetric'
                elif min(DCS_dev_avg, DTS_dev_avg, EA_dev_avg) == DTS_dev_avg:
                    symmetry = 'double trans symmetric'
                elif min(DCS_dev_avg, DTS_dev_avg, EA_dev_avg) == EA_dev_avg:
                    symmetry = 'equatorial asymmetric'
                if verbose and min(DCS_dev_avg, DTS_dev_avg, EA_dev_avg) > max_allowed_dev:
                    print('Warning: high deviation from ideal symmetry, manual inspection recommended')
                symmetry_dict = {'symmetry': symmetry, 'double_cis_symmetric_dev': DCS_dev_avg,
                                 'double_trans_symmetric_dev': DTS_dev_avg, 'equatorial_asymmetric_dev': EA_dev_avg}

            elif unique_ligand_ratios == [3 / 2, 2, 3]:
                # Find all angles between coordinating atoms of all L1 and L2 type ligands and metal.
                lig_angles = np.array((self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[1]),
                                       self.getAngle(idx0=lig1_catoms[1], idx1=metal_idx, idx2=lig1_catoms[2]),
                                       self.getAngle(idx0=lig1_catoms[0], idx1=metal_idx, idx2=lig1_catoms[2]),
                                       self.getAngle(idx0=lig2_catoms[0], idx1=metal_idx, idx2=lig2_catoms[1])))
                lig_angles.sort()
                # Classify complex as FA, MAT, or MAC based on deviation from ideal angle.
                FA_dev_avg = np.average(np.abs(lig_angles - 90))
                MAT_dev_avg = np.average(
                    np.abs(np.concatenate((np.array(lig_angles)[0:2] - 90, np.array(lig_angles[2:] - 180)))))
                MAC_dev_avg = np.average(
                    np.abs(np.concatenate((np.array(lig_angles)[0:3] - 90, np.array(lig_angles[3:] - 180)))))

                if min(FA_dev_avg, MAT_dev_avg, MAC_dev_avg) == FA_dev_avg:
                    symmetry = 'fac asymmetric'
                elif min(FA_dev_avg, MAT_dev_avg, MAC_dev_avg) == MAT_dev_avg:
                    symmetry = 'mer asymmetric trans'
                elif min(FA_dev_avg, MAT_dev_avg, MAC_dev_avg) == MAC_dev_avg:
                    symmetry = 'mer asymmetric cis'
                if verbose and min(FA_dev_avg, MAT_dev_avg, MAC_dev_avg) > max_allowed_dev:
                    print('Warning: high deviation from ideal symmetry, manual inspection recommended')
                symmetry_dict = {'symmetry': symmetry, 'fac_asymmetric_dev': FA_dev_avg,
                                 'mer_asymmetric_trans_dev': MAT_dev_avg, 'mer_asymmetric_cis_dev': MAC_dev_avg}

        if details:
            detailed_dict = {'num_unique_ligands': len(ligand_dict), 'unique_ligand_ratios': unique_ligand_ratios,
                             'metal_idx': metal_idx, 'lig1_atoms': lig1_atoms, 'lig1_catoms': lig1_catoms,
                             'lig2_atoms': lig2_atoms, 'lig2_catoms': lig2_catoms,
                             'lig3_atoms': lig3_atoms, 'lig3_catoms': lig3_catoms}
            return symmetry_dict, detailed_dict
        else:
            return symmetry_dict

    def get_symmetry_denticity(self, return_eq_catoms=False, BondedOct=False):
        """
        Get symmetry class of molecule.

        Parameters
        ----------
            return_eq_catoms : bool, optional
                Flag for if equatorial atoms should be returned. Default is False.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.

        Returns
        -------
            eqsym : bool
                Flag for equatorial symmetry.
            maxdent : int
                Maximum denticity in molecule.
            ligdents : list
                List of denticities in molecule.
            homoleptic : bool
                Flag for whether a geometry is homoleptic.
            ligsymmetry : str
                Symmetry class for ligand of interest.
            eq_catoms : list
                List of equatorial connection atoms.
        """

        from molSimplify.Classes.ligand import ligand_breakdown, ligand_assign_consistent, get_lig_symmetry
        liglist, ligdents, ligcons = ligand_breakdown(self, BondedOct=BondedOct)
        flat_eq_ligcons = []
        try:
            _, _, _, _, _, _, _, eq_con_list, _ = ligand_assign_consistent(
                self, liglist, ligdents, ligcons)
            if len(eq_con_list):
                flat_eq_ligcons = [
                    x for sublist in eq_con_list for x in sublist]
                assigned = True
            else:
                assigned = False
        except ValueError:
            # Excepts the case where ligdents is empty and the call to
            # max(ligdents) in ligand_assign_consistent raises a ValueError.
            # There needs to be a better way to check this! RM 2022/02/17
            assigned = False
        if ligdents:
            maxdent = max(ligdents)
        else:
            maxdent = 0
        eqsym = None
        homoleptic = True
        ligsymmetry = None
        if assigned:
            metal_ind = self.findMetal()[0]
            n_eq_syms = len(
                list(set([self.getAtom(x).sym for x in flat_eq_ligcons])))
            flat_eq_dists = [np.round(self.get_pair_distance(
                x, metal_ind), 6) for x in flat_eq_ligcons]
            minmax_eq_plane = max(flat_eq_dists) - min(flat_eq_dists)
            # Match eq plane symbols and eq plane dists
            if (n_eq_syms < 2) and (minmax_eq_plane < 0.2):
                eqsym = True
            else:
                eqsym = False
            ligsymmetry = get_lig_symmetry(self)
        if eqsym:
            for lig in liglist[1:]:
                if not connectivity_match(liglist[0], lig, self, self):
                    homoleptic = False
        else:
            homoleptic = False
        if return_eq_catoms:
            if eqsym:
                eq_catoms = flat_eq_ligcons
            else:
                eq_catoms = False
            return eqsym, maxdent, ligdents, homoleptic, ligsymmetry, eq_catoms
        else:
            return eqsym, maxdent, ligdents, homoleptic, ligsymmetry

    def getfarAtomdir(self, uP):
        """
        Get atom furthest from center of mass in a given direction.

        Parameters
        ----------
            uP : list
                List of length 3 [dx, dy, dz] for direction vector.

        Returns
        -------
            dist : float
                Distance of atom from center of mass in angstroms.
        """

        dd = 1000.0
        atomc = [0.0, 0.0, 0.0]
        for atom in self.atoms:
            d0 = distance(atom.coords(), uP)
            if d0 < dd:
                dd = d0
                atomc = atom.coords()
        return distance(self.centermass(), atomc)

    def getfragmentlists(self):
        """
        Get all independent molecules in mol3D.

        Returns
        -------
            atidxes_total : list
                list of lists for atom indices comprising of each distinct molecule.
        """

        atidxes_total = []
        atidxes_unique = set([0])
        atidxes_done = []
        natoms_total_ = len(atidxes_done)
        natoms_total = self.natoms
        while natoms_total_ < natoms_total:
            natoms_ = len(atidxes_unique)
            for atidx in atidxes_unique:
                if atidx not in atidxes_done:
                    atidxes_done.append(atidx)
                    atidxes = self.getBondedAtoms(atidx)
                    atidxes.extend(atidxes_unique)
                    atidxes_unique = set(atidxes)
                    natoms = len(atidxes_unique)
                    natoms_total_ = len(atidxes_done)
            if natoms_ == natoms:
                atidxes_total.append(list(atidxes_unique))
                for atidx in range(natoms_total):
                    if atidx not in atidxes_done:
                        atidxes_unique = set([atidx])
                        natoms_total_ = len(atidxes_done)
                        break

        return atidxes_total

    def graph_from_bodict(self, bo_dict):
        g = []
        for i, atom in enumerate(self.atoms):
            sub_g = []
            connected = []
            for tup in bo_dict:
                if i in tup:
                    if i != tup[0]:
                        connected.append(tup[0])
                    else:
                        connected.append(tup[1])
            for j in range(0,len(self.atoms)):
                if j in connected:
                    sub_g.append(1.)
                else:
                    sub_g.append(0.)
            g.append(sub_g)
        return g

    def initialize(self):
        """
        Initialize the mol3D to an empty object.
        """

        self.atoms = []
        self.natoms = 0
        self.mass = 0
        self.size = 0
        self.graph = np.array([])
        self.bo_mat = np.array([])
        self.bo_dict = {}

    def isPristine(self, unbonded_min_dist=1.3, oct=False):
        """
        Checks the organic portions of a transition metal complex and
        determines if they look good.

        Parameters
        ----------
            unbonded_min_dist : float, optional
                Minimum distance for two things that are not bonded (in angstrom). Default is 1.3.
            oct : bool, optional
                Flag for octahedral complex. Default is False.

        Returns
        -------
            pass : bool
                Whether or not molecule passes the organic checks.
            fail_list : list
                List of failing criteria, as a set of strings.
        """

        if len(self.graph) == 0:
            self.createMolecularGraph(oct=oct)

        failure_reason = []
        pristine = True
        metal_idx = self.findMetal()
        non_metals = [i for i in range(self.natoms) if i not in metal_idx]

        # Ensure that non-bonded atoms are well-seperated (not close to overlapping or crowded).
        for atom1 in non_metals:
            bonds = self.graph[atom1]
            for atom2 in non_metals:
                if atom1 == atom2:  # Ignore pairwise interactions.
                    continue
                bond = bonds[atom2]
                if bond < 0.1:  # These atoms are not bonded.
                    min_distance = unbonded_min_dist * \
                        (self.atoms[atom1].rad+self.atoms[atom2].rad)
                    d = distance(self.atoms[atom1].coords(),
                                 self.atoms[atom2].coords())
                    if d < min_distance:
                        failure_reason.append(
                            f'Crowded organic atoms {atom1}-{atom2} {round(d, 2)} angstrom.')
                        pristine = False

        return pristine, failure_reason

    def is_edge_compound(self, transition_metals_only: bool = True) -> Tuple[int, List, List]:
        """
        Check if a TMC/mononuclear metal complex structure is an edge compound.

        Parameters
        ----------
            transition_metals_only : bool, optional
                Flag if only transition metals counted as metals. Default is True.

        Returns
        -------
            num_edge_lig : int
                Number of edge ligands.
            info_edge_lig : list
                List of dictionaries with info about edge ligands.
            edge_lig_atoms: list
                List of dictionaries with the connecting atoms of the edge ligands.
        """

        # Request: 1) complexes with ligands where there are at least
        # two connected non-metal atoms both connected to the metal.

        from molSimplify.Informatics.graph_analyze import obtain_truncation_metal
        (num_sandwich_lig, info_sandwich_lig, aromatic, allconnect,
         sandwich_lig_atoms) = self.is_sandwich_compound(
             transition_metals_only=transition_metals_only
        )
        if not num_sandwich_lig or (num_sandwich_lig and not allconnect):
            mol_fcs = obtain_truncation_metal(self, hops=1, transition_metals_only=transition_metals_only)
            metal_ind = mol_fcs.findMetal(transition_metals_only=transition_metals_only)[0]
            catoms = list(range(mol_fcs.natoms))
            catoms.remove(metal_ind)
            edge_ligands, _el = list(), list()
            for atom0 in catoms:
                lig = mol_fcs.findsubMol(
                    atom0=atom0, atomN=metal_ind, smart=True)
                if len(lig) >= 2 and not set(lig) in _el:
                    edge_ligands.append([set(lig)])
                    _el.append(set(lig))
            num_edge_lig = len(edge_ligands)
            info_edge_lig = [
                {"natoms_connected": len(x[0])} for x in edge_ligands]
            edge_lig_atoms = [
                {"atom_idxs": x[0]} for x in edge_ligands]
        else:
            num_edge_lig, info_edge_lig, edge_lig_atoms = 0, list(), list()
        return num_edge_lig, info_edge_lig, edge_lig_atoms

    def is_linear_ligand(self, ind):
        """
        Check whether a ligand is linear.

        Parameters
        ----------
            ind : int
                Index for one of the metal-coordinating atoms.

        Returns
        -------
            flag : bool
                True if the ligand is linear.
            catoms : list
                Atoms bonded to the index of interest.
        """

        def find_the_other_ind(arr, ind):
            arr.pop(arr.index(ind))
            return arr[0]
        catoms = self.getBondedAtomsSmart(ind)
        metal_ind = self.findMetal()[0]
        flag = False
        endcheck = False
        if not self.atoms[ind].sym == 'O':
            if metal_ind in catoms and len(catoms) == 2:
                ind_next = find_the_other_ind(catoms[:], metal_ind)
                _catoms = self.getBondedAtomsSmart(ind_next)
                if (self.atoms[ind].sym, self.atoms[ind_next].sym) in list(self.globs.tribonddict().keys()):
                    dist = np.linalg.norm(
                        np.array(self.atoms[ind].coords()) - np.array(self.atoms[ind_next].coords()))
                    if dist > self.globs.tribonddict()[(self.atoms[ind].sym, self.atoms[ind_next].sym)]:
                        endcheck = True
                else:
                    endcheck = True
                if (not self.atoms[ind_next].sym == 'H') and (not endcheck):
                    if len(_catoms) == 1:
                        flag = True
                    elif len(_catoms) == 2:
                        ind_next2 = find_the_other_ind(_catoms[:], ind)
                        vec1 = np.array(self.getAtomCoords(ind)) - \
                            np.array(self.getAtomCoords(ind_next))
                        vec2 = np.array(self.getAtomCoords(
                            ind_next2)) - np.array(self.getAtomCoords(ind_next))
                        ang = vecangle(vec1, vec2)
                        if ang > 170:
                            flag = True
        return flag, catoms

    def is_sandwich_compound(self, transition_metals_only: bool = True
                             ) -> Tuple[int, List, bool, bool, List]:
        """
        Evaluates whether a TMC/mononuclear metal complex compound is a sandwich compound.

        Parameters
        ----------
            transition_metals_only : bool, optional
                Flag if only transition metals counted as metals. Default is True.

        Returns
        -------
            num_sandwich_lig : int
                Number of sandwich ligands.
            info_sandwich_lig : list
                List of dictionaries about the sandwich ligands.
            aromatic : bool
                Flag about whether the ligand is aromatic.
            allconnect : bool
                Flag for connected atoms in ring.
            sandwich_lig_atoms: list
                List of dictionaries with the connecting atoms of the sandwich ligands.
        """

        # Check if a structure is sandwich compound.
        # Request: 1) complexes with ligands where there are at least
        # three connected non-metal atoms both connected to the metal.
        # 2) These >three connected non-metal atoms are in a ring.
        # 3) Optional: the ring is aromatic.
        # 4) Optional: all the atoms in the base ring are connected to the same metal.

        from molSimplify.Informatics.graph_analyze import obtain_truncation_metal
        mol_fcs = obtain_truncation_metal(self, hops=1, transition_metals_only=transition_metals_only)
        metal_ind = mol_fcs.findMetal(transition_metals_only=transition_metals_only)[0]
        catoms = list(range(mol_fcs.natoms))
        catoms.remove(metal_ind)
        sandwich_ligands, _sl = list(), list()
        for atom0 in catoms:
            lig = mol_fcs.findsubMol(atom0=atom0, atomN=metal_ind, smart=True)
            # Require to be at least a three-member ring.
            if len(lig) >= 3 and not set(lig) in _sl:
                full_lig = self.findsubMol(atom0=mol_fcs.mapping_sub2mol[lig[0]],
                                           atomN=mol_fcs.mapping_sub2mol[metal_ind],
                                           smart=True)
                lig_inds_in_obmol = [sorted(full_lig).index(
                    mol_fcs.mapping_sub2mol[x])+1 for x in lig]
                full_ligmol = self.create_mol_with_inds(full_lig)
                full_ligmol.convert2OBMol2()
                ringlist = full_ligmol.OBMol.GetSSSR()
                for obmol_ring in ringlist:
                    if all([obmol_ring.IsInRing(x) for x in lig_inds_in_obmol]):
                        sandwich_ligands.append(
                            [set(lig), obmol_ring.Size(), obmol_ring.IsAromatic()])
                        _sl.append(set(lig))
                        break
        num_sandwich_lig = len(sandwich_ligands)
        info_sandwich_lig = [
                {"natoms_connected": len(x[0]), "natoms_ring": x[1], "aromatic": x[2]} for x in sandwich_ligands]
        sandwich_lig_atoms = [
                {"atom_idxs": x[0]} for x in sandwich_ligands]
        aromatic = any([x["aromatic"] for x in info_sandwich_lig])
        allconnect = any([x["natoms_connected"] == x["natoms_ring"]
                          for x in info_sandwich_lig])
        return num_sandwich_lig, info_sandwich_lig, aromatic, allconnect, sandwich_lig_atoms

    def ligand_comp_org(self, init_mol, catoms_arr=None,
                        flag_deleteH=True, flag_lbd=True, debug=False, depth=3,
                        BondedOct=False, angle_ref=False):
        """
        Get the ligand distortion by comparing each individual ligands in init_mol and opt_mol.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            flag_deleteH : bool, optional,
                Flag to delete Hs in ligand comparison. Default is True.
            flag_lbd : bool, optional
                Flag for using ligand breakdown on the optimized geometry. If False, assuming equivalent index to initial geo.
                Default is True.
            debug : bool, optional
                Flag for extra printout. Default is False.
            depth : int, optional
                Depth for truncated molecule. Default is 3.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.

        Returns
        -------
            dict_lig_distort : dict
                Dictionary containing rmsd_max and atom_dist_max.
        """

        from molSimplify.Scripts.oct_check_mols import readfromtxt
        from molSimplify.Classes.ligand import ligand_breakdown
        _, _, flag_match = self.match_lig_list(init_mol,
                                               catoms_arr=catoms_arr,
                                               BondedOct=BondedOct,
                                               flag_lbd=flag_lbd,
                                               debug=debug,
                                               depth=depth,
                                               check_whole=True,
                                               angle_ref=angle_ref)
        liglist, liglist_init, _ = self.match_lig_list(init_mol,
                                                       catoms_arr=catoms_arr,
                                                       BondedOct=BondedOct,
                                                       flag_lbd=flag_lbd,
                                                       debug=debug,
                                                       depth=depth,
                                                       check_whole=False,
                                                       angle_ref=angle_ref)
        if debug:
            print(('lig_list:', liglist, len(liglist)))
            print(('lig_list_init:', liglist_init, len(liglist_init)))
        if flag_lbd:
            mymol_xyz = self.my_mol_trunc
            initmol_xyz = self.init_mol_trunc
        else:
            mymol_xyz = self
            initmol_xyz = init_mol
        if flag_match:
            rmsd_arr, max_atom_dist_arr = [], []
            for idx, lig in enumerate(liglist):
                lig_init = liglist_init[idx]
                if debug:
                    print(f'----This is {idx+1} th piece of ligand.')
                    print(('ligand is:', lig, lig_init))
                foo = []
                for ii, atom in enumerate(mymol_xyz.atoms):
                    if ii in lig:
                        xyz = atom.coords()
                        line = f'{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n'
                        foo.append(line)
                tmp_mol = mol3D()
                tmp_mol = readfromtxt(tmp_mol, foo)
                foo = []
                for ii, atom in enumerate(initmol_xyz.atoms):
                    if ii in lig_init:
                        xyz = atom.coords()
                        line = f'{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n'
                        foo.append(line)
                tmp_org_mol = mol3D()
                tmp_org_mol = readfromtxt(tmp_org_mol, foo)
                if debug:
                    print(f'# atoms: {tmp_mol.natoms}, init: {tmp_org_mol.natoms}')
                    print('!!!!atoms:', [x.symbol() for x in tmp_mol.getAtoms()],
                           [x.symbol() for x in tmp_org_mol.getAtoms()])
                if flag_deleteH:
                    tmp_mol.deleteHs()
                    tmp_org_mol.deleteHs()
                try:
                    rmsd = rigorous_rmsd(tmp_mol, tmp_org_mol,
                                         rotation="kabsch", reorder="hungarian")
                except np.linalg.LinAlgError:
                    rmsd = 0
                rmsd_arr.append(rmsd)
                atom_dist_max = -1
                max_atom_dist_arr.append(atom_dist_max)
                if debug:
                    print(('rmsd:', rmsd))
            rmsd_max = max(rmsd_arr)
            atom_dist_max = max(max_atom_dist_arr)
        else:
            rmsd_max, atom_dist_max = 'lig_mismatch', 'lig_mismatch'
        try:
            dict_lig_distort = {'rmsd_max': float(
                rmsd_max), 'atom_dist_max': float(atom_dist_max)}
        except ValueError:
            dict_lig_distort = {'rmsd_max': rmsd_max,
                                'atom_dist_max': atom_dist_max}
        self.dict_lig_distort = dict_lig_distort
        return dict_lig_distort

    def make_formula(self, latex=True):
        """
        Get a chemical formula from the mol3D class instance.

        Parameters
        ----------
            latex : bool, optional
                Flag for if formula is going to go in a latex document. Default is True.

        Returns
        -------
            retstr : str
                Chemical formula
        """

        retstr = ""
        atomorder = self.globs.elementsbynum()
        unique_symbols = dict()
        for atoms in self.getAtoms():
            if atoms.symbol() in atomorder:
                if atoms.symbol() in list(unique_symbols.keys()):
                    unique_symbols[atoms.symbol(
                    )] = unique_symbols[atoms.symbol()] + 1
                else:
                    unique_symbols[atoms.symbol()] = 1

        skeys = sorted(list(unique_symbols.keys()), key=lambda x: (
            self.globs.elementsbynum().index(x)))
        skeys = skeys[::-1]
        for sk in skeys:
            if latex:
                retstr += '\\textrm{' + sk + '}_{' + \
                          str(int(unique_symbols[sk])) + '}'
            else:
                retstr += sk+str(int(unique_symbols[sk]))
        return retstr

    def match_lig_list(self, init_mol, catoms_arr=None,
                       BondedOct=False, flag_lbd=True, debug=False, depth=3,
                       check_whole=False, angle_ref=False):
        """
        Match the ligands of mol and init_mol by calling ligand_breakdown.

        Parameters
        ----------
            init_mol : mol3D
                mol3D class instance of the initial geometry.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
                Default is Nonetype.
            BondedOct : bool, optional
                Flag for bonding. Only used in Oct_inspection, not in geo_check. Default is False.
            flag_lbd : bool, optional
                Flag for using ligand breakdown on the optimized geometry. If False, assuming equivalent index to initial geo.
                Default is True.
            debug : bool, optional
                Flag for extra printout. Default is False.
            depth : int, optional
                Depth for truncated molecule. Default is 3.
            check_whole : bool, optional
                Flag for checking whole ligand.
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.

        Returns
        -------
            liglist_shifted : list
                List of lists containing all ligands from optimized molecule.
            liglist_init : list
                List of lists containing all ligands from initial molecule.
            flag_match : bool
                A flag about whether the ligands of initial and optimized mol are exactly the same.
                There is a one to one mapping.
        """

        from molSimplify.Informatics.graph_analyze import obtain_truncation_metal
        from molSimplify.Classes.ligand import ligand_breakdown
        flag_match = True
        self.my_mol_trunc = mol3D()
        self.my_mol_trunc.copymol3D(self)
        self.init_mol_trunc = mol3D()
        self.init_mol_trunc.copymol3D(init_mol)
        if flag_lbd:  # Also do ligand breakdown for opt geo.
            if not check_whole:
                # Truncate ligands at 4 bonds away from metal to avoid rotational group.
                self.my_mol_trunc = obtain_truncation_metal(self, hops=depth)
                self.init_mol_trunc = obtain_truncation_metal(
                    init_mol, hops=depth)
                self.my_mol_trunc.createMolecularGraph()
                self.init_mol_trunc.createMolecularGraph()
                self.my_mol_trunc.writexyz("final_trunc.xyz")
                self.init_mol_trunc.writexyz("init_trunc.xyz")
            liglist_init, ligdents_init, ligcons_init = ligand_breakdown(
                self.init_mol_trunc, BondedOct=BondedOct)
            liglist, ligdents, ligcons = ligand_breakdown(self.my_mol_trunc, BondedOct=BondedOct)
            liglist_atom = [[self.my_mol_trunc.getAtom(x).symbol() for x in ele]
                            for ele in liglist]
            liglist_init_atom = [[self.init_mol_trunc.getAtom(x).symbol() for x in ele]
                                 for ele in liglist_init]
            if debug:
                print(('init_mol_trunc:', [x.symbol()
                                           for x in self.init_mol_trunc.getAtoms()]))
                print(('liglist_init, ligdents_init, ligcons_init',
                       liglist_init, ligdents_init, ligcons_init))
                print(('liglist, ligdents, ligcons', liglist, ligdents, ligcons))
        else:  # Create/use the liglist, ligdents, ligcons of initial geo as we just want to track them down.
            if debug:
                print('Just inherit the ligand list from init structure.')
            liglist_init, ligdents_init, ligcons_init = ligand_breakdown(init_mol,
                                                                         BondedOct=BondedOct)
            liglist, ligdents, ligcons = liglist_init[:
                                                      ], ligdents_init[:], ligcons_init[:]
            liglist_atom = [[self.getAtom(x).symbol() for x in ele]
                            for ele in liglist]
            liglist_init_atom = [[init_mol.getAtom(x).symbol() for x in ele]
                                 for ele in liglist_init]
        if catoms_arr is not None:
            catoms, catoms_init = catoms_arr, catoms_arr
        else:
            self.my_mol_trunc.writexyz("final_trunc.xyz")
            self.init_mol_trunc.writexyz("init_trunc.xyz")
            _, catoms = self.my_mol_trunc.oct_comp(
                debug=False, angle_ref=angle_ref)
            _, catoms_init = self.init_mol_trunc.oct_comp(
                debug=False, angle_ref=angle_ref)
        if debug:
            print(('ligand_list opt in symbols:', liglist_atom))
            print(('ligand_list init in symbols: ', liglist_init_atom))
            print(("catoms opt: ", catoms, [
                  self.getAtom(x).symbol() for x in catoms]))
            print(("catoms init: ", catoms_init, [
                  self.getAtom(x).symbol() for x in catoms_init]))
            print(("catoms diff: ", set(catoms) - set(catoms_init),
                   len(set(catoms) - set(catoms_init))))
        liglist_shifted = []
        if len(set(catoms) - set(catoms_init)):
            print("catoms for opt and init geo:", set(catoms), set(catoms_init))
            print('Ligands cannot match! (Connecting atoms are different)')
            flag_match = False
        else:
            for ii, ele in enumerate(liglist_init_atom):
                liginds_init = liglist_init[ii]
                try:
                    _flag = False
                    for idx, _ele in enumerate(liglist_atom):
                        if set(ele) == set(_ele) and len(ele) == len(_ele):
                            liginds = liglist[idx]
                            if catoms_arr is not None:
                                match = True
                            else:
                                match = connectivity_match(liginds_init, liginds, self.init_mol_trunc,
                                                           self.my_mol_trunc)
                            if debug:
                                print(
                                    ('fragment in liglist_init', ele, liginds_init))
                                print(('fragment in liglist', _ele, liginds))
                                print(("match status: ", match))
                            if match:
                                posi = idx
                                _flag = True
                                break
                    liglist_shifted.append(liglist[posi])
                    liglist_atom.pop(posi)
                    liglist.pop(posi)
                    if not _flag:
                        if debug:
                            print('Ligands cannot match!')
                        flag_match = False
                except UnboundLocalError:
                    # If there is no match the variable posi is never assigned.
                    if debug:
                        print("UnboundLocalError.")
                        print('Ligands cannot match!')
                    flag_match = False
        if debug:
            print('returning: ', liglist_shifted, liglist_init)
        if catoms_arr is not None:  # Force as matching in inspection mode.
            flag_match = True
        return liglist_shifted, liglist_init, flag_match

    def maxatomdist(self, mol2):
        """
        Compute the max atom distance between two molecules.
        Does not align molecules. For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            dist_max : float
                Maximum atom distance between two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        dist_max = 0
        if (Nat0 != Nat1):
            print(
                "ERROR: max_atom_dist can be calculated only for molecules with the same number of atoms..")
            return float('NaN')
        else:
            for atom0, atom1 in zip(self.getAtoms(), mol2.getAtoms()):
                dist = atom0.distance(atom1)
                if dist > dist_max:
                    dist_max = dist
            return dist_max

    def maxatomdist_nonH(self, mol2):
        """
        Compute the max atom distance between two molecules, considering heavy atoms only.
        Does not align molecules. For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            dist_max : float
                Maximum atom distance between two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        dist_max = 0
        if (Nat0 != Nat1):
            print(
                "ERROR: max_atom_dist can be calculated only for molecules with the same number of atoms.")
            return float('NaN')
        else:
            for atom0, atom1 in zip(self.getAtoms(), mol2.getAtoms()):
                if (not atom0.sym == 'H') and (not atom1.sym == 'H'):
                    dist = atom0.distance(atom1)
                    if dist > dist_max:
                        dist_max = dist
            return dist_max

    def maxdist(self, mol):
        """
        Measure the largest distance between atoms in two molecules.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance of second molecule.

        Returns
        -------
            maxd : float
                Max distance between atoms of two molecules.
        """

        maxd = 0
        for atom1 in mol.atoms:
            for atom0 in self.atoms:
                if (distance(atom1.coords(), atom0.coords()) > maxd):
                    maxd = distance(atom1.coords(), atom0.coords())
        return maxd

    def meanabsdev(self, mol2):
        """
        Compute the mean absolute deviation (MAD) between two molecules.
        Does not align molecules. For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            dev : float
                Mean absolute deviation between the two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        if (Nat0 != Nat1):
            print(
                "ERROR: Absolute atom deviations can be calculated only for molecules with the same number of atoms..")
            return float('NaN')
        else:
            dev = 0
            for atom0, atom1 in zip(self.getAtoms(), mol2.getAtoms()):
                dev += abs((atom0.distance(atom1)))
            if Nat0 == 0:
                dev = 0
            else:
                dev /= Nat0
            return dev

    def mindist(self, mol):
        """
        Measure the smallest distance between atoms in two molecules.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance of second molecule.

        Returns
        -------
            mind : float
                Min distance between atoms of two molecules.
        """

        mind = 1000
        for atom1 in mol.atoms:
            for atom0 in self.atoms:
                if (distance(atom1.coords(), atom0.coords()) < mind):
                    mind = distance(atom1.coords(), atom0.coords())
        return mind

    def mindistmol(self):
        """
        Measure the smallest distance between atoms in a single molecule.

        Returns
        -------
            mind : float
                Min distance between atoms of two molecules.
        """

        mind = 1000
        for ii, atom1 in enumerate(self.atoms):
            for jj, atom0 in enumerate(self.atoms):
                d = distance(atom1.coords(), atom0.coords())
                if (d < mind) and ii != jj:
                    mind = distance(atom1.coords(), atom0.coords())
        return mind

    def mindistnonH(self, mol):
        """
        Measure the smallest distance between an atom and a non H atom in another molecule.

        Parameters
        ----------
            mol : mol3D
                mol3D class of second molecule.

        Returns
        -------
            mind : float
                Min distance between atoms of two molecules that are not Hs.
        """

        mind = 1000
        for atom1 in mol.atoms:
            for atom0 in self.atoms:
                if (distance(atom1.coords(), atom0.coords()) < mind):
                    if (atom1.sym != 'H' and atom0.sym != 'H'):
                        mind = distance(atom1.coords(), atom0.coords())
        return mind

    def mindisttopoint(self, point):
        """
        Measure the smallest distance between an atom and a point.

        Parameters
        ----------
            point : list
                List of coordinates of reference point.

        Returns
        -------
            mind : float
                Min distance between atoms of two molecules.
        """

        mind = 1000
        for atom1 in self.atoms:
            d = distance(atom1.coords(), point)
            if (d < mind):
                mind = d
        return mind

    def mol3D_to_networkx(self,get_symbols:bool=True,get_bond_order:bool=True,get_bond_distance:bool=False):
        g = nx.Graph()
        # Get every index of atoms in mol3D object.
        for atom_ind in range(0,self.natoms):
            # Set each atom as a node in the graph, and add symbol information if wanted.
            data={}
            if get_symbols:
                data['Symbol']=self.getAtom(atom_ind).symbol()
                data['atom3D']=self.getAtom(atom_ind)
            g.add_node(atom_ind,**data)
        # Get every bond in mol3D object.
        bond_info=self.bo_dict
        for bond in bond_info:
            # Set each bond as an edge in the graph, and add symbol information if wanted.
            data={}
            if get_bond_order:
                data['bond_order']=bond_info[bond]
            if get_bond_distance:
                distance=self.getAtom(bond[0]).distance(self.getAtom(bond[1]))
                data['bond_distance']=distance
            g.add_edge(bond[0],bond[1],**data)
        return g

    def mols_symbols(self):
        """
        Store symbols and their frequencies in symbols_dict attributes.
        """

        self.symbols_dict = {}
        for atom in self.getAtoms():
            if atom.symbol() in self.symbols_dict:
                self.symbols_dict[atom.symbol()] += 1
            else:
                self.symbols_dict.update({atom.symbol(): 1})

    def molsize(self):
        """
        Measure the size of the molecule, by quantifying the max distance
        between atoms and center of mass.

        Returns
        -------
            maxd : float
                Max distance between an atom and the center of mass.
        """

        maxd = 0
        cm = self.centermass()
        for atom in self.atoms:
            if distance(cm, atom.coords()) > maxd:
                maxd = distance(cm, atom.coords())
        return maxd

    def moments_of_inertia(self):
        """
        Determines the moments of inertia for the object, in the specified coordinates
        (after centering about the center of mass).

        Returns
        -------
            I : np.array
                Moments of inertia tensor.
        """

        copy = mol3D()
        copy.copymol3D(self)

        I = np.zeros((3, 3))
        # Center about the center of mass.
        cm = self.centermass()
        for atom in copy.atoms:
            atom.setcoords(np.array(atom.coords()) - cm)
            I[0, 0] += atom.mass * (atom.coords()[1]**2 + atom.coords()[2]**2) #xx
            I[1, 1] += atom.mass * (atom.coords()[0]**2 + atom.coords()[2]**2) #yy
            I[2, 2] += atom.mass * (atom.coords()[0]**2 + atom.coords()[1]**2) #zz
            I[0, 1] -= atom.mass * (atom.coords()[0] * atom.coords()[1]) #xy
            I[1, 0] -= atom.mass * (atom.coords()[0] * atom.coords()[1]) #yx
            I[0, 2] -= atom.mass * (atom.coords()[2] * atom.coords()[0]) #xz
            I[2, 0] -= atom.mass * (atom.coords()[2] * atom.coords()[0]) #zx
            I[1, 2] -= atom.mass * (atom.coords()[1] * atom.coords()[2]) #yz
            I[2, 1] -= atom.mass * (atom.coords()[1] * atom.coords()[2]) #zy
        return I

    def num_rings(self, index):
        """
        Computes the number of simple rings an atom is in.

        Parameters
        ----------
            index : int
                The index of the atom in question. Zero-indexing, so the first atom has an index of zero.

        Returns
        -------
            myNumRings : int
                The number of rings the atom is in.
        """

        self.convert2OBMol()             # Need to populate the self.OBMol field.
        ringlist = self.OBMol.GetSSSR()  # Get the smallest set of simple rings for a molecule.
        ringinds = []
        for obmol_ring in ringlist:  # Loop through the simple rings.
            _inds = []
            for ii in range(1, self.natoms+1):  # Loop through all atoms in the mol3D object.
                if obmol_ring.IsInRing(ii):     # Check if a given atom is in the current ring.
                    _inds.append(ii-1)
            ringinds.append(_inds)

        # ringinds is an array of arrays, where each inner array contains the atom indices of the atoms in a simple ring.
        # The length of ringinds is the number of simple rings in the mol3D object calling numRings.

        myNumRings = 0  # Running tally

        for idx_list in ringinds:
            if index in idx_list:
                myNumRings += 1

        return myNumRings

    def oct_comp(self, angle_ref=False, catoms_arr=None, debug=False):
        """
        Get the deviation of shape of the catoms from the desired shape,
        which is defined in angle_ref.

        Parameters
        ----------
            angle_ref : bool, optional
                Reference list of list for the expected angles (A-metal-B) of each connection atom.
            catoms_arr : Nonetype, optional
                Uses the catoms of the mol3D by default. User can overwrite this connection atom array by explicit input.
            debug : bool, optional
                Flag for extra printout. Default is False.

        Returns
        -------
            dict_catoms_shape : dict
                Dictionary of first coordination sphere shape measures.
            catoms_arr : list
                Connection atom array.
        """

        if not angle_ref:
            angle_ref = self.oct_angle_ref
        from molSimplify.Scripts.oct_check_mols import loop_target_angle_arr

        metal_coord = self.getAtomCoords(self.findMetal()[0])
        catom_coord = []
        # Note that use this only when you want to specify the metal connecting atoms.
        # This will change the attributes of mol3D.
        if catoms_arr is not None:
            self.catoms = catoms_arr
            self.num_coord_metal = len(catoms_arr)
        else:
            self.get_num_coord_metal(debug=debug)
        theta_arr, oct_dist = [], []
        for atom in self.catoms:
            coord = self.getAtomCoords(atom)
            catom_coord.append(coord)
        th_input_arr = []
        catoms_map = {}
        for idx1, coord1 in enumerate(catom_coord):
            catoms_map.update({self.catoms[idx1]: idx1})
            delr1 = (np.array(coord1) - np.array(metal_coord)).tolist()
            theta_tmp = []
            for idx2, coord2 in enumerate(catom_coord):
                if idx2 != idx1:
                    delr2 = (np.array(coord2) - np.array(metal_coord)).tolist()
                    theta = vecangle(delr1, delr2)
                    theta_tmp.append(theta)
                else:
                    theta_tmp.append(-1)
            th_input_arr.append([self.catoms[idx1], theta_tmp])
        # This will help pick out 6 catoms that forms the closest shape compared to the desired structure.
        # When we have the customized catoms_arr, it will not change anything.
        th_output_arr, sum_del_angle, catoms_arr, max_del_sig_angle = loop_target_angle_arr(
            th_input_arr, angle_ref, catoms_map)
        self.catoms = catoms_arr
        if debug:
            print(('th:', th_output_arr))
            print(('sum_del:', sum_del_angle))
            print(('catoms_arr:', catoms_arr))
            print(('catoms_type:', [self.getAtom(x).symbol()
                                    for x in catoms_arr]))
            print(('catoms_coord:', [self.getAtom(x).coords()
                                     for x in catoms_arr]))
        for idx, ele in enumerate(th_output_arr):
            theta_arr.append([catoms_arr[idx], sum_del_angle[idx], ele])
        theta_trunc_arr = theta_arr
        theta_trunc_arr_T = list(map(list, list(zip(*theta_trunc_arr))))
        oct_catoms = theta_trunc_arr_T[0]
        oct_angle_devi = theta_trunc_arr_T[1]
        oct_angle_all = theta_trunc_arr_T[2]
        if debug:
            print(('Summation of deviation angle for catoms:', oct_angle_devi))
            print(('Angle for catoms:', oct_angle_all))
        for atom in oct_catoms:
            coord = self.getAtom(atom).coords()
            dist = np.linalg.norm(np.array(coord) - np.array(metal_coord))
            oct_dist.append(dist)
        oct_dist.sort()
        dist_del_all = oct_dist[-1] - oct_dist[0]
        oct_dist_relative = [(np.linalg.norm(np.array(self.getAtom(ii).coords()) -
                                             np.array(metal_coord)))
                             / (self.globs.amass()[self.getAtom(ii).sym][2]
                                + self.globs.amass()[self.getAtom(self.findMetal()[0]).sym][2])
                             for ii in oct_catoms]
        dict_catoms_shape = dict()
        dict_catoms_shape['oct_angle_devi_max'] = float(max(oct_angle_devi))
        dict_catoms_shape['max_del_sig_angle'] = float(max_del_sig_angle)
        dict_catoms_shape['dist_del_eq'] = 0
        dict_catoms_shape['dist_del_all'] = float(dist_del_all)
        dict_catoms_shape['dist_del_all_relative'] = np.max(
            oct_dist_relative) - np.min(oct_dist_relative)
        dict_catoms_shape['dist_del_eq_relative'] = 0
        self.dict_catoms_shape = dict_catoms_shape
        return dict_catoms_shape, catoms_arr

    def overlapcheck(self, mol, silence=False):
        """
        Measure the smallest distance between an atom and a point.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance of second molecule.
            silence : bool, optional
                Flag for extra output. Default is False.

        Returns
        -------
            overlap : bool
                Flag for whether two molecules are overlapping.
        """

        overlap = False
        for atom1 in mol.atoms:
            for atom0 in self.atoms:
                if (distance(atom1.coords(), atom0.coords()) < 0.85 * (atom1.rad + atom0.rad)):
                    overlap = True
                    if not silence:
                        print("#############################################################")
                        print("!!!Molecules might be overlapping. Increase distance!!!")
                        print("#############################################################")
                    break
        return overlap

    def populateBOMatrix(self, bonddict=False, set_bo_mat=False):
        """
        Populate the bond order matrix using openbabel.

        Parameters
        ----------
            bonddict : bool
                Flag for if the obmol bond dictionary should be saved. Default is False.
            set_bo_mat : bool
                Flag for whether self.bo_mat and self.graph should be set. Default is False.

        Returns
        -------
            molBOMat : np.array
                Numpy array for bond order matrix.
        """

        if not self.OBMol:
            print('Need to set OBMol attribute first. Exiting.')
            return None
        obiter = openbabel.OBMolBondIter(self.OBMol)
        n = self.natoms
        molBOMat = np.zeros((n, n))
        bond_dict = dict()
        for bond in obiter:
            these_inds = [bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()]
            this_order = bond.GetBondOrder()
            molBOMat[these_inds[0] - 1, these_inds[1] - 1] = this_order
            molBOMat[these_inds[1] - 1, these_inds[0] - 1] = this_order
            bond_dict[tuple(
                sorted([these_inds[0]-1, these_inds[1]-1]))] = this_order
        if bonddict:
            self.bo_dict = bond_dict
        if set_bo_mat:
            self.bo_mat = molBOMat
            self.graph = (molBOMat > 0).astype(int)

        return molBOMat

    def populateBOMatrixAug(self):
        """
        Populate the augmented bond order matrix using openbabel.

        Parameters
        ----------
            bonddict : bool
                Flag for if the obmol bond dictionary should be saved. Default is False.

        Returns
        -------
            molBOMat : np.array
                Numpy array for augmented bond order matrix.
        """

        obiter = openbabel.OBMolBondIter(self.OBMol)
        n = self.natoms
        molBOMat = np.zeros((n, n))
        for bond in obiter:
            these_inds = [bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()]
            this_order = bond.GetBondOrder()
            molBOMat[these_inds[0] - 1, these_inds[1] - 1] = this_order
            molBOMat[these_inds[1] - 1, these_inds[0] - 1] = this_order
        self.convert2mol3D()
        self.createMolecularGraph()
        molgraph = self.graph
        error_mat = molBOMat - molgraph
        error_idx = np.where(error_mat < 0)
        for i in range(len(error_idx)):
            if len(error_idx[i]):
                molBOMat[error_idx[i].tolist()[0], error_idx[i].tolist()[1]] = 1
        return molBOMat

    def principal_moments_of_inertia(self, return_eigvecs=False):
        """
        Returns the principal moments of inertia, and optionally
        the eigenvectors defining the principal axes.

        Parameters
        ----------
            return_eigvecs : bool
                Flag for if the matrices used to diagonalize I should be returned.
                Default is False.

        Returns
        -------
            pmom : np.array
                3x1 array of the principal moments of inertia, in the provided Cartesian frame.
            eigvecs : np.array
                3x3 array where each column is an eigenvector.
        """

        I = self.moments_of_inertia()
        # Diagonalize the moments of inertia.
        eigvals, eigvecs = np.linalg.eigh(I)
        D = np.linalg.inv(eigvecs) @ I @ eigvecs
        pmom = np.diag(D)

        if return_eigvecs:
            return pmom, eigvecs
        else:
            return pmom

    def print_geo_dict(self):
        """
        Print geometry check info after the check.
        """

        def print_dict(_dict):
            for key, value in list(_dict.items()):
                print(('%s: ' % key, value))
        print('========Geo_check_results========')
        print('--------coordination_check-----')
        print(('num_coord_metal:', self.num_coord_metal))
        print(('catoms_arr:', self.catoms))
        print('-------catoms_shape_check-----')
        _dict = self.dict_catoms_shape
        print_dict(_dict)
        print('-------individual_ligand_distortion_check----')
        _dict = self.dict_lig_distort
        print_dict(_dict)
        print('-------linear_ligand_orientation_check-----')
        _dict = self.dict_orientation
        print_dict(_dict)
        print('=======End of printing geo_check_results========')

    def printxyz(self):
        """
        Print XYZ info of mol3D class instance to stdout. To write to file
        (more common), use writexyz() instead.
        """

        for atom in self.atoms:
            xyz = atom.coords()
            ss = f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}"
            print(ss)

    def read_bo_from_mol(self, molfile):
        with open(molfile, 'r') as fo:
            for line in fo:
                ll = line.split()
                if len(ll) == 7 and all([x.isdigit() for x in ll]):
                    self.bo_mat[int(ll[0])-1, int(ll[1])-1] = int(ll[2])
                    self.bo_mat[int(ll[1])-1, int(ll[0])-1] = int(ll[2])

    def read_bond_order(self, bofile):
        """
        Get bond order information from file.

        Parameters
        ----------
            bofile : str
                Path to a bond order file.
        """

        bonds_organic = {'H': 1, 'C': 4, 'N': 3,
                         'O': 2, 'F': 1, 'P': 3, 'S': 2}
        self.bv_dict = {}
        self.ve_dict = {}
        self.bvd_dict = {}
        self.bodstd_dict = {}
        self.bodavrg_dict = {}
        self.bo_mat = np.zeros(shape=(self.natoms, self.natoms))
        if os.path.isfile(bofile):
            with open(bofile, "r") as fo:
                for line in fo:
                    ll = line.split()
                    if len(ll) == 5 and ll[0].isdigit() and ll[1].isdigit():
                        self.bo_mat[int(ll[0]), int(ll[1])] = float(ll[2])
                        self.bo_mat[int(ll[1]), int(ll[0])] = float(ll[2])
                        if int(ll[0]) == int(ll[1]):
                            self.bv_dict.update({int(ll[0]): float(ll[2])})
        else:
            print(("bofile does not exist.", bofile))
        for ii in range(self.natoms):
            self.ve_dict.update({ii: bonds_organic[self.atoms[ii].symbol()]})
            self.bvd_dict.update({ii: self.bv_dict[ii] - self.ve_dict[ii]})
            vec = self.bo_mat[ii, :][self.bo_mat[ii, :] > 0.1]
            if vec.shape[0] == 0:
                self.bodstd_dict.update({ii: 0})
                self.bodavrg_dict.update({ii: 0})
            else:
                devi = [abs(v - max(round(v), 1)) for v in vec]
                self.bodstd_dict.update({ii: np.std(devi)})
                self.bodavrg_dict.update({ii: np.mean(devi)})

    def read_charge(self, chargefile):
        """
        Get charge information from file.

        Parameters
        ----------
            chargefile : str
                Path to a charge file.
        """

        self.charge_dict = {}
        if os.path.isfile(chargefile):
            with open(chargefile, "r") as fo:
                for line in fo:
                    ll = line.split()
                    if len(ll) == 3 and ll[0].isdigit():
                        self.charge_dict.update({int(ll[0]) - 1: float(ll[2])})
        else:
            print(("chargefile does not exist.", chargefile))

    def read_smiles(self, smiles, ff="mmff94", steps=2500):
        """
        Read a smiles string and convert it to a mol3D class instance.

        Parameters
        ----------
            smiles : str
                SMILES string to be interpreted by openbabel.
            ff : str, optional
                Forcefield to be used by openbabel. Default is mmff94.
            steps : int, optional
                Steps to be taken by forcefield. Default is 2500.
        """

        # Used to convert from one format (ex, SMILES) to another (ex, mol3D).
        obConversion = openbabel.OBConversion()

        # The input format "SMILES"; Reads the SMILES - all stacked as 2-D - one on top of the other.
        obConversion.SetInFormat("SMILES")
        OBMol = openbabel.OBMol()
        obConversion.ReadString(OBMol, smiles)

        # Adds hydrogens
        OBMol.AddHydrogens()

        # Get a 3-D structure with H's.
        builder = openbabel.OBBuilder()
        builder.Build(OBMol)

        # Force field optimization is done in the specified number of "steps" using the specified "ff" force field.
        if ff:
            forcefield = openbabel.OBForceField.FindForceField(ff)
            s = forcefield.Setup(OBMol)
            if not s:
                print('FF setup failed')
            forcefield.ConjugateGradients(steps)
            forcefield.GetCoordinates(OBMol)

        # mol3D structure
        self.OBMol = OBMol
        self.convert2mol3D()

    def readfrommol(self, filename):
        """
        Read mol into a mol3D class instance. Stores the bond orders and atom types.

        Parameters
        -------
            filename : string
                String of path to MOL file. Path may be local or global.
        """

        with open(filename, 'r') as f:
            contents = f.readlines()

        counts_block_line_idx, num_atoms, num_bonds = None, None, None

        # Searching for counts block.
        for idx, line in enumerate(contents):
            split_line = line.split()

            # Counts block
            if len(split_line) == 11 or len(split_line) == 12:
                counts_block_line_idx = idx
                num_atoms = int(split_line[0])
                num_bonds = int(split_line[1])
                break

        if counts_block_line_idx is None:
            print('Failed to read the .mol file.')
            return

        # Atoms block
        for idx, line in enumerate(contents[counts_block_line_idx+1:counts_block_line_idx+num_atoms+1]):
            split_line = line.split()
            x_coord = float(split_line[0])
            y_coord = float(split_line[1])
            z_coord = float(split_line[2])
            sym = split_line[3]

            my_atom = atom3D(Sym=sym, xyz=[x_coord,y_coord,z_coord])
            self.addAtom(my_atom)

        self.graph = np.zeros((num_atoms, num_atoms))
        self.bo_mat = np.zeros((num_atoms, num_atoms))
        self.bo_dict = {}

        # Bonds block
        for idx, line in enumerate(contents[counts_block_line_idx+num_atoms+1:counts_block_line_idx+num_atoms+num_bonds+1]):
            split_line = line.split()

            atom1_idx = int(split_line[0])-1
            atom2_idx = int(split_line[1])-1
            bond_type = split_line[2]

            self.graph[atom1_idx, atom2_idx] = 1
            self.graph[atom2_idx, atom1_idx] = 1
            self.bo_mat[atom1_idx, atom2_idx] = bond_type
            self.bo_mat[atom2_idx, atom1_idx] = bond_type

            self.bo_dict[tuple(sorted([atom1_idx, atom2_idx]))] = bond_type

    def readfrommol2(self, filename, readstring=False):
        """
        Read mol2 into a mol3D class instance. Stores the bond orders and atom types (SYBYL).

        Parameters
        -------
            filename : string
                String of path to MOL2 file. Path may be local or global. May be read in as a string.
            readstring : bool
                Flag for deciding whether a string of mol2 file is being passed as the filename.
        """

        globs = globalvars()
        amassdict = globs.amass()
        graph = False
        bo_graph = False
        bo_dict = False
        if readstring:
            s = filename.splitlines()
        else:
            with open(filename, 'r') as f:
                s = f.read().splitlines()
        read_atoms = False
        read_bonds = False
        self.charge = 0
        for line in s:
            # Get atoms first.
            if '<TRIPOS>BOND' in line:
                read_atoms = False
            if '<TRIPOS>SUBSTRUCTURE' in line:
                read_bonds = False
            if '<TRIPOS>UNITY_ATOM_ATTR' in line:
                read_atoms = False
            if read_atoms:
                s_line = line.split()
                # Check redundancy in chemical symbols.
                atom_symbol1 = re.sub('[0-9]+[A-Z]+', '', line.split()[1])
                atom_symbol1 = re.sub('[0-9]+', '', atom_symbol1)
                atom_symbol2 = line.split()[5]
                if len(atom_symbol2.split('.')) > 1:
                    atype = atom_symbol2.split('.')[1]
                else:
                    atype = False
                atom_symbol2 = atom_symbol2.split('.')[0]
                if atom_symbol1 in list(amassdict.keys()):
                    atom = atom3D(atom_symbol1, [float(s_line[2]), float(
                        s_line[3]), float(s_line[4])], name=atype)
                elif atom_symbol2 in list(amassdict.keys()):
                    atom = atom3D(atom_symbol2, [float(s_line[2]), float(
                        s_line[3]), float(s_line[4])], name=atype)
                else:
                    print('Cannot find atom symbol in amassdict')
                    sys.exit()
                self.charge += float(s_line[8])
                self.partialcharges.append(float(s_line[8]))
                self.addAtom(atom)
            if '<TRIPOS>ATOM' in line:
                read_atoms = True
            if read_bonds:  # Read in bonds to molecular graph.
                s_line = line.split()
                graph[int(s_line[1]) - 1, int(s_line[2]) - 1] = 1
                graph[int(s_line[2]) - 1, int(s_line[1]) - 1] = 1
                if s_line[3] in ["ar"]:
                    bo_graph[int(s_line[1]) - 1, int(s_line[2]) - 1] = 1.5
                    bo_graph[int(s_line[2]) - 1, int(s_line[1]) - 1] = 1.5
                elif s_line[3] in ["am"]:
                    bo_graph[int(s_line[1]) - 1, int(s_line[2]) - 1] = 1
                    bo_graph[int(s_line[2]) - 1, int(s_line[1]) - 1] = 1
                elif s_line[3] in ["un"]:
                    bo_graph[int(s_line[1]) - 1, int(s_line[2]) - 1] = np.nan
                    bo_graph[int(s_line[2]) - 1, int(s_line[1]) - 1] = np.nan
                else:
                    bo_graph[int(s_line[1]) - 1, int(s_line[2]) - 1] = s_line[3]
                    bo_graph[int(s_line[2]) - 1, int(s_line[1]) - 1] = s_line[3]
                bo_dict[tuple(
                    sorted([int(s_line[1]) - 1, int(s_line[2]) - 1]))] = s_line[3]
            if '<TRIPOS>BOND' in line:
                read_bonds = True
                # Initialize molecular graph.
                graph = np.zeros((self.natoms, self.natoms))
                bo_graph = np.zeros((self.natoms, self.natoms))
                bo_dict = dict()
        if isinstance(graph, np.ndarray):  # Enforce mol2 molecular graph if it exists.
            self.graph = graph
            self.bo_mat = bo_graph
            self.bo_dict = bo_dict
        else:
            self.graph = np.array([])
            self.bo_mat = np.array([])
            self.bo_dict = {}

    @deprecated('Duplicate function will be removed in a future release.'
                'Use readfromxyz(readstring=True) instead.')
    def readfromstring(self, xyzstring):
        """
        Read XYZ from string.

        Parameters
        -------
            xyzstring : string
                String of XYZ file.
        """

        globs = globalvars()
        amassdict = globs.amass()
        self.graph = np.array([])
        s = xyzstring.split('\n')
        try:
            s.remove('')
        except ValueError:
            pass
        s = [f'{val}\n' for val in s]
        for line in s[0:]:
            line_split = line.split()
            if len(line_split) == 4 and line_split[0]:
                # This looks for unique atom IDs in files.
                lm = re.search(r'\d+$', line_split[0])
                # If the string ends in digits m will be a Match object, or None otherwise.
                if lm is not None:
                    symb = re.sub(r'\d+', '', line_split[0])
                    atom = atom3D(symb, [float(line_split[1]), float(line_split[2]), float(line_split[3])],
                                  name=line_split[0])
                elif line_split[0] in list(amassdict.keys()):
                    atom = atom3D(line_split[0], [float(line_split[1]), float(
                        line_split[2]), float(line_split[3])])
                else:
                    print('Cannot find atom type.')
                    sys.exit()
                self.addAtom(atom)

    def readfromtxt(self, txt):
        """
        Read XYZ from textfile.

        Parameters
        -------
            txt : list
                List of lists that comes as a result of readlines.
        """

        globs = globalvars()
        en_dict = globs.endict()
        self.graph = np.array([])
        for line in txt:
            line_split = line.split()
            if len(line_split) == 4 and line_split[0]:
                # This looks for unique atom IDs in files.
                lm = re.search(r'\d+$', line_split[0])
                # If the string ends in digits m will be a Match object, or None otherwise.
                if lm is not None:
                    symb = re.sub(r'\d+', '', line_split[0])
                    atom = atom3D(symb, [float(line_split[1]), float(line_split[2]), float(line_split[3])],
                                  name=line_split[0])
                elif line_split[0] in list(en_dict.keys()):
                    atom = atom3D(line_split[0], [float(line_split[1]), float(
                        line_split[2]), float(line_split[3])])
                else:
                    print('Cannot find atom type.')
                    sys.exit()
                self.addAtom(atom)

    def readfromxyz(self, filename: str, ligand_unique_id=False, read_final_optim_step=False, readstring=False):
        """
        Read XYZ into a mol3D class instance.

        Parameters
        -------
            filename : string
                String of path to XYZ file. Path may be local or global.
            ligand_unique_id : string
                Unique identifier for a ligand. In MR diagnostics, we abstract the atom based graph to a ligand based graph.
                For ligands, they don't have a natural name, so they are named with a UUID. Hard to attribute MR character to
                just atoms, so it is attributed ligands instead.
            read_final_optim_step : boolean
                if there are multiple geometries in the xyz file
                (after an optimization run) use only the last one.
            readstring : boolean
                Flag for deciding whether a string or xyz file is being passed as the filename.
        """

        globs = globalvars()
        amassdict = globs.amass()
        self.graph = np.array([])
        self.xyzfile = filename

        if readstring:
            s = filename.split('\n')
            try:
                s.remove('')
            except ValueError:
                pass
            s = [f'{val}\n' for val in s]
            for line in s[0:]:
                line_split = line.split()
                if len(line_split) == 4 and line_split[0]:
                    # This looks for unique atom IDs in files.
                    lm = re.search(r'\d+$', line_split[0])
                    # If the string ends in digits m will be a Match object, or None otherwise.
                    if lm is not None:
                        symb = re.sub(r'\d+', '', line_split[0])
                        atom = atom3D(symb, [float(line_split[1]), float(line_split[2]), float(line_split[3])],
                                      name=line_split[0])
                    elif line_split[0] in list(amassdict.keys()):
                        atom = atom3D(line_split[0], [float(line_split[1]), float(
                            line_split[2]), float(line_split[3])])
                    else:
                        print('Cannot find atom type.')
                        sys.exit()
                    self.addAtom(atom)
        else:
            with open(filename, 'r') as f:
                s = f.read().splitlines()
            try:
                atom_count = int(s[0])
            except ValueError:
                atom_count = 0
            start = 2
            if read_final_optim_step:
                start = len(s) - int(s[0])
            for line in s[start:start+atom_count]:
                line_split = line.split()
                # If the split line has more than 4 elements, only elements 0 through 3 will be used.
                # This means that it should work with any XYZ file that also stores something like Mulliken charge.
                # Next, this looks for unique atom IDs in files.
                if len(line_split):
                    lm = re.search(r'\d+$', line_split[0])
                    # If the string ends in digits m will be a Match object, or None otherwise.
                    if line_split[0] in list(amassdict.keys()) or ligand_unique_id:
                        atom = atom3D(line_split[0], [float(line_split[1]), float(
                            line_split[2]), float(line_split[3])])
                    elif lm is not None:
                        print(line_split)
                        symb = re.sub(r'\d+', '', line_split[0])
                        atom = atom3D(symb, [float(line_split[1]), float(line_split[2]), float(line_split[3])],
                                      name=line_split[0])
                    else:
                        print('Cannot find atom type.')
                        sys.exit()
                    self.addAtom(atom)

    def reflect_coords(self, metal_coords, lig1_catom_coords, lig2_catom_coords, atoms_to_move):
        """
        Helper function for flip_symmetry to calculate vectors, projections, and update coordinates.

        Parameters
        ----------
            metal_coords: np.array
                Coordinates of metal atom.
            lig1_catom_coords: np.array
                Coordinates of coordinating atom of first ligand to be flipped.
            lig2_catom_coords: np.array
                Coordinates of coordinating atom of second ligand to be flipped.
            atoms_to_move: list
                List of atom indices to be moved.

        Returns
        -------
            self: mol3D
                returns self, a mol3D object with flipped symmetry.
        """

        # Define vector from metal to first coordinating atom of first ligand to be swapped.
        vec1 = lig1_catom_coords - metal_coords
        # Define vector from metal to first coordinating atom of second ligand to be swapped.
        vec2 = lig2_catom_coords - metal_coords
        # Define reflection vector between the two previous vectors and normalize.
        vec_reflect = vec1 / np.linalg.norm(vec1, 2) + vec2 / np.linalg.norm(vec2, 2)
        vec_reflect = vec_reflect / np.linalg.norm(vec_reflect, 2)
        # Define all atoms to be moved, i.e., all atoms in both ligands that will be moved.
        # Move all atoms by flipping coordinates across normalized reflection vector.
        for atom_idx in atoms_to_move:
            vec_atoms = np.array(self.atoms[atom_idx].coords()) - metal_coords
            vec_proj = np.dot(vec_atoms, vec_reflect) * vec_reflect
            reflected_coords = metal_coords + 2 * vec_proj - vec_atoms
            self.atoms[atom_idx].setcoords(reflected_coords)
        return self

    def resetBondOBMol(self):
        """
        Repopulates the bond order matrix via openbabel. Interprets bond order matrix.
        """

        if self.OBMol:
            bo_mat = self.populateBOMatrix()
            self.cleanBonds()
            for i in range(0, self.natoms):
                for j in range(0, self.natoms):
                    if bo_mat[i][j] > 0:
                        self.OBMol.AddBond(i + 1, j + 1, int(bo_mat[i][j]))
        else:
            print("OBmol does not exist.")

    def returnxyz(self, no_tabs=False):
        """
        Print XYZ info of mol3D class instance to stdout. To write to file
        (more common), use writexyz() instead.

        Parameters
        ----------
            no_tabs : bool, optional
                Whether or not to use tabs in coordinate columns.

        Returns
        -------
            ss : string
                String of XYZ information from mol3D class.
        """

        ss = ''
        for atom in self.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        if no_tabs:
            ss = ss.replace('\t', ' ' * 8)
        return ss

    def rmsd(self, mol2):
        """
        Compute the RMSD between two molecules. Does not align molecules.
        For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            rmsd : float
                RMSD between the two structures.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        if (Nat0 != Nat1):
            print(
                "ERROR: RMSD can be calculated only for molecules with the same number of atoms.")
            return float('NaN')
        else:
            rmsd = 0
            for atom0, atom1 in zip(self.getAtoms(), mol2.getAtoms()):
                rmsd += (atom0.distance(atom1)) ** 2
            if Nat0 == 0:
                rmsd = 0
            else:
                rmsd /= Nat0
            rmsd = np.sqrt(rmsd)
            return rmsd

    def rmsd_nonH(self, mol2):
        """
        Compute the RMSD between two molecules, considering heavy atoms only.
        Does not align molecules. For that, use geometry.kabsch().

        Parameters
        ----------
            mol2 : mol3D
                mol3D instance of second molecule.

        Returns
        -------
            rmsd : float
                RMSD between the two structures ignoring hydrogens.
        """

        Nat0 = self.natoms
        Nat1 = mol2.natoms
        if (Nat0 != Nat1):
            print(
                "ERROR: RMSD can be calculated only for molecules with the same number of atoms.")
            return float('NaN')
        else:
            rmsd = 0
            for atom0, atom1 in zip(self.getAtoms(), mol2.getAtoms()):
                if (not atom0.sym == 'H') and (not atom1.sym == 'H'):
                    rmsd += (atom0.distance(atom1)) ** 2
            rmsd /= Nat0
            rmsd = np.sqrt(rmsd)
            return rmsd

    def roland_combine(self, mol, catoms, bond_to_add=[], dirty=False):
        """
        Combines two molecules. Each atom in the second molecule
        is appended to the first while preserving orders. Assumes
        operation with a given mol3D instance, when handed a second mol3D instance.

        Parameters
        ----------
            mol : mol3D
                mol3D class instance containing molecule to be added.
            catoms : TODO
                TODO
            bond_to_add : list, optional
                List of tuples (ind1,ind2,order) bonds to add. Default is empty.
            dirty : bool, optional
                Add atoms without worrying about bond orders. Default is False.

        Returns
        -------
            cmol : mol3D
                New mol3D class containing the two molecules combined.
        """

        cmol = self
        bo_dict = cmol.bo_dict

        print('lig_dict')
        print(mol.bo_dict)

        if cmol.bo_dict == False:
            # Only central metal
            bo_dict = {}
        new_bo_dict = copy.deepcopy(bo_dict)

        # Add ligand connections.
        for bo in mol.bo_dict:
            ind1 = bo[0] + len(cmol.atoms)
            ind2 = bo[1] + len(cmol.atoms)
            new_bo_dict[(ind1,ind2)]=mol.bo_dict[(bo[0],bo[1])]

        # Connect metal to ligand.
        metal_ind = cmol.findMetal(transition_metals_only=False)[0]
        for atom in catoms:
            ind1 = metal_ind
            ind2 = atom + len(cmol.atoms)
            new_bo_dict[(ind1,ind2)]=1

        for atom in mol.atoms:
            cmol.addAtom(atom, auto_populate_bo_dict = False)

        cmol.bo_dict = new_bo_dict
        bo_mat = np.zeros((cmol.natoms, cmol.natoms))
        for k, v in new_bo_dict.items():
            bo_mat[k[0], k[1]] = v
            bo_mat[k[1], k[0]] = v
        cmol.bo_mat = bo_mat
        cmol.graph = (cmol.bo_mat > 0).astype(int)

        return cmol

    def sanitycheck(self, silence=False, debug=False):
        """
        Sanity check a molecule for overlap within the molecule.

        Parameters
        ----------
            silence : bool
                Flag for printing warnings. Default is False.
            debug : bool
                Flag for extra printout. Default is False.

        Returns
        -------
            overlap : bool
                Flag for whether two structures overlap. True for overlap.
            mind : float
                Minimum distance between atoms in molecule.
        """

        overlap = False
        mind = 1000
        errors_dict = {}
        for ii, atom1 in enumerate(self.atoms):
            for jj, atom0 in enumerate(self.atoms):
                if jj > ii:
                    if atom1.ismetal() or atom0.ismetal():
                        cutoff = 0.6
                    elif (atom0.sym in ['N', 'O'] and atom1.sym == 'H') or (atom1.sym in ['N', 'O'] and atom0.sym == 'H'):
                        cutoff = 0.6
                    else:
                        cutoff = 0.65
                    if distance(atom1.coords(), atom0.coords()) < cutoff * (atom1.rad + atom0.rad):
                        overlap = True
                        norm = distance(
                            atom1.coords(), atom0.coords())/(atom1.rad+atom0.rad)
                        errors_dict.update(
                            {f'{atom1.sym}{ii}-{atom0.sym}{jj}_normdist': norm})
                        if distance(atom1.coords(), atom0.coords()) < mind:
                            mind = distance(atom1.coords(), atom0.coords())
                        if not (silence):
                            print("#############################################################")
                            print("Molecules might be overlapping. Increase distance!")
                            print("#############################################################")
        if debug:
            return overlap, mind, errors_dict
        else:
            return overlap, mind

    def sanitycheckCSD(self, oct=False, angle1=30, angle2=80, angle3=45, debug=False, metals=None):
        """
        Sanity check a CSD molecule.
        Check that the molecule passes basic angle tests in line with CSD pulls.

        Parameters
        ----------
            oct : bool, optional
                Flag for octahedral test. Default is False.
            angle1 : float, optional
                Metal angle cutoff. Default is 30.
            angle2 : float, optional
                Organic angle cutoff. Default is 80.
            angle3 : float, optional
                Metal/organic angle cutoff e.g. M-X-X angle. Default is 45.
            debug : bool, optional
                Extra print out desired. Default is False.
            metals : Nonetype, optional
                Check for metals. Default is None.

        Returns
        -------
            sane : bool
                Whether or not molecule is a sane molecule.
            error_dict : dict
                Returned if debug, {bondidists and angles breaking constraints:values}
        """

        import itertools
        if metals:
            metalinds = [i for i, x in enumerate(
                self.symvect()) if x in metals]
        else:
            metalinds = self.findMetal()
        mcons = []
        metal_syms = []
        if len(metalinds):  # Only if there are metals.
            for metal in metalinds:
                metalcons = self.getBondedAtomsSmart(metal, oct=oct)
                mcons.append(metalcons)
                metal_syms.append(self.symvect()[metal])
        overlap, _, errors_dict = self.sanitycheck(silence=True, debug=True)
        heavy_atoms = [i for i, x in enumerate(self.symvect()) if (
            x != 'H') and (x not in metal_syms)]
        sane = not overlap
        for i, metal in enumerate(metalinds):  # Check metal center angles.
            if len(mcons[i]) > 1:
                combos = itertools.combinations(mcons[i], 2)
                for combo in combos:
                    if self.getAngle(combo[0], metal, combo[1]) < angle1:
                        sane = False
                        label = f'{self.atoms[combo[0]].sym}{combo[0]}-' + \
                            f'{self.atoms[metal].sym}{metal}-' + \
                            f'{self.atoms[combo[1]].sym}{combo[1]}_angle'
                        angle = self.getAngle(combo[0], metal, combo[1])
                        errors_dict.update({label: angle})
        for indx in heavy_atoms:  # Check heavy atom angles.
            if len(self.getBondedAtomsSmart(indx, oct=oct)) > 1:
                combos = itertools.combinations(
                    self.getBondedAtomsSmart(indx), 2)
                for combo in combos:
                    # Any metals involved in the bond, but not the metal center.
                    if any([True for x in combo if self.atoms[x].ismetal()]):
                        cutoff = angle3
                    else:  # Only organic/ligand bonds.
                        cutoff = angle2
                    if self.getAngle(combo[0], indx, combo[1]) < cutoff:
                        sane = False
                        label = f'{self.atoms[combo[0]].sym}{combo[0]}-' + \
                            f'{self.atoms[indx].sym}{indx}-' + \
                            f'{self.atoms[combo[1]].sym}{combo[1]}_angle'
                        angle = self.getAngle(combo[0], indx, combo[1])
                        errors_dict.update({label: angle})
        if debug:
            return sane, errors_dict
        else:
            return sane

    def setLoc(self, loc):
        """
        Sets the conformation of an amino acid in the chain of a protein.

        Parameters
        ----------
            loc : str
                A one-character string representing the conformation.
        """

        self.loc = loc

    def symvect(self):
        """
        Method to obtain array of symbol vector of molecule.

        Returns
        -------
            symbol_vector : np.array
                1 dimensional numpy array of atom symbols.
                (N,) dimension, N is number of atoms.
        """

        symbol_vector = []
        for atom in self.atoms:
            symbol_vector.append(atom.sym)
        symbol_vector = np.array(symbol_vector)
        return symbol_vector

    def translate(self, dxyz):
        """
        Translate all atoms by a given vector.

        Parameters
        ----------
            dxyz : list
                Vector to translate all molecules, as a list [dx, dy, dz].
        """

        for atom in self.atoms:
            atom.translate(dxyz)

    def typevect(self):
        """
        Method to obtain array of type vector of molecule.

        Returns
        -------
            type_vector : np.array
                1 dimensional numpy array of atom types (by name).
                (N,) dimension, N is number of atoms.
        """

        type_vector = []
        for atom in self.atoms:
            type_vector.append(atom.name)
        type_vector = np.array(type_vector)
        return type_vector

    def writegxyz(self, filename):
        """
        Write GAMESS XYZ file.

        Parameters
        ----------
            filename : str
                Path to XYZ file.
        """

        ss = ''  # initialize returning string
        ss += "Date:" + time.strftime(
            '%m/%d/%Y %H:%M') + f", XYZ structure generated by mol3D Class, {self.globs.PROGRAM}\nC1\n"
        for atom in self.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{float(atom.atno):.1f}\t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        fname = filename.split('.gxyz')[0]
        with open(fname + '.gxyz', 'w') as f:
            f.write(ss)

    def writemol(self, filename):
        """
        Write mol file from mol3D object.
        Not advised if molecule has > 99 atoms.
        If there is no bond order information available,
        all bonds will be set as single bonds.

        Parameters
        ----------
            filename : str
                Path to mol file.
        """

        if not len(self.graph):
            # Set self.graph.
            self.createMolecularGraph()
        num_atoms = self.natoms
        num_bonds = int(np.count_nonzero(self.graph) / 2)

        mol_contents = [
        '',
        'Generated with molSimplify',
        '',
        f' {num_atoms} {num_bonds}  0  0  0  0  0  0  0  0999 V2000'
        ]

        # Atom section
        coords, syms = self.get_coordinate_array(), self.get_element_list()
        for coord, sym in zip(coords, syms):
            s = f' {coord[0]:9.4f} {coord[1]:9.4f} {coord[2]:9.4f} {sym.ljust(2)}  0  0  0  0  0  0  0  0  0  0  0  0'
            mol_contents.append(s)

        # Bond section
        # .mol files use 1 indexing.
        # Use bond order information if available
        # (self.bo_dict or self.bo_mat).
        if len(self.bo_dict) != 0:
            # If self.bo_dict is set, use that.
            bo_dict_keys = list(self.bo_dict.keys())
            bo_dict_keys.sort()
            for k in bo_dict_keys:
                v = self.bo_dict[k]
                s = f' {k[0]+1:2.0f} {k[1]+1:2.0f}  {v}  0  0  0  0'
                mol_contents.append(s)
        elif self.bo_mat.size != 0:
            # Only self.bo_mat is set, not self.bo_dict.
            rows, cols = np.nonzero(np.triu(self.bo_mat))
            for i, j in zip(rows, cols):
                s = f' {i+1:2.0f} {j+1:2.0f}  {int(self.bo_mat[i][j])}  0  0  0  0'
                mol_contents.append(s)
        else:
            # Make all bond orders be one.
            # Use triu since we only care about bonding pairs
            # where i < j.
            rows, cols = np.nonzero(np.triu(self.graph))
            for i, j in zip(rows, cols):
                s = f' {i+1:2.0f} {j+1:2.0f}  1  0  0  0  0'
                mol_contents.append(s)

        mol_contents.extend(['M  END', ''])
        mol_contents = '\n'.join(mol_contents)

        with open(filename, 'w') as f:
            f.write(mol_contents)

    def new_writemol2(
        self,
        ignore_dummy_atoms=True,
        write_bond_orders=True,
        return_string=True,
        output_file=None
    ):
        """
        Generate a MOL2-format string or file from atomic coordinates and bonding data.

        Parameters
        ----------
        atom_coords : list or np.ndarray of shape (N, 3)
            A list or NumPy array of atomic coordinates. Each element is a 3D coordinate
            (x, y, z) for a single atom.

        atom_elements : list of str
            A list of atomic element symbols (e.g., 'C', 'N', 'O', etc.), one for each atom
            in `atom_coords`. The list must be the same length as `atom_coords`.

        bond_order_dict : dict
            A dictionary mapping tuples of atom indices (i, j) to bond orders. The bond order
            may be a string like '1', '2', '3', 'ar', etc.
            Example: {(0, 1): '1', (1, 2): '2'}

        ignore_dummy_atoms : bool, optional (default=True)
            If True, atoms with element symbol 'X' will be ignored in both atoms and bonds.

        write_bond_orders : bool, optional (default=True)
            If True, writes the actual bond orders from `bond_order_dict`.
            If False, all bonds are assigned order '1'.

        return_string : bool, optional (default=True)
            If True, returns the MOL2 content as a string.
            If False, writes to `output_file`.

        output_file : str or None, optional
            If `return_string` is False, this must be the path to the file to write.

        Returns
        -------
        str or None
            Returns the MOL2-format string if `return_string` is True, otherwise writes to file
            and returns None.

        Notes
        -----
        - Atoms are renumbered starting from 1.
        - Element-based labels (e.g., C1, C2) are assigned using counts per element.
        - Substructures are inferred using connected components in the bond graph.
        - Only bonds where both atoms are not dummy atoms are retained if `ignore_dummy_atoms` is True.
        """
        # Filter out dummy atoms
        filtered_atoms = []
        index_map = {}
        counter_by_element = {}
        new_index = 1

        # get the atoms
        atom_coords = []
        atom_elements = []
        for atom in self.atoms:
            atom_coords.append(atom.coords())
            atom_elements.append(atom.sym)

        # get bond_order dictionary
        bond_order_dict = self.bo_dict

        for i, (coord, elem) in enumerate(zip(atom_coords, atom_elements)):
            if ignore_dummy_atoms and elem.upper() == 'X':
                continue
            elem_clean = elem.capitalize()
            counter_by_element.setdefault(elem_clean, 0)
            counter_by_element[elem_clean] += 1
            atom_label = f"{elem_clean}{counter_by_element[elem_clean]}"
            filtered_atoms.append((new_index, atom_label, coord, elem_clean))
            index_map[i] = new_index
            new_index += 1

        # Rebuild bond list using new indices
        bonds = []
        for (i, j), order in bond_order_dict.items():
            if i in index_map and j in index_map:
                idx1 = index_map[i]
                idx2 = index_map[j]
                bond_type = order if write_bond_orders else '1'
                bonds.append((idx1, idx2, bond_type))

        # Determine substructures using NetworkX
        G = nx.Graph()
        G.add_nodes_from([idx for idx, _, _, _ in filtered_atoms])
        G.add_edges_from([(i, j) for i, j, _ in bonds])
        components = list(nx.connected_components(G))
        substructure_lookup = {}
        for idx, comp in enumerate(components, start=1):
            for atom_idx in comp:
                substructure_lookup[atom_idx] = idx

        # Compose mol2 content
        mol2_lines = []
        mol2_lines.append("@<TRIPOS>MOLECULE")
        mol2_lines.append("GeneratedMol")
        mol2_lines.append(f"{len(filtered_atoms)} {len(bonds)} 1")
        mol2_lines.append("SMALL")
        mol2_lines.append("NO_CHARGES\n")

        mol2_lines.append("@<TRIPOS>ATOM")
        for idx, label, coord, elem in filtered_atoms:
            mol2_lines.append(f"{idx:<5d} {label:<6s} {coord[0]:>10.4f} {coord[1]:>10.4f} {coord[2]:>10.4f} {elem:<4s} {substructure_lookup[idx]:>2d} RES{substructure_lookup[idx]} 0.0000")

        mol2_lines.append("@<TRIPOS>BOND")
        for i, (idx1, idx2, bond_type) in enumerate(bonds, start=1):
            mol2_lines.append(f"{i:<5d} {idx1:<4d} {idx2:<4d} {bond_type}")

        mol2_lines.append("@<TRIPOS>SUBSTRUCTURE")
        for sub_id in sorted(set(substructure_lookup.values())):
            mol2_lines.append(f"{sub_id:<3d} RES{sub_id}       1 TEMP              0 ****  ****    0 ROOT")

        mol2_str = '\n'.join(mol2_lines)

        if return_string:
            return mol2_str
        elif output_file:
            with open(output_file, 'w') as f:
                f.write(mol2_str)
        else:
            raise ValueError("Must specify either return_string=True or output_file='filename.mol2'")

    def writemol2(self, filename, writestring=False, ignoreX=False, force=False):
        """
        Write mol2 file from mol3D object. Partial charges are appended if given.
        Else, total charge of the complex (given or interpreted by OBMol) is assigned
        to the metal.

        Parameters
        ----------
            filename : str
                Path to mol2 file.
            writestring : bool, optional
                Flag to write to a string if True or file if False. Default is False.
            ignoreX : bool, optional
                Flag to delete atom X. Default is False.
            force : bool, optional
                Flag to dictate if bond orders are written (obmol/assigned) or =1.
        """

        from scipy.sparse import csgraph
        if ignoreX:
            for i, atom in enumerate(self.atoms):
                if atom.sym == 'X':
                    self.deleteatom(i)
        if not len(self.graph):
            self.createMolecularGraph()
        if not self.bo_dict and not force:
            self.convert2OBMol2()
        csg = csgraph.csgraph_from_dense(self.graph)
        disjoint_components = csgraph.connected_components(csg)
        if disjoint_components[0] > 1:
            atom_group_names = [f'RES{x+1}' for x in disjoint_components[1]]
            atom_groups = [str(x+1) for x in disjoint_components[1]]
        else:
            atom_group_names = ['RES1']*self.natoms
            atom_groups = [str(1)]*self.natoms
        atom_types = list(set(self.symvect()))
        atom_type_numbers = np.ones(len(atom_types))
        atom_types_mol2 = []
        try:
            metal_ind = self.findMetal()[0]
        except IndexError:
            metal_ind = 0
        if len(self.partialcharges):
            charges = self.partialcharges
            charge_string = 'PartialCharges'
        elif self.charge:  # Assign total charge to metal.
            charges = np.zeros(self.natoms)
            charges[metal_ind] = self.charge
            charge_string = 'UserTotalCharge'
        else:  # Calculate total charge with OBMol, assign to metal.
            if self.OBMol:
                charges = np.zeros(self.natoms)
                charges[metal_ind] = self.OBMol.GetTotalCharge()
                charge_string = 'OBmolTotalCharge'
            else:
                charges = np.zeros(self.natoms)
                charge_string = 'ZeroCharges'
        ss = f'@<TRIPOS>MOLECULE\n{filename}\n'
        ss += f'{self.natoms}\t{int(csg.nnz/2)}\t{disjoint_components[0]}\n'
        ss += 'SMALL\n'
        ss += charge_string + '\n' + '****\n' + 'Generated from molSimplify\n\n'
        ss += '@<TRIPOS>ATOM\n'
        atom_default_dict = {'C': '3', 'N': '3', 'O': '2', 'S': '3', 'P': '3'}
        for i, atom in enumerate(self.atoms):
            if atom.name != atom.sym:
                atom_types_mol2 = '.'+atom.name
            elif atom.sym in list(atom_default_dict.keys()):
                atom_types_mol2 = '.' + atom_default_dict[atom.sym]
            else:
                atom_types_mol2 = ''
            type_ind = atom_types.index(atom.sym)
            atom_coords = atom.coords()
            ss += f'{i+1} {atom.sym}{int(atom_type_numbers[type_ind])}\t' + \
                f'{atom_coords[0]}  {atom_coords[1]}  {atom_coords[2]} ' + \
                f'{atom.sym}{atom_types_mol2}\t{atom_groups[i]}' + \
                f' {atom_group_names[i]} {charges[i]}\n'
            atom_type_numbers[type_ind] += 1
        ss += '@<TRIPOS>BOND\n'
        bonds = csg.nonzero()
        bond_count = 1
        if self.bo_dict:
            bondorders = True
        else:
            bondorders = False
        for i, b1 in enumerate(bonds[0]):
            b2 = bonds[1][i]
            if b2 > b1 and not bondorders:
                ss += f'{bond_count} {b1+1} {b2+1} 1\n'
                bond_count += 1
            elif b2 > b1 and bondorders:
                ss += f'{bond_count} {b1+1} {b2+1} {self.bo_dict[(int(b1), int(b2))]}\n'
        ss += '@<TRIPOS>SUBSTRUCTURE\n'
        unique_group_names = np.unique(atom_group_names)
        for i, name in enumerate(unique_group_names):
            ss += f'{i+1} {name} {atom_group_names.count(name)}\n'
        ss += '\n'
        if writestring:
            return ss
        else:
            if '.mol2' not in filename:
                if '.' not in filename:
                    filename += '.mol2'
                else:
                    filename = filename.split('.')[0]+'.mol2'
            with open(filename, 'w') as file1:
                file1.write(ss)

    def writemol2_bodict(
            self,
            ignore_dummy_atoms=True,
            write_bond_orders=True,
            return_string=True,
            output_file=None
        ):
        """
        Generate a MOL2-format string or file from atomic coordinates and bonding data.

        Parameters
        ----------
            atom_coords : list or np.ndarray of shape (N, 3)
                A list or NumPy array of atomic coordinates. Each element is a 3D coordinate
                (x, y, z) for a single atom.
            atom_elements : list of str
                A list of atomic element symbols (e.g., 'C', 'N', 'O', etc.), one for each atom
                in `atom_coords`. The list must be the same length as `atom_coords`.
            bond_order_dict : dict
                A dictionary mapping tuples of atom indices (i, j) to bond orders. The bond order
                may be a string like '1', '2', '3', 'ar', etc.
                Example: {(0, 1): '1', (1, 2): '2'}
            ignore_dummy_atoms : bool, optional (default=True)
                If True, atoms with element symbol 'X' will be ignored in both atoms and bonds.
            write_bond_orders : bool, optional (default=True)
                If True, writes the actual bond orders from `bond_order_dict`.
                If False, all bonds are assigned order '1'.
            return_string : bool, optional (default=True)
                If True, returns the MOL2 content as a string.
                If False, writes to `output_file`.
            output_file : str or None, optional
                If `return_string` is False, this must be the path to the file to write.

        Returns
        -------
            str or None
                Returns the MOL2-format string if `return_string` is True, otherwise writes to file
                and returns None.

        Notes
        -----
            - Atoms are renumbered starting from 1.
            - Element-based labels (e.g., C1, C2) are assigned using counts per element.
            - Substructures are inferred using connected components in the bond graph.
            - Only bonds where both atoms are not dummy atoms are retained if `ignore_dummy_atoms` is True.
        """

        # Filter out dummy atoms
        filtered_atoms = []
        index_map = {}
        counter_by_element = {}
        new_index = 1

        # get the atoms
        atom_coords = []
        atom_elements = []
        for atom in self.atoms:
            atom_coords.append(atom.coords())
            atom_elements.append(atom.sym)

        # get bond_order dictionary
        bond_order_dict = self.bo_dict

        for i, (coord, elem) in enumerate(zip(atom_coords, atom_elements)):
            if ignore_dummy_atoms and elem.upper() == 'X':
                continue
            elem_clean = elem.capitalize()
            counter_by_element.setdefault(elem_clean, 0)
            counter_by_element[elem_clean] += 1
            atom_label = f"{elem_clean}{counter_by_element[elem_clean]}"
            filtered_atoms.append((new_index, atom_label, coord, elem_clean))
            index_map[i] = new_index
            new_index += 1

        # Rebuild bond list using new indices
        bonds = []
        for (i, j), order in bond_order_dict.items():
            if i in index_map and j in index_map:
                idx1 = index_map[i]
                idx2 = index_map[j]
                bond_type = order if write_bond_orders else '1'
                bonds.append((idx1, idx2, bond_type))

        # Determine substructures using NetworkX
        G = nx.Graph()
        G.add_nodes_from([idx for idx, _, _, _ in filtered_atoms])
        G.add_edges_from([(i, j) for i, j, _ in bonds])
        components = list(nx.connected_components(G))
        substructure_lookup = {}
        for idx, comp in enumerate(components, start=1):
            for atom_idx in comp:
                substructure_lookup[atom_idx] = idx

        # Compose mol2 content
        mol2_lines = []
        mol2_lines.append("@<TRIPOS>MOLECULE")
        mol2_lines.append("GeneratedMol")
        mol2_lines.append(f"{len(filtered_atoms)} {len(bonds)} 1")
        mol2_lines.append("SMALL")
        mol2_lines.append("NO_CHARGES\n")

        mol2_lines.append("@<TRIPOS>ATOM")
        for idx, label, coord, elem in filtered_atoms:
            mol2_lines.append(f"{idx:<5d} {label:<6s} {coord[0]:>10.4f} {coord[1]:>10.4f} {coord[2]:>10.4f} {elem:<4s} {substructure_lookup[idx]:>2d} RES{substructure_lookup[idx]} 0.0000")

        mol2_lines.append("@<TRIPOS>BOND")
        for i, (idx1, idx2, bond_type) in enumerate(bonds, start=1):
            mol2_lines.append(f"{i:<5d} {idx1:<4d} {idx2:<4d} {bond_type}")

        mol2_lines.append("@<TRIPOS>SUBSTRUCTURE")
        for sub_id in sorted(set(substructure_lookup.values())):
            mol2_lines.append(f"{sub_id:<3d} RES{sub_id}       1 TEMP              0 ****  ****    0 ROOT")

        mol2_str = '\n'.join(mol2_lines)

        if return_string:
            return mol2_str
        elif output_file:
            with open(output_file, 'w') as f:
                f.write(mol2_str)
        else:
            raise ValueError("Must specify either return_string=True or output_file='filename.mol2'")

    def writemxyz(self, mol, filename, no_tabs=False):
        """
        Write standard XYZ file with two molecules.

        Parameters
        ----------
            mol : mol3D
                mol3D instance of second molecule.
            filename : str
                Path to XYZ file.
            no_tabs : bool, optional
                Whether or not to use tabs in coordinate columns.
        """

        ss = ''  # initialize returning string
        ss += f'{self.natoms + mol.natoms}\n' + time.strftime(
            '%m/%d/%Y %H:%M') + f', XYZ structure generated by mol3D Class, {self.globs.PROGRAM}\n'
        for atom in self.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        for atom in mol.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        if no_tabs:
            ss = ss.replace('\t', ' ' * 8)
        fname = filename.split('.xyz')[0]
        with open(fname + '.xyz', 'w') as f:
            f.write(ss)

    def writenumberedxyz(self, filename):
        """
        Write standard XYZ file with numbers instead of symbols.

        Parameters
        ----------
            filename : str
                Path to XYZ file.
        """

        ss = ''  # Initialize returning string.
        ss += f'{self.natoms}\n' + time.strftime(
            '%m/%d/%Y %H:%M') + f', XYZ structure generated by mol3D Class, {self.globs.PROGRAM}\n'
        unique_types = dict()

        for atom in self.atoms:
            this_sym = atom.symbol()
            if this_sym not in list(unique_types.keys()):
                unique_types.update({this_sym: 1})
            else:
                unique_types.update({this_sym: unique_types[this_sym] + 1})
            atom_name = f'{atom.symbol()}{unique_types[this_sym]}'
            xyz = atom.coords()
            ss += f"{atom_name} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        fname = filename.split('.xyz')[0]
        with open(fname + '.xyz', 'w') as f:
            f.write(ss)

    def writesepxyz(self, mol, filename):
        """
        Write standard XYZ file with two molecules separated.

        Parameters
        ----------
            mol : mol3D
                mol3D instance of second molecule.
            filename : str
                Path to XYZ file.
        """

        ss = ''  # Initialize returning string.
        ss += f'{self.natoms}\n' + time.strftime(
            '%m/%d/%Y %H:%M') + f', XYZ structure generated by mol3D Class, {self.globs.PROGRAM}\n'
        for atom in self.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        ss += f'--\n{mol.natoms}\n\n'
        for atom in mol.atoms:
            xyz = atom.coords()
            ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        fname = filename.split('.xyz')[0]
        with open(fname + '.xyz', 'w') as f:
            f.write(ss)

    def writexyz(self, filename, symbsonly=True, ignoreX=False,
                 ordering=False, writestring=False, withgraph=False,
                 specialheader=False, no_tabs=False):
        """
        Write standard XYZ file.

        Parameters
        ----------
            filename : str
                Path to XYZ file.
            symbsonly : bool, optional
                Only write symbols to file. Default is True.
            ignoreX : bool, optional
                Ignore X element when writing. Default is False.
            ordering : bool, optional
                If handed a list, will order atoms in a specific order. Default is False.
            writestring : bool, optional
                Flag to write to a string if True or file if False. Default is False.
            withgraph : bool, optional
                Flag to write with graph (after XYZ) if True. Default is False.
                If True, sparse graph written. All bonds indicated as single.
            specialheader : str, optional
                String to write information into header. Default is False. If True, a special string is written.
            no_tabs : bool, optional
                Whether or not to use tabs in coordinate columns.

        Returns
        -------
            ss : str
                XYZ contents, if writestring is True.
        """

        ss = ''  # Initialize returning string.
        natoms = self.natoms
        if not ordering:
            ordering = list(range(natoms))
        if ignoreX:
            natoms -= sum([1 for i in self.atoms if i.sym == "X"])

        if specialheader:
            ss += f'{natoms}\n'
            ss += f'{specialheader}\n'
        else:
            ss += f'{natoms}\n' + time.strftime(
                '%m/%d/%Y %H:%M') + f', XYZ structure generated by mol3D Class, {self.globs.PROGRAM}\n'
        for ii in ordering:
            atom = self.getAtom(ii)
            if not (ignoreX and atom.sym == 'X'):
                xyz = atom.coords()
                if symbsonly:
                    ss += f"{atom.sym} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
                else:
                    ss += f"{atom.name} \t{xyz[0]:.6f}\t{xyz[1]:.6f}\t{xyz[2]:.6f}\n"
        if withgraph:
            from scipy.sparse import csgraph

            if not len(self.graph):
                self.createMolecularGraph()

            csg = csgraph.csgraph_from_dense(self.graph)
            x, y = csg.nonzero()
            tempstr = ''
            for row1, row2 in zip(x, y):
                tempstr += str(row1).rjust(4)
                tempstr += str(row2).rjust(5)
                tempstr += ' S\n' # Indicate all bonds as single.
            ss += tempstr

        if no_tabs:
            ss = ss.replace('\t', ' ' * 8)

        if writestring:
            return ss
        else:
            fname = filename.split('.xyz')[0]
            with open(fname + '.xyz', 'w') as f:
                f.write(ss)
