# @file nn_prep.py
#  Helper routines for ANN integration
#
#   Written by JP Janet for HJK Group
#
#  Dpt of Chemical Engineering, MIT

from typing import List, Tuple, Union, Dict, Any
from molSimplify.Scripts.io import lig_load
from molSimplify.Informatics.decoration_manager import decorate_molecule
from molSimplify.Informatics.graph_analyze import (get_lig_EN,
                                                   get_truncated_kier)
from molSimplify.python_nn.ANN import (find_eu_dist,
                                       simple_hs_ann,
                                       simple_ls_ann,
                                       simple_slope_ann,
                                       simple_splitting_ann)


def get_bond_order(OBMol, connection_atoms, mol) -> int:
    # informs the ANN of the highest bond order in ligand
    # INPUT:
    #   - OBMol:  OBMol class ligand
    # OUTPUT:
    #   - max_bo: int, max bond order

    bond_order_pairs = []

    OBMol.PerceiveBondOrders()
    for atoms in connection_atoms:
        this_neighbourhood = mol.getBondedAtoms(atoms)
        for items in this_neighbourhood:
            bond_order_pairs.append(tuple([atoms, items]))

    max_bo = 0
    for index_pairs in bond_order_pairs:
        this_bond = OBMol.GetBond(int(index_pairs[0]+1), int(index_pairs[1]+1))
        if this_bond.IsAromatic():
            this_BO = int(2)
        else:
            this_BO = int(this_bond.GetBondOrder())
        if this_BO > max_bo:
            max_bo = this_BO
    return max_bo


def check_ligands(ligs, batlist, dents, tcats):
    # tests if ligand combination
    # is compatiable with the ANN
    # INPUT:
    #   - ligs:  list of mol3D class, ligands
    #   - batlist: list of int, occupations
    #   - dents: list of int, denticity
    #   - tcats: list of int/bool
    # OUTPUT:
    #   - valid: bool
    # tcats controls
    # manual overide
    # of connection atoms

    n_ligs = len(ligs)
    axial_ind_list = []
    equatorial_ind_list = []
    axial_ligs = []
    equatorial_ligs = []
    ax_dent = 0
    eq_dent = 0
    eq_tcat = False
    ax_tcat = False
    valid = True
    if (set(dents) == set([2])):
        print('triple bidentate case\n')
        unique_ligs = []
        ucats = []
        if not (n_ligs) == 3:
            # something unexpected happened!
            valid = False
        for i in range(0, n_ligs):
            this_lig = ligs[i]
            this_dent = dents[i]
            # multiple points
            if not (this_lig in unique_ligs):
                unique_ligs.append(this_lig)
                ucats.append(tcats[i])
            elif (this_lig in unique_ligs) and not (this_lig in equatorial_ligs):
                equatorial_ligs.append(this_lig)
                eq_dent = this_dent
                eq_tcat = tcats[i]
        if len(unique_ligs) == 1:
            axial_ligs.append(equatorial_ligs[0])
            ax_dent = 2
            ax_tcat = eq_tcat
        elif len(unique_ligs) == 2:
            for i, uligs in enumerate(unique_ligs):
                if not (uligs in equatorial_ligs):  # only occurred once
                    axial_ligs.append(uligs)
                    ax_dent = 2
                    ax_tcat = ucats[i]
        else:
            valid = False
    else:
        for i in range(0, n_ligs):
            this_bat = batlist[i]
            this_lig = ligs[i]
            this_dent = dents[i]
            # multiple points
            if len(this_bat) == 1:
                if (5 in this_bat) or (6 in this_bat):
                    if not (this_lig in axial_ligs):
                        axial_ligs.append(this_lig)
                        ax_dent = this_dent
                        ax_tcat = tcats[i]
                else:
                    if not (this_lig in equatorial_ligs):
                        equatorial_ligs.append(this_lig)
                        eq_dent = this_dent
                        eq_tcat = tcats[i]
            else:
                if not (this_lig in equatorial_ligs):
                    equatorial_ligs.append(this_lig)
                    eq_dent = this_dent
                    eq_tcat = tcats[i]
    if not (len(axial_ligs) == 1):
        print(('axial ligs mismatch: ', axial_ligs, ax_dent))
        valid = False
    if not (len(equatorial_ligs) == 1):
        print(('equatorial ligs mismatch: ', equatorial_ligs, eq_dent))
        valid = False
    if valid:  # get the index position in ligs
        axial_ind_list = [ligs.index(ax_lig) for ax_lig in axial_ligs]
        equatorial_ind_list = [ligs.index(eq_lig)
                               for eq_lig in equatorial_ligs]
    return valid, axial_ligs, equatorial_ligs, ax_dent, eq_dent, ax_tcat, eq_tcat, axial_ind_list, equatorial_ind_list


def check_metal(metal: str, oxidation_state: str) -> Tuple[bool, str]:
    supported_metal_dict = {"fe": [2, 3], "mn": [2, 3], "cr": [2, 3],
                            "co": [2, 3], "ni": [2]}
    romans = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6'}
    if oxidation_state in list(romans.keys()):
        oxidation_state = romans[oxidation_state]
    outcome = False
    if metal in list(supported_metal_dict.keys()):
        if int(oxidation_state) in supported_metal_dict[metal]:
            outcome = True
    return outcome, oxidation_state


def get_con_at_type(mol, connection_atoms: List[Union[int, str]]) -> Tuple[bool, str]:
    this_type = ""
    been_set = False
    valid = True
    # test if the ligand is pi-bonded
    if 'pi' in connection_atoms:
        print('ANN cannot handle Pi bonding (yet)')
        valid = False
        this_type = 'pi'
    else:
        for atoms in connection_atoms:
            this_symbol = mol.getAtom(atoms).symbol()
            if not (this_symbol == this_type):
                if been_set:
                    print('different connection atoms in one ligand')
                    valid = False
                else:
                    this_type = this_symbol
                    # RM 2022/08/10: added this because I assume this was the
                    # original intention to avoid multidentate ligands with
                    # connecting atoms of different types. Otherwise I have no
                    # idea what 'been_set' was intended for (previously unused)
                    been_set = True

        if this_type not in ['C', 'O', 'Cl', 'N', 'S']:
            valid = False
            print(('untrained atom type: ', this_type))
    return valid, this_type


def ANN_preproc(args, ligs: List[str], occs: List[int], dents: List[int],
                batslist: List[List[int]], tcats: List[List[Union[int, str]]],
                licores: dict) -> Tuple[bool, str, dict]:
    # prepares and runs ANN calculation

    ######################
    ANN_reason = ''  # holder for reason to reject ANN call
    ANN_attributes: Dict[str, Any] = {}
    ######################

    nn_excitation = []
    emsg = []
    valid = True
    metal = args.core
    spin = args.spin
    # Set default oxidation state variables
    ox = 0
    this_metal = metal.lower()
    if len(this_metal) > 2:
        this_metal = this_metal[0:2]
    newligs = []
    newcats = []
    newdents = []
    newdecs = [False]*6
    newdec_inds = [[0]]*6
    ANN_trust = ''
    count = -1
    for i, lig in enumerate(ligs):
        this_occ = occs[i]
        for j in range(0, int(this_occ)):
            count += 1
            newligs.append(lig)
            newdents.append(dents[i])
            newcats.append(tcats[i])
            if args.decoration:
                newdecs[count] = (args.decoration[i])
                newdec_inds[count] = (args.decoration_index[i])

    ligs = newligs
    dents = newdents
    tcats = newcats

    if not args.geometry == "oct":
        valid = False
        ANN_reason = 'geometry not oct'
    if not args.oxstate:
        emsg.append("\n oxidation state must be given")
        valid = False
        ANN_reason = 'oxstate not given'
    if not valid:
        return valid, ANN_reason, ANN_attributes

    oxidation_state = args.oxstate
    valid, oxidation_state = check_metal(this_metal, oxidation_state)
    # generate key in descriptor space
    ox = int(oxidation_state)
    if args.debug:
        print(f'metal is {this_metal}')
        print(('metal validity', valid))
    if not valid:
        emsg.append("\n Oxidation state not available for this metal")
        ANN_reason = 'ox state not avail for metal'
        return valid, ANN_reason, ANN_attributes

    try:
        high_spin, spin_ops = spin_classify(this_metal, spin, ox)
    except KeyError:
        valid = False
        emsg.append("\n this spin state not available for this metal")
        ANN_reason = 'spin state not available for metal'
        return valid, ANN_reason, ANN_attributes

    if emsg:
        print(str(" ".join(["ANN messages:"] + [str(i) for i in emsg])))

    (valid, axial_ligs, equatorial_ligs, ax_dent, eq_dent, ax_tcat,
        eq_tcat, axial_ind_list, equatorial_ind_list) = check_ligands(
        ligs, batslist, dents, tcats)
    if args.debug:
        print("\n")
        print(f"ligand validity is {valid}")
        print('Occs')
        print(occs)
        print('Ligands')
        print(ligs)
        print('Dents')
        print(dents)
        print('Bats (backbone atoms)')
        print(batslist)
        print(('lig validity', valid))
        print(('ax ligs', axial_ligs))
        print(('eq ligs', equatorial_ligs))
        print(('spin is', spin))
    if not valid:
        ANN_reason = 'found incorrect ligand symmetry'
        return valid, ANN_reason, ANN_attributes

    ax_lig3D, r_emsg = lig_load(axial_ligs[0], licores)  # load ligand
    if r_emsg:
        emsg += r_emsg
    # check decoration index
    if newdecs:
        if newdecs[axial_ind_list[0]]:
            ax_lig3D = decorate_molecule(
                axial_ligs[0], newdecs[axial_ind_list[0]], newdec_inds[axial_ind_list[0]], args.debug, save_bond_info=False)

    ax_lig3D.convert2mol3D()  # mol3D representation of ligand
    # eq
    eq_lig3D, r_emsg = lig_load(equatorial_ligs[0], licores)  # load ligand
    if newdecs:
        if newdecs[equatorial_ind_list[0]]:
            eq_lig3D = decorate_molecule(
                equatorial_ligs[0], newdecs[equatorial_ind_list[0]], newdec_inds[equatorial_ind_list[0]], args.debug,
                save_bond_info=False)
    if r_emsg:
        emsg += r_emsg
    eq_lig3D.convert2mol3D()  # mol3D representation of ligand
    if ax_tcat:
        ax_lig3D.cat = ax_tcat
        if args.debug:
            print(f'custom ax connect atom given (0-ind) {ax_tcat}')
    if eq_tcat:
        eq_lig3D.cat = eq_tcat
        if args.debug:
            print(f'custom eq connect atom given (0-ind) {eq_tcat}')

    if args.debug:
        print(f'finished checking ligands, valid is {valid}')

    valid, ax_type = get_con_at_type(ax_lig3D, ax_lig3D.cat)
    valid, eq_type = get_con_at_type(eq_lig3D, eq_lig3D.cat)
    if args.debug:
        print(f'finished con atom types {ax_type} and {eq_type}')
    if not valid:
        return valid, ANN_reason, ANN_attributes

    eq_ki = get_truncated_kier(eq_lig3D, eq_lig3D.cat)
    ax_ki = get_truncated_kier(ax_lig3D, ax_lig3D.cat)
    eq_EN = get_lig_EN(eq_lig3D, eq_lig3D.cat)
    ax_EN = get_lig_EN(ax_lig3D, ax_lig3D.cat)
    eq_bo = get_bond_order(eq_lig3D.OBMol, eq_lig3D.cat, eq_lig3D)
    ax_bo = get_bond_order(ax_lig3D.OBMol, ax_lig3D.cat, ax_lig3D)

    if axial_ligs[0] in ['carbonyl', 'cn']:
        ax_bo = 3
    if equatorial_ligs[0] in ['carbonyl', 'cn']:
        eq_bo = 3
    eq_charge = eq_lig3D.OBMol.GetTotalCharge()
    ax_charge = ax_lig3D.OBMol.GetTotalCharge()

    # preprocess:
    sum_delen = (2.0)*ax_EN + (4.0)*eq_EN
    if abs(eq_EN) > abs(ax_EN):
        max_delen = eq_EN
    else:
        max_delen = ax_EN
    alpha = 0.2  # default for B3LYP
    if args.exchange:
        try:
            if float(args.exchange) > 1:
                alpha = float(args.exchange)/100  # if given as %
            elif float(args.exchange) <= 1:
                alpha = float(args.exchange)
        except ValueError:
            print('cannot cast exchange argument to float, using 20%')

    if args.debug:
        print(('ax_bo', ax_bo))
        print(('eq_bo', eq_bo))
        print(('ax_dent', ax_dent))
        print(('eq_dent', eq_dent))
        print(('ax_charge', ax_charge))
        print(('eq_charge', eq_charge))
        print(('sum_delen', sum_delen))
        print(('max_delen', max_delen))
        print(('ax_type', ax_type))
        print(('eq_type', eq_type))
        print(('ax_ki', ax_ki))
        print(('eq_ki', eq_ki))

    nn_excitation = [0, 0, 0, 0, 0,  # metals co/cr/fe/mn/ni                 #1-5
                     ox, alpha, ax_charge, eq_charge,  # ox/alpha/axlig charge/eqlig charge #6-9
                     ax_dent, eq_dent,  # ax_dent/eq_dent/ #10-11
                     0, 0, 0, 0,  # axlig_connect: Cl,N,O,S #12 -15
                     0, 0, 0, 0,  # eqliq_connect: Cl,N,O,S #16-19
                     sum_delen, max_delen,  # mdelen, maxdelen #20-21
                     ax_bo, eq_bo,  # axlig_bo, eqliq_bo #22-23
                     ax_ki, eq_ki]  # axlig_ki, eqliq_kii #24-25
    slope_excitation = [0, 0, 0, 0, 0,  # metals co/cr/fe/mn/ni                 #1-5
                        ox, ax_charge, eq_charge,  # ox/axlig charge/eqlig charge #6-8
                        ax_dent, eq_dent,  # ax_dent/eq_dent/ #9-10
                        0, 0, 0, 0,  # axlig_connect: Cl,N,O,S #11 -14
                        0, 0, 0, 0,  # eqliq_connect: Cl,N,O,S #15-18
                        sum_delen, max_delen,  # mdelen, maxdelen #19-20
                        ax_bo, eq_bo,  # axlig_bo, eqliq_bo #21-22
                        ax_ki, eq_ki]  # axlig_ki, eqliq_kii #23-24

    # discrete variable encodings

    valid, nn_excitation = metal_corrector(nn_excitation, this_metal)
    valid, slope_excitation = metal_corrector(slope_excitation, this_metal)

    valid, nn_excitation = ax_lig_corrector(nn_excitation, ax_type)
    valid, slope_excitation = ax_lig_corrector(slope_excitation, ax_type)

    valid, nn_excitation = eq_lig_corrector(nn_excitation, eq_type)
    valid, slope_excitation = eq_lig_corrector(slope_excitation, eq_type)

    if not valid:
        return valid, ANN_reason, ANN_attributes

    print("******************************************************************")
    print("************** ANN is engaged and advising on spin ***************")
    print("************** and metal-ligand bond distances    ****************")
    print("******************************************************************")
    if high_spin:
        print(f'You have selected a high-spin state, s = {spin}')
    else:
        print(f'You have selected a low-spin state, s = {spin}')
    # test Euclidean norm to training data distance
    train_dist, best_row = find_eu_dist(nn_excitation)

    ANN_attributes.update({'ANN_dist_to_train': train_dist})
    ANN_attributes.update({'ANN_closest_train': best_row})
    print('distance to training data is ' +
           f'{train_dist:.2f} ANN trust: {max(0.01, 1.0-train_dist):.2f}')
    print(f' with closest training row {best_row[:-2]} at {best_row[-2:]}% HFX')
    ANN_trust = 'not set'
    if float(train_dist) < 0.25:
        print('ANN results should be trustworthy for this complex ')
        ANN_trust = 'high'
    elif float(train_dist) < 0.75:
        print('ANN results are probably useful for this complex ')
        ANN_trust = 'medium'
    elif float(train_dist) < 1.0:
        print('ANN results are fairly far from training data, be cautious ')
        ANN_trust = 'low'
    elif float(train_dist) > 1.0:
        print('ANN results are too far from training data, be cautious ')
        ANN_trust = 'very low'
    ANN_attributes.update({'ANN_trust': ANN_trust})
    # engage ANN

    delta, scaled_excitation = get_splitting(nn_excitation)
    # report to stdout
    if delta[0] < 0 and not high_spin:
        if abs(delta[0]) > 5:
            print('warning, ANN predicts a high spin ground state for this complex')
        else:
            print(
                'warning, ANN predicts a near degenerate ground state for this complex')
    if delta[0] >= 0 and high_spin:
        if abs(delta[0]) > 5:
            print('warning, ANN predicts a low spin ground state for this complex')
        else:
            print(
                'warning, ANN predicts a near degenerate ground state for this complex')
    print(f'ANN predicts a spin splitting (HS - LS) of {float(delta[0]):.2f} kcal/mol at {100*alpha:.0f}% HFX')
    ANN_attributes.update({'pred_split_HS_LS': delta[0]})
    # reparse to save attributes
    ANN_attributes.update({'This spin': spin})
    if delta[0] < 0 and (abs(delta[0]) > 5):
        ANN_attributes.update({'ANN_ground_state': spin_ops[1]})
    elif delta[0] > 0 and (abs(delta[0]) > 5):
        ANN_attributes.update({'ANN_ground_state': spin_ops[0]})
    else:
        ANN_attributes.update({'ANN_ground_state': f'dgen {spin_ops}'})

    r_ls = get_ls_dist(nn_excitation)
    r_hs = get_hs_dist(nn_excitation)
    if high_spin:
        r = r_hs
    else:
        r = r_ls

    print('ANN bond length is predicted to be: ' +
           f'{float(r):.2f} angstrom')
    ANN_attributes.update({'ANN_bondl': len(batslist)*[r[0]]})
    print('ANN low spin bond length is predicted to be: ' +
           f'{float(r_ls):.2f} angstrom')
    print('ANN high spin bond length is predicted to be: ' +
           f'{float(r_hs):.2f} angstrom')

    # use ANN to predict functional sensitivty
    HFX_slope = 0
    HFX_slope = get_slope(slope_excitation)
    print('Predicted HFX exchange sensitivity is : ' +
           f'{float(HFX_slope):.2f} kcal/HFX')
    ANN_attributes.update({'ANN_slope': HFX_slope})
    print("*******************************************************************")
    print("************** ANN complete, saved in record file *****************")
    print("*******************************************************************")

    if not valid and not ANN_reason:
        ANN_reason = ' uncaught rejection (see sdout/stderr)'
    return valid, ANN_reason, ANN_attributes


def ax_lig_corrector(excitation, con_atom_type):
    ax_lig_index_dictionary = {'Cl': 11, 'F': 11, 'N': 12, 'O': 13, 'S': 14}
    # C is the basic value
    try:
        if not con_atom_type == "C":
            excitation[ax_lig_index_dictionary[con_atom_type]] = 1
        valid = True
    except KeyError:
        valid = False
    return valid, excitation


def eq_lig_corrector(excitation, con_atom_type):
    eq_lig_index_dictionary = {'Cl': 15, 'F': 15, 'N': 16, 'O': 17, 'S': 18}
    try:
        if not con_atom_type == "C":
            excitation[eq_lig_index_dictionary[con_atom_type]] = 1
        valid = True
    except KeyError:
        valid = False
    return valid, excitation


def metal_corrector(excitation, metal):
    metal_index_dictionary = {'co': 0, 'cr': 1, 'fe': 2, 'mn': 3, 'ni': 4}
    try:
        excitation[metal_index_dictionary[metal]] += 1
        valid = True
    except KeyError:
        valid = False

    return valid, excitation


def spin_classify(metal, spin, ox):
    metal_spin_dictionary = {'co': {2: 4, 3: 5},
                             'cr': {2: 5, 3: 4},
                             'fe': {2: 5, 3: 6},
                             'mn': {2: 6, 3: 5},
                             'ni': {2: 3}}

    suggest_spin_dictionary = {'co': {2: [2, 4], 3: [1, 5]},
                               'cr': {2: [1, 5], 3: [2, 4]},
                               'fe': {2: [1, 5], 3: [2, 6]},
                               'mn': {2: [2, 6], 3: [1, 5]},
                               'ni': {2: [1, 3]}}

    high_spin = False
    if (int(spin) >= int(metal_spin_dictionary[metal][ox])):
        high_spin = True
    spin_ops = suggest_spin_dictionary[metal][ox]
    return high_spin, spin_ops


def get_splitting(excitation):
    delta, scaled_excitation = simple_splitting_ann(excitation)
    return delta, scaled_excitation


def get_slope(slope_excitation):
    HFX = simple_slope_ann(slope_excitation)
    return HFX


def get_ls_dist(excitation):
    r = simple_ls_ann(excitation)
    return r


def get_hs_dist(excitation):
    r = simple_hs_ann(excitation)
    return r
