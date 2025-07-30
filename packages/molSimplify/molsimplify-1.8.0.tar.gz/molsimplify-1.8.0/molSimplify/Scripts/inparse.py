# @file inparse.py
#  Processes inputs
#
#  Written by Tim Ioannidis for HJK Group
#
#  Dpt of Chemical Engineering, MIT

import argparse
import os
import re

import yaml

from molSimplify.Classes.globalvars import (defaultspins,
                                            elementsbynum,
                                            globalvars,
                                            metals_conv,
                                            romans,
                                            mtlsdlist)
from molSimplify.Scripts.io import (getbinds, getcores, getgeoms, getlicores,
                                    getslicores, printgeoms, substr_load, getligs)


# Checks input for correctness and uses defaults otherwise
#  @param args Namespace of arguments
def checkinput(args, calctype="base"):
    globs = globalvars()
    coords, geomnames, geomshorts, geomgroups = getgeoms()
    emsg = False
    if calctype == "base":
        # check core
        if not args.core:
            print(
                f'WARNING: No core specified. Defaulting to Fe. Available cores are: {getcores()}')
            args.core = ['fe']
        # convert full element name to symbol for cores:
        if args.core[0].lower() in list(metals_conv.keys()):
            print(f'switching core from {args.core} to {metals_conv[args.core[0].lower()]}')
            args.core = [metals_conv[args.core[0].lower()]]
        if (args.core[0][0].upper()+args.core[0][1:].lower() in elementsbynum):
            # convert to titlecase
            args.core[0] = args.core[0][0].upper()+args.core[0][1:].lower()
            # check oxidation state
            if not args.oxstate:
                try:
                    print('WARNING: No oxidation state specified. Defaulting to ' +
                          globs.defaultoxstate[args.core[0].lower()])
                    args.oxstate = globs.defaultoxstate[args.core[0].lower()]
                except KeyError:
                    print('WARNING: No oxidation state specified. Defaulting to 2')
                    args.oxstate = '2'
            # check spin state (doesn't work for custom cores)
            if not args.spin:
                if args.oxstate in list(romans.keys()):
                    oxstatenum = romans[args.oxstate]
                else:
                    oxstatenum = args.oxstate
                if args.core[0].lower() in mtlsdlist:
                    if mtlsdlist[args.core[0].lower()]-max(0, int(oxstatenum)-2) in defaultspins:
                        defaultspinstate = defaultspins[mtlsdlist[args.core[0].lower(
                        )]-max(0, int(oxstatenum)-2)]
                        print(
                            f'WARNING: No spin multiplicity specified. Defaulting to {defaultspinstate}')
                        print(
                            'Please check this against our ANN output (where available)')
                    else:
                        print(
                            'WARNING: Oxidation state seems to be invalid. Please check. Defaulting to singlet anyway.')
                        defaultspinstate = '1'
                else:
                    defaultspinstate = '1'
                    print(
                        'WARNING: No spin multiplicity specified. Defaulting to singlet (1)')
                args.spin = defaultspinstate

            # default ligand if none given
            if not args.lig and not args.rgen:
                print('WARNING: No ligands specified. Defaulting to water with six occurrences.')
                args.lig = ['water']
                args.ligocc = ['6']

            # calculate occurrences, denticities etc for all ligands
            # Begin toccs calculation.
            licores = getlicores()
            smilesligs = 0
            toccs = 0
            occs0 = []
            dentl = []
            cats0 = []
            ligoc = args.ligocc
            for i, ligname in enumerate(args.lig):
                # if not in cores -> smiles/file
                if ligname not in list(licores.keys()):
                    if args.smicat and len(args.smicat) >= (smilesligs+1):
                        if 'pi' in args.smicat[smilesligs]:
                            cats0.append(['c'])
                        else:
                            cats0.append(args.smicat[smilesligs])
                    else:
                        cats0.append([0])
                    dent_i = len(cats0[-1])
                    smilesligs += 1
                else:
                    cats0.append(False)
                # otherwise get denticity from ligands dictionary
                    if 'pi' in licores[ligname][2]:
                        dent_i = 1
                    else:
                        if isinstance(licores[ligname][2], str):
                            dent_i = 1
                        else:
                            dent_i = int(len(licores[ligname][2]))
                # get occurrence for each ligand if specified
                # default of 1 if args.ligocc is not set
                if ligoc:
                    oc_i = int(ligoc[i]) if i < len(ligoc) else 1
                else:
                    oc_i = 1
                occs0.append(0)         # initialize occurrences list
                dentl.append(dent_i)    # append denticity to list
                # loop over occurrence of ligand i to check for max coordination
                for j in range(0, oc_i):
                    occs0[i] += 1
                    toccs += dent_i
            # End of toccs calculation.

            if (not args.coord) and (not args.geometry) and args.lig:
                print(
                    f'WARNING: No coordination number specified. Calculating from lig, ligocc, and subcatoms and found {toccs}.')
                args.coord = toccs
            # set default coord if nothing given
            elif (not args.coord) and (not args.geometry) and (not args.lig):
                print(
                    'WARNING: No coord/geo is specified. Defaulting to 6-coord/octahedral')
                args.coord = 6
                args.geometry = 'oct'

            if args.coord and (not args.geometry or (args.geometry not in geomnames and args.geometry not in geomshorts)):
                print('WARNING: No or unknown coordination geometry specified. Defining coordination geometry based on found coordination number: ' +
                      globs.defaultgeometry[int(args.coord)][1])
                args.geometry = globs.defaultgeometry[int(args.coord)][0]
            elif args.geometry and not args.coord:
                if args.geometry not in geomnames and args.geometry not in geomshorts:
                    print(
                        'You have specified an invalid geometry. Available geometries are:')
                    printgeoms()
                    print('Defaulting to octahedral (6)')
                    args.geometry = 'oct'
                    args.coord = 6
                else:
                    if args.geometry in geomnames:
                        args.coord = coords[geomnames.index(args.geometry)]
                    else:
                        # args.geometry is a short name.
                        args.coord = coords[geomshorts.index(args.geometry)]
                    print(
                        f'WARNING: No coordination number specified. Defaulting to {args.coord}')
            elif args.coord and args.geometry:
                # Check whether the coordination number and geometry are compatible.
                if args.geometry in geomnames:
                    expected_coord = coords[geomnames.index(args.geometry)]
                else:
                    # args.geometry is a short name.
                    expected_coord = coords[geomshorts.index(args.geometry)]

                consistency_check = int(args.coord) == int(expected_coord)
                if not consistency_check:
                    raise ValueError(f'args.coord {args.coord} and args.geometry {args.geometry} are incompatible. Expect a coordination of {expected_coord} for the provided geometry.')
            # check number of ligands
            if not args.ligocc:
                # If denticity of the first ligand is one
                if dentl[0] == 1:
                    print(f'WARNING: No ligand numbers specified. Defaulting to {args.coord} of the first ligand and 0 of all others.')
                    args.ligocc = [args.coord]
                    for lig in args.lig[1:]:
                        args.ligocc.append(0)
                else:
                    raise ValueError('ligocc not set and denticity of the first ligand is not one. Exiting.')
            elif int(args.coord) != toccs:
                # If ligocc was provided by the user, toccs value should be good.
                raise ValueError(f'args.coord {args.coord} mismatch with number of ligand connections ({toccs}), based on ligocc and their denticity.')

    elif calctype == "tsgen":
        # load substrate for reference
        print(args.substrate[0], 0, args.subcatoms)
        sub, subcatoms, emsg = substr_load(
            args.substrate[0], 0, args.subcatoms)
        # check core
        if not args.core:
            print(
                f'WARNING: No core specified. Defaulting to Fe. \nAvailable cores are: {getcores()}')
            args.core = ['fe']
        if args.core[0][0].upper()+args.core[0][1:].lower() in elementsbynum:
            # convert to titlecase
            args.core[0] = args.core[0][0].upper()+args.core[0][1:].lower()
            # check oxidation state
            if not args.oxstate:
                try:
                    print('WARNING: No oxidation state specified. Defaulting to ' +
                          globs.defaultoxstate[args.core[0].lower()])
                    args.oxstate = globs.defaultoxstate[args.core[0].lower()]
                except KeyError:
                    print('WARNING: No oxidation state specified. Defaulting to 2')
                    args.oxstate = '2'
            # check spin state (doesn't work for custom cores)
            if not args.spin:
                if args.oxstate in list(romans.keys()):
                    oxstatenum = romans[args.oxstate]
                else:
                    oxstatenum = args.oxstate
                if args.core[0].lower() in mtlsdlist:
                    if mtlsdlist[args.core[0].lower()]-max(0, int(oxstatenum)-2) in defaultspins:
                        defaultspinstate = defaultspins[mtlsdlist[args.core[0].lower(
                        )]-max(0, int(oxstatenum)-2)]
                        print(
                            f'WARNING: No spin multiplicity specified. Defaulting to {defaultspinstate}')
                        print(
                            'Please check this against our ANN output (where available)')
                    else:
                        print(
                            'WARNING: Oxidation state seems to be invalid. Please check. Defaulting to singlet anyway.')
                        defaultspinstate = '1'
                else:
                    defaultspinstate = '1'
                    print(
                        'WARNING: No spin multiplicity specified. Defaulting to singlet (1)')
                args.spin = defaultspinstate
            # check ligands
            if not args.lig and not args.rgen:
                print('WARNING: No ligands specified. Substrate is placed to core.')
                args.lig = ['']

            # check coordination number and geometry

            # Calculate occurrences, denticities etc for all ligands
            # Begin toccs calculation.
            licores = getlicores()
            smilesligs = 0
            toccs = 0
            occs0 = []
            dentl = []
            cats0 = []
            ligoc = args.ligocc
            for i, ligname in enumerate(args.lig):
                # if not in cores -> smiles/file
                if ligname not in list(licores.keys()):
                    if args.smicat and len(args.smicat) >= (smilesligs+1):
                        if 'pi' in args.smicat[smilesligs]:
                            cats0.append(['c'])
                        else:
                            cats0.append(args.smicat[smilesligs])
                    else:
                        cats0.append([0])
                    dent_i = len(cats0[-1])
                    smilesligs += 1
                else:
                    cats0.append(False)
                # otherwise get denticity from ligands dictionary
                    if 'pi' in licores[ligname][2]:
                        dent_i = 1
                    else:
                        if isinstance(licores[ligname][2], str):
                            dent_i = 1
                        else:
                            dent_i = int(len(licores[ligname][2]))
                # get occurrence for each ligand if specified (default 1)
                oc_i = int(ligoc[i]) if i < len(ligoc) else 1
                occs0.append(0)         # initialize occurrences list
                dentl.append(dent_i)    # append denticity to list
                # loop over occurrence of ligand i to check for max coordination
                for j in range(0, oc_i):
                    occs0[i] += 1
                    toccs += dent_i
            for i, substrate in enumerate(args.substrate):
                if args.core[0].lower() in args.mlig:
                    suboc_i = len(
                        [core for core in args.core if core.lower() in args.mlig])
                    for j in range(suboc_i):
                        toccs += 1
            # End of toccs calculation.

            if not args.coord and not args.geometry:
                print(
                    f'WARNING: No coordination number specified. Calculating from lig, ligocc, and subcatoms and found {toccs}.')
                args.coord = toccs
            if args.coord and (not args.geometry or (args.geometry not in geomnames and args.geometry not in geomshorts)):
                print('WARNING: No or unknown coordination geometry specified. Defining coordination geometry based on found coordination number: ' +
                      globs.defaultgeometry[int(args.coord)][1])
                args.geometry = globs.defaultgeometry[int(args.coord)][0]
            elif args.geometry and not args.coord:
                coords, geomnames, geomshorts, geomgroups = getgeoms()
                if args.geometry not in geomnames and args.geometry not in geomshorts:
                    print(
                        'You have specified an invalid geometry. Available geometries are:')
                    printgeoms()
                    print('Defaulting to octahedral (6)')
                    args.geometry = 'oct'
                    args.coord = 6
                else:
                    if args.geometry in geomnames:
                        args.coord = coords[geomnames.index(args.geometry)]
                    else:
                        # args.geometry is a short name.
                        args.coord = coords[geomshorts.index(args.geometry)]
                    print(
                        f'WARNING: No coordination number specified. Defaulting to {args.coord}')
            elif args.coord and args.geometry:
                # Check whether the coordination number and geometry are compatible.
                if args.geometry in geomnames:
                    expected_coord = coords[geomnames.index(args.geometry)]
                else:
                    # args.geometry is a short name.
                    expected_coord = coords[geomshorts.index(args.geometry)]

                consistency_check = int(args.coord) == int(expected_coord)
                if not consistency_check:
                    raise ValueError(f'args.coord {args.coord} and args.geometry {args.geometry} are incompatible. Expect a coordination of {expected_coord} for the provided geometry.')
            # check number of ligands
            if not args.ligocc:
                # If denticity of the first ligand is one
                if dentl[0] == 1:
                    print(f'WARNING: No ligand numbers specified. Defaulting to {args.coord} of the first ligand and 0 of all others.')
                    args.ligocc = [args.coord]
                    for lig in args.lig[1:]:
                        args.ligocc.append(0)
                else:
                    raise ValueError('ligocc not set and denticity of the first ligand is not one. Exiting.')
            elif int(args.coord) != toccs:
                # If ligocc was provided by the user, toccs value should be good.
                raise ValueError(f'args.coord {args.coord} mismatch with number of ligand connections ({toccs}), based on ligocc and their denticity.')
            # check substrate
            if not args.substrate:
                print('WARNING: Transition state generation is request without the specification of a substrate. Defaulting to methane.')
                args.substrate = 'methane'
            # check substrate connecting atom
            if args.substrate and not args.subcatoms:
                print(f'WARNING: A substrate is specified for TS generation without the specification of a connection point in the substrate. Defaulting to the numbers stored in the dictionary: {subcatoms}')
                args.subcatoms = subcatoms
            # check mcomplex connecting ligand to the substrate
            if args.substrate and not args.mlig:
                print('WARNING: A substrate is specified for TS generation without the specification of a ligand in the metal complex to connect with. Defaulting to ligand index 0.')
                args.mlig = args.lig[0]
            # check mlig connecting point if the ligand has more than one atom
            if args.mlig and not args.mligcatoms:
                sub, subcatoms, emsg = substr_load(args.mlig[0], 0, subcatoms)
                if sub.natoms == 1:
                    args.mligcatoms = [0]
                else:
                    print('WARNING: A ligand in the metal complex is specified to connect with the substrate for TS generation without the specification of a connection point in the ligand. Defaulting to atom index 0.')
                    args.mligcatoms = [0]
    elif calctype == "dbadd":
        if args.ligadd:
            print('ligand addition function')
            if not args.ligname:
                args.ligname = os.path.splitext(
                    os.path.basename(args.ligadd))[0]
            if not args.ligcon:
                args.ligcon = [0]
            if not args.ligffopt:
                args.ligffopt = "BA"

    return(emsg)


# Check true or false
#  @param arg String to be checked
#  @return bool


def checkTrue(arg):

    if 'auto' in arg.lower():
        return 'auto'
    elif 'y' in arg.lower() or '1' in arg.lower() or 't' in arg.lower() or arg == 1:
        return True
    else:
        return False

# Check if variable is a number
#  @param s variable to be checked
#  @return bool


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

# Consolidate arguments into lists
#  @param args Namespace of arguments


def cleaninput(args):
    # check ligands
    if args.lig:
        ls = []
        ligdic = getslicores()
        for i, s in enumerate(args.lig):
            if isinstance(s, list):
                for ss in s:
                    if ss in list(ligdic.keys()):
                        ss = ligdic[ss][0]
                    ls.append(ss)
            else:
                if s in list(ligdic.keys()):
                    s = ligdic[s][0]
                ls.append(s)
        args.lig = ls
    # check sminame
    if args.sminame:
        ls = []
        for i, s in enumerate(args.sminame):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.sminame = ls
    # check qoption
    if args.qoption:
        ls = []
        for i, s in enumerate(args.qoption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.qoption = ls
    # check sysoption
    if args.sysoption:
        ls = []
        for i, s in enumerate(args.sysoption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.sysoption = ls
    # check ctrloption
    if args.ctrloption:
        ls = []
        for i, s in enumerate(args.ctrloption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.ctrloption = ls
    # check scfoption
    if args.scfoption:
        ls = []
        for i, s in enumerate(args.scfoption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.scfoption = ls
    # check statoption
    if args.statoption:
        ls = []
        for i, s in enumerate(args.statoption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.statoption = ls
    # check remoption
    if args.remoption:
        ls = []
        for i, s in enumerate(args.remoption):
            if isinstance(s, list):
                for ss in s:
                    ls.append(ss)
            else:
                ls.append(s)
        args.remoption = ls
    # convert keepHs to boolean and fill in missing values with default
    keepHs_default = 'auto'
    if not args.keepHs:
        args.keepHs = [keepHs_default]
    if args.keepHs and args.lig:
        while len(args.keepHs) < len(args.lig):  # user should specify as many booleans for keepHs as there are kinds of ligands if she wants to avoid default assignment
            args.keepHs.append(keepHs_default)
        for i, s in enumerate(args.keepHs):
            if args.keepHs[i].lower() != 'auto':
                args.keepHs[i] = checkTrue(s)
    # parse FF settings:
    # if no FF opt is requested, turn off
    if args.ffoption[0].lower() in ['n', 'no']:
        args.ff = False
    # if FF opt is desired, parse FF choice
    else:
        opts = args.ffoption
        if 'ba' in opts[0].lower():
            args.ffoption = 'ba'
        elif 'no' in opts[0].lower() or 'n' in opts[0].lower():
            args.ffoption = 'no'
        elif 'l' in opts[0].lower():
            args.ffoption = 'l'  # ligands.dict control
        else:
            args.ffoption = ''
            for op in opts:
                op = op.strip(' ')
                if op[0].lower() == 'b':
                    args.ffoption += 'b'
                if op[0].lower() == 'a':
                    args.ffoption += 'a'

# Generates input file from command line input
#  @param args Namespace of arguments
#  @return CLIinput.inp (file name)


def parseCLI(args):
    cliargs = ' '.join(args)
    cliargs = ' ' + cliargs
    s = [_f for _f in cliargs.split(' -') if _f]
    # fname = args.core[0] + '.inp'
    fname = 'CLIinput.inp'
    with open(fname, 'w') as f:
        f.write('# molSimplify input file generated from CLI input\n')
        for line in s:
            f.write('-'+line+'\n')
    return fname

# Parses input file
#  @param args Namespace of arguments


def parseinputfile(args, inputfile_str=None):
    # arguments that don't match with  inparse name and
    # are not automatically initialized go here:
    args.skipANN = False
    args.oldANN = False
    args.dbvdent = False
    args.dbvconns = False
    args.dbvhyb = False
    args.dbvlinks = False
    args.rprompt = False
    set_rundir = False
    args.overwrite = False

    # (we should remove these where posible)
    # THIS NEEDS CLEANING UP TO MINIMIZE DUPLICATION WITH parsecommandline
    if inputfile_str:
        inputfile_lines = inputfile_str.split('\n')
    else:
        with open(args.i) as f:
            inputfile_lines = f.readlines()

    for line in inputfile_lines:
        # For arguments that cannot accept smiles as args, split possible comments
        if '-lig' not in line and '-core' not in line and '-bind' not in line and '-dbsmarts' not in line:
            line = line.split('#')[0]  # remove comments
        li = line.strip()
        li = li.replace('\n', '')
        line = line.replace('\n', '')
        if not li.startswith("#") and len(li) > 0:  # ignore comments/empty lines
            # split arguments on whitespace, commas (this breaks smarts)
            l = [_f for _f in re.split(' |\t|,|&', li) if _f]  # noqa: E741
            # parse general arguments
            if (l[0] == '-core' and len(l[1:]) > 0):
                args.core = [ll for ll in l[1:]]
            if (l[0] == '-ccatoms' and len(l[1:]) > 0):
                args.ccatoms = []
                l = line.split('ccatoms', 1)[1]  # noqa: E741
                l = l.strip(' ')  # noqa: E741
                l = l.split(',')  # noqa: E741
                args.ccatoms = [int(ll)-1 for ll in l]
            if (l[0] == '-rundir'):
                set_rundir = True
                args.rundir = line.split("#")[0].strip('\n')
                args.rundir = args.rundir.split('-rundir')[1]
                args.rundir = args.rundir.lstrip(' ')
                args.rundir = args.rundir.rstrip(' ')
                print(f'The directory for this calculation is: {args.rundir}')

                if (args.rundir[-1] == '/'):
                    args.rundir = args.rundir[:-1]
            if (l[0] == '-custom_data_dir'):
                args.custom_data_dir = l[1]
            if (l[0] == '-suff'):
                args.suff = l[1].strip('\n')
            if (l[0] == '-name'):
                args.name = l[1]
            if (l[0] == '-skipANN'):
                args.skipANN = True
            if (l[0] == '-oldANN'):
                args.oldANN = True
            if (l[0] == '-jobdir'):
                if (len(l) > 1):
                    args.jobdir = l[1]
                else:
                    args.jobdirblank = True
            if (l[0] == '-no_tabs'):
                args.no_tabs = True
            ### parse structure generation arguments ###
            if (l[0] == '-bind' and len(l[1:]) > 0):
                l = [_f for _f in re.split(' |,|\t', line) if _f]  # noqa: E741
                # discard comments
                for ibind, lbind in enumerate(l):
                    if lbind == '#':
                        l = l[:ibind]  # noqa: E741
                        break
                args.bind = l[1]
            if (l[0] == '-nbind' and len(l[1:]) > 0):
                args.bindnum = l[1]
            if (l[0] == '-bcharge' and len(l[1:]) > 0):  # parse charge for binding species
                args.bcharge = l[1]
            if (l[0] == '-btheta' and len(l[1:]) > 0):
                args.btheta = l[1]
            if (l[0] == '-bphi' and len(l[1:]) > 0):
                args.bphi = l[1]
            if (l[0] == '-bsep' and len(l[1:]) > 0):
                args.bsep = l[1]
            if (l[0] == '-bref' and len(l[1:]) > 0):
                args.bref = l[1:]
            if (l[0] == '-nambsmi' and len(l[1:]) > 0):
                args.nambsmi = l[1]
            if (l[0] == '-maxd' and len(l[1:]) > 0):
                args.maxd = l[1]
            if (l[0] == '-mind' and len(l[1:]) > 0):
                args.mind = l[1]
            if (l[0] == '-oxstate' and len(l[1:]) > 0):
                args.oxstate = l[1]
            if (l[0] == '-coord' and len(l[1:]) > 0):
                args.coord = l[1]
            if (l[0] == '-geometry' and len(l[1:]) > 0):
                args.geometry = l[1].lower()
            if (l[0] == '-geo' and len(l[1:]) > 0):
                args.geometry = l[1].lower()
            # parse ligands
            if (l[0] == '-lig') and len(l[1:]):
                args.lig = l[1:]
            if (l[0] == '-lignum' and len(l[1:]) > 0):
                args.lignum = l[1]
            if (l[0] == '-liggrp' and len(l[1:]) > 0):
                args.liggrp = l[1]
            if (l[0] == '-ligctg' and len(l[1:]) > 0):
                args.ligctg = l[1]
            if (l[0] == '-ligocc' and len(l[1:]) > 0):
                args.ligocc = l[1:]
            if (l[0] == '-rkHs'):
                args.rkHs = checkTrue(l[1])
            if (l[0] == '-stripHs'):
                args.stripHs = True
            if (l[0] == '-ligloc'):
                args.ligloc = checkTrue(l[1])
            if (l[0] == '-ligalign'):
                args.ligalign = checkTrue(l[1])
            if (l[0] == '-replig'):
                args.replig = checkTrue(l[1])
            if (l[0] == '-genall'):
                args.genall = checkTrue(l[1])
            if (l[0] == '-isomers'):
                args.isomers = checkTrue(l[1])
            if (l[0] == '-antigeoisomer'):
                args.antigeoisomer = checkTrue(l[1])
            if (l[0] == '-reportonly'):
                args.reportonly = checkTrue(l[1])
            if (l[0] == '-stereos'):
                args.stereos = checkTrue(l[1])
            if (l[0] == '-MLbonds' and len(l[1:]) > 0):
                args.MLbonds = l[1:]
            if (l[0] == '-distort' and len(l[1:]) > 0):
                args.distort = l[1]
            if (l[0] == '-rgen' and len(l[1:]) > 0):
                args.rgen = l[1:]
            if (l[0] == '-keepHs' and len(l[1:]) > 0):
                args.keepHs = l[1:]
            if (l[0] == '-ff'):
                args.ff = l[1].lower()
            if (l[0] == '-ffoption' and len(l[1:]) > 0):
                args.ffoption = l[1:]
            if (l[0] == '-ff_final_opt' and len(l[1:]) > 0):
                args.ff_final_opt = l[1].lower()
            if (l[0] == '-place' and len(l[1:]) > 0):
                args.place = l[1]
            if (l[0] == '-sminame' and len(l[1:]) > 0):
                if args.sminame:
                    args.sminame.append(l[1:])
                else:
                    args.sminame = l[1:]
            if '-smicat' in line:
                args.smicat = []
                l = line.split('smicat', 1)[1]  # noqa: E741
                l = l.replace(' ', '')  # noqa: E741
                l = l.split('],[')  # noqa: E741
                for smicats in l:
                    smicats = smicats.strip('[]')
                    smicats = smicats.split(',')
                    lloc = list()
                    for ll in smicats:
                        try:
                            if ll.lower() != 'pi':
                                lloc.append(int(ll)-1)
                            else:
                                lloc.append(ll.lower())
                        except ValueError:
                            print(f'ERROR: smicat processing failed at {ll}')
                            print(
                                'Please use integers or  "pi" and divide by smiles ligand using [],[]')
                    args.smicat.append(lloc)

                print(f'final smicat set to {args.smicat}')
            if (l[0] == '-nconfs' and len(l[1:]) > 0):
                args.nconfs = l[1]
            if (l[0] == '-scoreconfs'):
                args.scoreconfs = True
            if '-pangles' in line:
                args.pangles = []
                l = [_f for _f in line.split('pangles', 1)[1] if _f]  # noqa: E741
                l = l.replace(' ', '')  # noqa: E741
                l = re.split(',|\t|&|\n', l)  # noqa: E741
                for ll in l:
                    args.pangles.append(
                        ll) if ll != '' else args.pangles.append(False)
            if (l[0] == '-decoration' and len(l[1:]) > 0):
                list_to_parse = (line.strip().split(' ')[1:])
                list_to_add = list()
                local_list = list()
                if not isinstance(list_to_parse, str):
                    for decor in list_to_parse:
                        decor = str(decor).strip().strip('[]').split(',')
                        local_list = local_list + [str(i) for i in decor]
                        list_to_add.append([str(i) for i in decor])
                else:
                    list_to_add = [list_to_parse]
                args.decoration = list_to_add
            if (l[0] == '-decoration_index' and len(l[1:]) > 0):
                list_to_parse = (line.strip().split(' ')[1:])
                list_to_add = list()
                local_list = list()
                if not isinstance(list_to_parse, str):
                    for decor in list_to_parse:
                        decor = str(decor).strip().strip('[]').split(',')
                        local_list = local_list + [str(i) for i in decor]
                        # correct for 0 index
                        list_to_add.append(
                            [int(i.strip('[]'))-1 for i in decor])
                else:
                    # correct for 0 index
                    list_to_add = [int(list_to_parse.strip('[]'))-1]
                args.decoration_index = list_to_add
                print(args.decoration_index)
            # parse qc arguments
            if (l[0] == '-qccode' and len(l[1:]) > 0):
                args.qccode = l[1]
            if (l[0] == '-calccharge'):
                args.calccharge = checkTrue(l[1])
            if (l[0] == '-charge' and len(l[1:]) > 0):
                args.charge = l[1:]
            if (l[0] == '-spin' and len(l[1:]) > 0):
                args.spin = l[1:]
            if (l[0] == '-spinmultiplicity' and len(l[1:]) > 0):
                args.spin = l[1:]
            if (l[0] == '-multiplicity' and len(l[1:]) > 0):
                args.spin = l[1:]
            if (l[0] == '-runtyp' and len(l[1:]) > 0):
                args.runtyp = l[1]
            if (l[0] == '-method' and len(l[1:]) > 0):
                args.method = l[1:]
            # parse terachem arguments
            if (l[0] == '-basis'):
                args.basis = l[1]
            if (l[0] == '-dispersion'):
                args.dispersion = l[1].strip('\n').lower()
            if (l[0] == '-qoption'):
                if args.qoption:
                    args.qoption.append(l[1:])
                else:
                    args.qoption = l[1:]
            # parse qchem arguments
            if (l[0] == '-exchange'):
                args.exchange = l[1]
            if (l[0] == '-correlation'):
                args.correlation = l[1]
            if (l[0] == '-unrestricted'):
                args.unrestricted = checkTrue(l[1])
            if (l[0] == '-remoption'):
                if args.remoption:
                    args.remoption.append(l[1:])
                else:
                    args.remoption = l[1:]
            # parse gamess arguments
            if (l[0] == '-gbasis'):
                args.gbasis = l[1]
            if (l[0] == '-ngauss'):
                args.ngauss = l[1]
            if (l[0] == '-npfunc'):
                args.npfunc = l[1]
            if (l[0] == '-ndfunc'):
                args.ndfunc = l[1]
            if (l[0] == '-sysoption'):
                if args.sysoption:
                    args.sysoption.append(l[1:])
                else:
                    args.sysoption = l[1:]
            if (l[0] == '-ctrloption'):
                if args.ctrloption:
                    args.ctrloption.append(l[1:])
                else:
                    args.ctrloption = l[1:]
            if (l[0] == '-scfoption'):
                if args.scfoption:
                    args.scfoption.append(l[1:])
                else:
                    args.scfoption = l[1:]
            if (l[0] == '-statoption'):
                if args.statoption:
                    args.statoption.append(l[1:])
                else:
                    args.statoption = l[1:]
            # parse MOLPAC generation routines
            if (l[0] == '-mopac'):
                args.mopac = True

            # parse jobscript arguments
            if (l[0] == '-jsched'):
                args.jsched = l[1]
            if (l[0] == '-jname'):
                args.jname = l[1]
            if (l[0] == '-memory'):
                args.memory = l[1]
            if (l[0] == '-wtime'):
                args.wtime = l[1]
            if (l[0] == '-queue'):
                args.queue = l[1]
            if (l[0] == '-gpus'):
                args.gpus = l[1]
            if (l[0] == '-cpus'):
                args.cpus = l[1]
            if (l[0] == '-modules'):
                args.modules = l[1:]
            if (l[0] == '-joption'):
                if not args.joption:
                    args.joption = []
                opts = ''
                for ll in l[1:]:
                    opts += ll+' '
                args.joption.append(opts)
            if (l[0] == '-jcommand'):
                if not args.jcommand:
                    args.jcommand = []
                opts = ''
                for ll in l[1:]:
                    opts += ll+' '
                args.jcommand.append(opts)
            # parse database arguments
            if (l[0] == '-dbsim'):
                args.dbsearch = True
                args.dbsim = l[1]
            if (l[0] == '-dbsearch'):
                args.dbsearch = True
            if (l[0] == '-dbresults'):
                args.dbresults = l[1]
            if (l[0] == '-dbdissim'):
                args.dbsearch = True
                args.dbdissim = l[1]
            if (l[0] == '-dboutputf'):
                args.dboutputf = l[1]
            if (l[0] == '-dbbase'):
                args.dbbase = l[1]
            if (l[0] == '-dbsmarts'):
                # Needs to not have been split on commas
                args.dbsearch = True
                args.dbsmarts = li.split()[1]
            if (l[0] == '-dbcatoms'):
                args.dbcatoms = l[1:]
            if (l[0] == '-dbfinger'):
                args.dbfinger = l[1]
            if (l[0] == '-dbatoms'):
                args.dbatoms = l[1]
            if (l[0] == '-dbbonds'):
                args.dbbonds = l[1]
            if (l[0] == '-dbarbonds'):
                args.dbarbonds = l[1]
            if (l[0] == '-dbsbonds'):
                args.dbsbonds = l[1]
            if (l[0] == '-dbmw'):
                args.dbmw = l[1]
            if (l[0] == '-dbnsearch'):
                args.dbnsearch = l[1]
            if (l[0] == '-drawmode'):
                args.drawmode = True
            else:
                args.drawmode = False
            if (l[0] == '-dballowedels'):
                args.dballowedels = l[1:]
            if (l[0] == '-dbfname'):
                args.dbfname = l[1]
            if (l[0] == '-dbmaxsmartsmatches'):
                args.dbmaxsmartsmatches = l[1]
            if (l[0] == '-dbhuman'):
                args.dbsearch = True
                args.dbhuman = True
            if (l[0] == '-dbvdent'):
                args.dbvdent = l[1]
            if (l[0] == '-dbvconns'):
                ll = [x for x in l[1:]]
                args.dbvconns = ll
            if (l[0] == '-dbvhyb'):
                ll = [x for x in l[1:]]
                args.dbvhyb = ll
            if (l[0] == '-dbvlinks'):
                args.dbvlinks = l[1]
            if (l[0] == '-dbfs'):
                args.dbfs = True
            if (l[0] == '-ligadd'):
                print('adding a ligand')
                args.ligadd = l[1]
            if (l[0] == '-ligname'):
                args.ligname = l[1]
            if (l[0] == '-ligcon'):
                list_to_parse = (line.strip().split(' ')[1:])
                list_to_add = list()
                local_list = list()
                if not isinstance(list_to_parse, str):
                    for decor in list_to_parse:
                        print('correcting string')
                        decor = str(decor).strip().strip('[]').split(',')
                        local_list = local_list + [str(i) for i in decor]
                        # correct for 0 index
                        list_to_add.append([int(i.strip('[]')) for i in decor])

                else:
                    # correct for 0 index
                    list_to_add = [int(list_to_parse.strip('[]'))-1]
                args.decoration_index = list_to_add
                args.ligcon = list_to_add[0]
            if (l[0] == '-ligffopt'):
                args.ffopt = l[1]
            if (l[0] == '-overwrite'):
                args.overwrite = l[1]
            # parse postprocessing arguments
            if (l[0] == '-postp'):
                args.postp = True
            if (l[0] == '-postqc'):
                args.postqc = l[1]
            if (l[0] == '-postdir'):
                args.postdir = line.split("#")[0].strip('\n')
                args.postdir = args.postdir.split('-postdir')[1]
                args.postdir = args.postdir.lstrip(' ')
            if (l[0] == '-pres'):
                args.pres = True
            if (l[0] == '-pwfninfo'):
                args.pwfninfo = True
            if (l[0] == '-pcharge'):
                args.pcharge = True
            if (l[0] == '-pgencubes'):
                args.pgencubes = True
            if (l[0] == '-porbinfo'):
                args.porbinfo = True
            if (l[0] == '-pdeloc'):
                args.pdeloc = True
            if (l[0] == '-pnbo'):
                args.pnbo = True
            # parse slab building arguments
            if (l[0] == '-slab_gen'):  # 0
                print('slab gen')
                args.slab_gen = True
            if (l[0] == '-unit_cell'):  # 1
                args.unit_cell = l[1]
            if (l[0] == '-cell_vector'):  # 2
                temp = [float(i.strip('(){}<>[],.'))
                        for i in l[1:]]  # list-of-lists

                args.cell_vector = [[temp[i] for i in [0, 1, 2]], [
                    temp[i] for i in [3, 4, 5]], [temp[i] for i in [6, 7, 8]]]

            if (l[0] == '-cif_path'):  # 3
                args.cif_path = l[1]
            if (l[0] == '-duplication_vector'):  # 4
                args.duplication_vector = [
                    int(i.strip('(){}<>[],.')) for i in l[1:]]
            if (l[0] == '-slab_size'):  # 5
                args.slab_size = [float(i.strip('(){}<>[],.')) for i in l[1:]]
            if (l[0] == '-miller_index'):  # 6
                args.miller_index = [int(i.strip('(){}<>[],.')) for i in l[1:]]
            if (l[0] == '-freeze'):  # 7
                try:
                    args.freeze = int(l[1].strip('(){}<>[],.'))
                except ValueError:
                    args.freeze = True
            if (l[0] == '-debug'):  # 8
                args.debug = True
            if (l[0] == '-expose_type'):  # 9
                args.expose_type = l[1]
            if (l[0] == '-shave_extra_layers'):  # 9
                args.shave_extra_layers = int(l[1])
            # TS generation routine
            if (l[0] == '-tsgen'):
                args.tsgen = True
            if (l[0] == '-substrate'):
                args.substrate = l[1:]
            if (l[0] == '-subcatoms'):
                args.subcatoms = l[1:]
            if (l[0] == '-mlig'):
                args.mlig = l[1:]
            if (l[0] == '-mligcatoms'):
                args.mligcatoms = l[1:]
            # cdxml import routine
            if (l[0] == '-cdxml'):
                args.cdxml = l[1:]
            # conformers
            if (l[0] == '-conformer'):
                args.conformer = True
            # parse place on slab options
            if (l[0] == '-place_on_slab'):  # 0
                args.place_on_slab = True
            if (l[0] == '-target_molecule'):  # 1
                args.target_molecule = l[1]
            if (l[0] == '-align_distance_method'):  # 2
                args.align_distance_method = l[1]
            if (l[0] == '-align_dist'):  # 3
                args.align_dist = float(l[1].strip('(){}<>[],.'))
            if (l[0] == '-align_method'):  # 4
                args.align_method = l[1]
            if (l[0] == '-object_align'):  # 5
                globs = globalvars()
                elements = globs.elementsbynum()
                if l[1] in elements:
                    args.object_align = l[1]
                else:
                    args.object_align = [
                        int(i.strip('(){}<>[],.')) for i in l[1:]]
            if (l[0] == '-surface_atom_type'):  # 6
                args.surface_atom_type = l[1]
            if (l[0] == '-num_surface_atoms'):  # 7
                args.num_surface_atoms = int(l[1].strip('()[]<>.'))
            if (l[0] == '-num_placements'):  # 8
                args.num_placements = int(l[1].strip('()[]<>.'))
            if (l[0] == '-coverage'):  # 9
                args.coverage = float(l[1].strip('()[]<>.'))
            if (l[0] == '-multi_placement_centering'):  # 10
                args.multi_placement_centering = float(l[1].strip('()[]<>.'))
            if (l[0] == '-control_angle'):  # 11
                args.control_angle = float(l[1].strip('()[]<>.'))
            if (l[0] == '-angle_control_partner'):  # 12
                args.angle_control_partner = int(l[1].strip('()[]<>.'))
            if (l[0] == '-angle_surface_axis'):  # 13
                args.angle_surface_axis = [
                    float(i.strip('(){}<>[],.')) for i in l[1:]]
            if (l[0] == '-duplicate'):  # 14
                args.duplicate = l[1]
            if (l[0] == '-surface_atom_ind'):  # 6
                args.surface_atom_ind = [
                    int(i.strip('(){}<>[],.')) for i in l[1:]]
        # control GUI prompt
            if (l[0] == '-rprompt'):
                args.rprompt = True
            # parse chain-builder arguments
            if (l[0] == '-chain'):
                print('chain true')
                args.chain = l[1]
            if (l[0] == '-chain_units'):
                args.chain_units = l[1]
            if (l[0] == '-chain_head'):
                args.chain_head = l[1]
            # parse analysis arguments
            if (l[0] == '-correlate'):
                args.correlate = l[1]
            if (l[0] == '-lig_only'):
                args.lig_only = True
            if (l[0] == '-simple'):
                args.simple = True
            if (l[0] == '-max_descriptors'):
                args.max_descriptors = [str(i) for i in l[1:]]
    if not set_rundir:
        args.rundir = os.path.join(os.path.abspath('.'), 'Runs')


# Parses command line arguments and prints help information
#  @param parser Parser object
#  @return Namespace of arguments

def parseall(parser):
    parser.add_argument("-i", help="input file")
    # hidden (non-user) arguments for GUI
    parser.add_argument("-rprompt", help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument("-gui", help=argparse.SUPPRESS,
                        action="store_true")           # gui placeholder
    parser.add_argument(
        "-checkdirb", help="CLI only: automatically ignore warning to replace existing folder", action="store_true")
    # directory removal check flag (what does this actually do?)
    parser.add_argument("-checkdirt", action="store_true")
    args = parser.parse_args()
    parseinputs_basic(parser, args)
    parseinputs_advanced(parser, args)
    parseinputs_slabgen(parser, args)
    parseinputs_autocorr(parser, args)
    parseinputs_chainb(parser, args)
    parseinputs_db(parser, args)
    parseinputs_inputgen(parser, args)
    parseinputs_postproc(parser, args)
    parseinputs_random(parser, args)
    parseinputs_binding(parser, args)
    # parseinputs_tsgen(parser,args)
    parseinputs_tsgen(parser, args)
    parseinputs_customcore(parser, args)
    parseinputs_naming(parser, args)
    return args

# Parses basic input options and prints help
#  @param *p Parser pointer


def parseinputs_basic(*p):
    parser = p[0]
    parser.add_argument(
        "-core", help=f"core structures currently available: {', '.join(getcores().split(' '))}")
    # specified in cleaninput
    parser.add_argument("-oxstate", help="oxidation state of the metal")
    parser.add_argument(
        "-coord", help="coordination such as 4,5,6", action="store_true")
    parser.add_argument("-geometry", help=f"geometry; currently available ones are {', '.join(getgeoms()[2])} which correspond to {', '.join(getgeoms()[1])}", action="store_true")
    parser.add_argument("-geo", help=f"geometry; currently available ones are {', '.join(getgeoms()[2])} which correspond to {', '.join(getgeoms()[1])}", action="store_true")
    parser.add_argument(
        "-lig",
        help="ligands to be included in complex; ligands.dict options display with command `molsimplify -h liganddict`")
    parser.add_argument(
        "-ligocc", help="number of corresponding ligands", action="store_true")  # e.g., 1,2,1
    parser.add_argument("-spin", help="spin multiplicity (e.g., 1 for singlet)")
    parser.add_argument("-spinmultiplicity", help="spin multiplicity (e.g., 1 for singlet)")
    parser.add_argument("-multiplicity", help="spin multiplicity (e.g., 1 for singlet)")
    # specified in cleaninput
    parser.add_argument(
        "-keepHs", help="force keep hydrogens, default auto for each ligand")
    parser.add_argument("-skipANN", help="skip attempting ANN predictions")
    parser.add_argument(
        "-rundir", help="directory for jobs, default ~/Runs", action="store_true")
    parser.add_argument(
        "-custom_data_dir", help="optional custom data directory to override the path in ~/.molSimplify"
    )
    parser.add_argument(
        "-smicat", help="connecting atoms corresponding to smiles. Indexing starts at 1 which is the default value as well. Use [] for multiple SMILES ligands, e.g., [1],[2]", action="store_true")
    parser.add_argument(
        "-ligloc", help="force location of ligands in the structure generation (default False)", default=False)
    parser.add_argument(
        "-ff", help="select force field for FF optimization. Available: (default) MMFF94, UFF, GAFF, Ghemical, XTB, GFNFF", default='uff')
    parser.add_argument(
        "-ffoption", help="select when to perform FF optimization. Options: B(Before), A(After), BA(Before and after), N(default, no force field), L(ligands.dict controlled)", default='N')
    parser.add_argument(
        "-ff_final_opt", help="optionally select different force field for "
        "final FF optimization after structure generation (defaults to option"
        " used in -ff). Available: MMFF94, UFF, GAFF, Ghemical, XTB, GFNFF",
        default=None)
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
        return 0

# Parses advanced input options and prints help
#  @param *p Parser pointer


def parseinputs_advanced(*p):
    parser = p[0]
    # advanced structure generation options
    parser.add_argument(
        "-nconfs", help="number of conformers to generate for multidentate smiles ligands, default 1", default='1')
    parser.add_argument(
        "-scoreconfs", help="attempt to filter out identical conformers and rank them by rmsd to the desired template, default False", default=False)
    parser.add_argument(
        "-charge", help="net complex charge. Recommended NOT to specify, by default this is calculated from the metal oxidation state and ligand charges")
    parser.add_argument(
        "-calccharge", help="automatically calculate net complex charge. By default this is ON", default=True)
    parser.add_argument(
        "-genall", help="generate complex both with and without FF opt, default False", action="store_true")  # geometry
    parser.add_argument("-decoration_index", help="list of indices on each ligand to decorate",
                        action="store_true")  # decoration indexes, one list per ligand
    parser.add_argument("-decoration", help="list of SMILES for each decoratation",
                        action="store_true")  # decoration, one list ligand
    parser.add_argument(
        "-ligalign", help="smart alignment of ligands in the structure generation (default False)", default=False)
    parser.add_argument(
        "-MLbonds", help="custom M-L bond length (Ang) for corresponding ligand", action="store_true")
    parser.add_argument(
        "-distort", help="randomly distort backbone. Ranges from 0 (no distortion) to 100, e.g., 20", default='0')
    parser.add_argument(
        "-langles", help="custom angles (polar theta, azimuthal phi) for corresponding ligand in degrees separated by '/', e.g., 20/30, 10/20", action="store_true")
    parser.add_argument(
        "-pangles", help="custom angles (polar theta, azimuthal phi) for corresponding connection points in degrees separated by '/', e.g., 20/30, 10/20", action="store_true")
    parser.add_argument("-oldANN", help=" use old (MCDL-25) ANN predictions")
    parser.add_argument(
        "-isomers", help='generates all possible isomers of a complex, support oct, thd, and sqp geometries')
    parser.add_argument(
        "-antigeoisomer", help='for tetradentate structures with geometric isomers, allows generation of the anti isomer (as opposed to the syn, used by default)')
    parser.add_argument(
        "-stereos", help='works in combination with -isomers. Generates a mirror image of each isomer complex')
    parser.add_argument(
        "-reportonly", help='add this flag if you just want the report, without actual structure generation. Currently does not support pentadentates')
    parser.add_argument(
        "-jobmanager", help='use jobmanager naming convention', default=False)
    parser.add_argument(
        "-no_tabs", help="add this flag to use spaces instead of tabs in written xyz files", default=False)
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
        return 0

# Parses slab builder options and prints help
#  @param *p Parser pointer


def parseinputs_slabgen(*p):
    parser = p[0]
    # slab builder input: controli
    parser.add_argument(
        "-slab_gen", help="enables slab generation/periodic extension", action="store_true")  # 0
    # slab builder input: required
    parser.add_argument(
        "-unit_cell", help="unit cell: path to xyz or instructions, see manual for details")  # 1
    parser.add_argument(
        "-cell_vector", help="unit cell lattice vector, list of 3 list of float (Ang)")  # 2
    parser.add_argument("-cif_path", help="path to cif file")  # 3
    parser.add_argument("-duplication_vector",
                        help="lattice vector repeats, list of 3 ints")  # 4
    parser.add_argument(
        "-slab_size", help="slab size, list of 3 floats (Ang)")  # 5
    # slab builder: optional
    parser.add_argument(
        "-miller_index", help="list of 3 int, miller indices")  # 6
    parser.add_argument(
        "-freeze", help="bool or int, bottom layers of cell to freeze")  # 7
    parser.add_argument(
        "-expose_type", help="str, symbol of atom type to expose (eg 'O')")  # 9
    parser.add_argument("-shave_extra_layers",
                        help="int, number of extra layers to shave")  # 10
    parser.add_argument(
        "-debug", help="debug feature to print stepwise slabs", action="store_true")  # 10
    # placement input: control
    parser.add_argument(
        "-place_on_slab", help="enables placement on slab", action="store_true")  # 0
    # placemnt input: required
    parser.add_argument("-target_molecule",
                        help="path to target molecule")  # 1
    parser.add_argument("-align_distance_method", help="align distance method",
                        choices=['chemisorption', 'physisorption', 'custom'])  # 2
    parser.add_argument("-align_dist", help="align distance, float")  # 3
    # placement input: optional
    parser.add_argument("-align_method", help="align method ",
                        choices=['center', 'staggered', 'alignpair'])  # 4
    parser.add_argument(
        "-object_align", help="atom symbol or index for alignment partner in placed object")  # 5
    parser.add_argument("-surface_atom_type",
                        help="atom symbol for surface aligment partner")  # 6
    parser.add_argument(
        "-num_surface_atoms", help="number of surface sites to attach per adsorbate")  # 7
    parser.add_argument("-num_placements",
                        help="number of copies of object to place.")  # 8
    parser.add_argument(
        "-coverage", help="coverage fraction, float between 0 and 1")  # 9
    parser.add_argument("-multi_placement_centering",
                        help="float between 0 and 1, controls centering of placement. Recommend leaving as default")  # 10
    parser.add_argument(
        "-control_angle", help="angle in degrees to rotate object axis to surface")  # 11
    parser.add_argument("-angle_control_partner",
                        help='atom index, int. Controls angle between object_align and this atom')  # 12
    parser.add_argument('-angle_surface_axis',
                        help='list of two floats, vector in surface plane to control angle relative to')  # 13
    parser.add_argument(
        '-duplicate', help="bool, duplicate asorbate above and below slab", action="store_true")  # 14
    parser.add_argument('-surface_atom_ind',
                        help="list of int, surface atoms to use by index")  # 15
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
        return 0

# Parses automated correlation analysis options and prints help
#  @param *p Parser pointer


def parseinputs_autocorr(*p):
    parser = p[0]
    parser.add_argument(
        '-correlate',
        help="path to file for analysis, should contain name,value,folder where name.xyz geo is located on each line")
    parser.add_argument(
        '-lig_only', action="store_true",
        help="set to true to force only whole ligand descriptors (if metal is constant etc)")  # 1
    parser.add_argument(
        '-simple', help="set to true to force only simple default autocorrelations")  # 1
    parser.add_argument(
        '-max_descriptors',
        help="maxium number of descriptors to to use, not reccomended. "
        "The algorithm chooses the most representative set and removing some of these can degrade the model"
    )  # 0
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses chain builder options and prints help
#  @param *p Parser pointer


def parseinputs_chainb(*p):
    parser = p[0]
    parser.add_argument(
        '-chain', help="SMILES string of monomer", action="store_true")  # 0
    parser.add_argument('-chain_units', help="int, number of monomers")  # 0
    parser.add_argument('-chain_head', help="SMILEs of chain terminator")  # 0
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses database search options and prints help
#  @param *p Parser pointer


def parseinputs_db(*p):
    parser = p[0]
    parser.add_argument(
        "-dbsearch", help="flag enabling db search", action="store_true")
    parser.add_argument(
        "-dbsim", help="deprecated, please use dbsmarts instead", action="store_true")
    parser.add_argument(
        "-dbcatoms", help="connection atoms for similarity search", action="store_true")
    parser.add_argument(
        "-dbresults", help="how many results for similary search or screening", action="store_true")
    parser.add_argument(
        "-dbfname", help="filename for database search, default is simres.smi", action="store_true")
    parser.add_argument(
        "-dbbase", help="database for search", action="store_true")
    parser.add_argument(
        "-dbsmarts", help="SMARTS string for substructure search", action="store_true")
    parser.add_argument(
        "-dbfinger", help="fingerprint for similarity search", action="store_true")
    parser.add_argument(
        "-dbatoms", help="number of atoms to be used in screening", action="store_true")
    parser.add_argument(
        "-dbbonds", help="number of bonds to be used in screening", action="store_true")
    parser.add_argument(
        "-dbarbonds", help="Number of aromatic bonds to be used in screening", action="store_true")
    parser.add_argument(
        "-dbsbonds", help="number of single bonds to be used in screening", action="store_true")
    parser.add_argument(
        "-dbmw", help="molecular weight to be used in screening", action="store_true")
    parser.add_argument(
        "-dbdissim", help="number of dissimilar results", action="store_true")
    parser.add_argument(
        "-dbnsearch", help="number of database entries to be searched, only for fastsearch", action="store_true")
    parser.add_argument(
        "-dballowedels", help="elements allowed in search, default all", action="store_true")
    parser.add_argument("-dbmaxsmartsmatches",
                        help="maximum instances of SMARTS pattern permitted, default unlimited", action="store_true")
    parser.add_argument(
        "-dbhuman", help="human-readable alternative to SMARTS/SMILES strings", action="store_true")
    parser.add_argument(
        "-dbdent", help="ligand denticity (requires -dbhuman)", action="store_true")
    parser.add_argument(
        "-dbconns", help="ligand coordinating elements (requires dbhuman)", action="store_true")
    parser.add_argument(
        "-dbhyb", help="hybridization (sp^n) of ligand coordinating elements (requires dbhuman)", action="store_true")
    parser.add_argument(
        "-dblinks", help="number of linking atoms (requires dbhuman)", action="store_true")
    parser.add_argument(
        "-dbfs", help="use fastsearch database if present", action="store_true")
    # add to DB commands
    parser.add_argument(
        "-ligadd", help=" add file/SMILES string to ligands available database ", action="store_true")
    parser.add_argument(
        "-ligname", help="name of ligand to be added", action="store_true")
    parser.add_argument(
        "-ligcon", help="list of connecting atoms for ligand to be added", action="store_true")
    parser.add_argument(
        "-ligffopt", action="store_true",
        help="so we ff optimize the ligand before or (B), after (A) placement, never (N) or both (BA)")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses input file generation options and prints help
#  @param *p Parser pointer


def parseinputs_inputgen(*p):
    parser = p[0]
    parser.add_argument(
        "-qccode", help="Code to use, only terachem (default), GAMESS and qchem are currently supported", default='terachem')
    parser.add_argument(
        "-runtyp", help="Run type (energy - default, minimize)", default='energy')
    parser.add_argument(
        "-method", help="Terachem method (e.g., b3lyp - default)", default=['b3lyp'])
    parser.add_argument(
        "-tc_fix_dihedral", help="Constrain sqp dihedrals (terachem only)?", action="store_true")
    parser.add_argument(
        "-mopac", help="Generate MOPAC (semiempirical) files?", action="store_true")
    parser.add_argument(
        "-basis", help="basis set for terachem or qchem job (default: LACVP*)", default='lacvps_ecp')
    parser.add_argument(
        "-dispersion", help="dispersion forces. Default: no e.g., d2,d3", action="store_true")
    parser.add_argument(
        "-qoption", help="extra arguments for TeraChem in syntax keyword value, e.g., maxit 100", action="store_true")
    parser.add_argument(
        "-exchange", help="exchange in qchem job (default b3lyp)", action="store_true")
    parser.add_argument(
        "-correlation", help="correlation in qchem job (default none)", action="store_true")
    parser.add_argument(
        "-remoption", help="extra arguments for qchem $rem block in syntax keyword value, e.g., INCFOCK 0", action="store_true")
    parser.add_argument(
        "-unrestricted", help="unrestricted calculation, default true", action="store_true")
    parser.add_argument(
        "-gbasis", help="GBASIS option in GAMESS e.g., CCT", action="store_true")
    parser.add_argument(
        "-ngauss", help="NGAUSS option in GAMESS e.g., N31", action="store_true")
    parser.add_argument(
        "-npfunc", help="NPFUNC option for diffuse functions in GAMESS e.g., 2", action="store_true")
    parser.add_argument(
        "-ndfunc", help="NDFUNC option for diffuse functions in GAMESS e.g., 1", action="store_true")
    parser.add_argument(
        "-sysoption", action="store_true",
        help="extra arguments for $SYSTEM GAMESS block in syntax keyword value, e.g., MWORDS 20")
    parser.add_argument(
        "-ctrloption", action="store_true",
        help="extra arguments for $CONTRL GAMESS block in syntax keyword value, e.g., ISPHER 1")
    parser.add_argument(
        "-scfoption", action="store_true",
        help="extra arguments for $SCF GAMESS block in syntax keyword value, e.g., DIIS .TRUE.")
    parser.add_argument(
        "-statoption", action="store_true",
        help="extra arguments for $STATPT GAMESS block in syntax keyword value, e.g., NSTEP 100")
    parser.add_argument(
        "-jsched", help="job scheduling system. Choices: SLURM or SGE", default='sge')
    parser.add_argument(
        "-jname", help="jobs main identifier", action="store_true")
    parser.add_argument(
        "-memory", help="memory reserved per thread for job file in G(default: 2G), e.g., 2", action="store_true")
    parser.add_argument(
        "-wtime", help="wall time requested in hours for queueing system (default: 168hrs) e.g., 8", action="store_true")
    parser.add_argument(
        "-queue", help="queue name e.g gpus", action="store_true")
    parser.add_argument(
        "-gpus", help="number of GPUS (default: 1)", action="store_true")
    parser.add_argument(
        "-cpus", help="number of CPUs (default: 1)", action="store_true")
    parser.add_argument(
        "-modules", help="modules to be loaded for the calculation", action="store_true")
    parser.add_argument(
        "-joption", help="additional options for jobscript", action="store_true")
    parser.add_argument(
        "-jcommand", help="additional commands for jobscript", action="store_true")
    parser.add_argument(
        "-jobdir", help="custom directory name for this job", action="store_true")
    # does this still do anything?
    parser.add_argument("-jid", help="job ID", action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses postprocessing options and prints help
#  @param *p Parser pointer


def parseinputs_postproc(*p):
    parser = p[0]
    parser.add_argument(
        "-postp", help="post process results", action="store_true")
    parser.add_argument(
        "-postqc", help="quantum chemistry code used. Choices: TeraChem or GAMESS", action="store_true")
    parser.add_argument(
        "-postdir", help="directory with results", action="store_true")
    parser.add_argument(
        "-pres", help="generate calculations summary", action="store_true")
    parser.add_argument(
        "-pdeninfo", help="calculate average properties for electron density", action="store_true")
    parser.add_argument(
        "-pcharge", help="calculate charges", action="store_true")
    parser.add_argument(
        "-pgencubes", help="generate cubefiles", action="store_true")
    parser.add_argument(
        "-pwfninfo", help="get information about wavefunction", action="store_true")
    parser.add_argument(
        "-pdeloc", help="get delocalization and localization indices", action="store_true")
    parser.add_argument(
        "-porbinfo", help="get information about MO", action="store_true")
    parser.add_argument(
        "-pnbo", help="post process nbo analysis", action="store_true")
    parser.add_argument(
        "-pdorbs", help="get information on metal d orbitals", action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses random generation options and prints help
#  @param *p Parser pointer


def parseinputs_random(*p):
    parser = p[0]
    parser.add_argument("-liggrp", "--liggrp",
                        help="ligand group for random generation ", action="store_true")
    parser.add_argument("-ligctg", "--ligctg",
                        help="ligand category for random generation", action="store_true")
    parser.add_argument(
        "-rkHs", "--rkHs", help="keep Hydrogens for random generation", action="store_true")
    parser.add_argument(
        "-rgen", "--rgen", help="number of random generated molecules", action="store_true")
    parser.add_argument(
        "-lignum", help="number of ligands for random generation", action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses binding species placement options and prints help
#  @param *p Parser pointer


def parseinputs_binding(*p):
    parser = p[0]
    parser.add_argument(
        "-bind", help="binding species, currently available: "+getbinds(), action="store_true")
    parser.add_argument("-bindnum", help="number of binding species copies for random placement",
                        action="store_true")  # different geometric arrangements for calculating binding energy
    parser.add_argument(
        "-nambsmi", help="name of SMILES string for binding species e.g., carbonmonoxide", action="store_true")
    parser.add_argument(
        "-maxd", help="maximum distance above cluster size for molecules placement maxdist=size1+size2+maxd",
        action="store_true")
    parser.add_argument(
        "-mind", help="minimum distance above cluster size for molecules placement mindist=size1+size2+mind",
        action="store_true")
    parser.add_argument(
        "-place", help="place binding species relative to core. Takes either angle (0-360) or ax/s for axial side",
        action="store_true")
    parser.add_argument(
        "-bcharge", "--bcharge", default='0', action="store_true",
        help="binding species charge, default 0")
    parser.add_argument(
        "-bphi", "--bphi", action="store_true",
        help="azimuthal angle phi for binding species, default random between 0 and 180")
    parser.add_argument(
        "-bref", "--bref", action="store_true",
        help="reference atoms for placement of extra molecules, default COM (center of mass), e.g., 1,5 or 1-5, Fe, COM")
    parser.add_argument(
        "-bsep", "--bsep", action="store_true",
        help="flag for separating extra molecule in input or xyz file")
    parser.add_argument(
        "-btheta", "--btheta", action="store_true",
        help="polar angle theta for binding species, default random between 0 and 360")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses transition state building version 2 options and prints help
#  @param *p Parser pointer


def parseinputs_tsgen(*p):
    parser = p[0]
    parser.add_argument("-tsgen", help="flag for enabling TS generation mode",
                        action="store_true", default=False)
    parser.add_argument("-substrate", help="small molecule substrate")
    parser.add_argument(
        "-subcatoms", help="index of the connecting atom in substrate")
    parser.add_argument(
        "-mlig", help="ligand name in the metal complex that the substrate connects with")
    parser.add_argument(
        "-mligcatoms", help="index of the connecting atom in the specified ligand in the metal complex", action="store_true")
    parser.add_argument("-cdxml", help="cdxml file name", action="store_true")
    parser.add_argument(
        "-conformers", help="flag for requesting metal-substrate TS conformation search", action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses ligand replacement options and prints help
#  @param *p Parser pointer


def parseinputs_customcore(*p):
    parser = p[0]
    parser.add_argument(
        "-replig", help="flag for replacing ligand at specified connection point", action="store_true")
    parser.add_argument(
        "-ccatoms", help="core connection atoms indices, indexing starting from 1")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0

# Parses file naming options and prints help
#  @param *p Parser pointer


def parseinputs_naming(*p):
    parser = p[0]
    parser.add_argument(
        "-name", help="custom name for complex", action="store_true")
    parser.add_argument(
        "-suff", help="additional suffix for jobs folder names", action="store_true")
    parser.add_argument(
        "-sminame", help="name for smiles species used in the folder naming, e.g., amm", action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0


# Prints ligands in ligands.dict
#  @param *p Parser pointer


def parseinputs_ligdict(*p):
    parser = p[0]

    available_ligands = getligs().split(' ')
    available_ligands.sort()  # Sorting the ligands in alphabetical order
    available_ligands = "\n".join(available_ligands)  # Converting back from a list to a string
    available_ligands = (
        "ligands to be included in complex; available ligands in the ligands dictionary at "
        "molSimplify/molSimplify/Ligands/ligands.dict are: \n%s}" % available_ligands
    )

    parser.add_argument(
        "-lig LIG", help=available_ligands, action="store_true")
    if len(p) == 1:  # only one input, printing help only
        args = parser.parse_args()
        return args
    elif len(p) == 2:  # two inputs, normal parsing
        args = p[1]
        parser.parse_args(namespace=args)
    return 0


def deserialize_json(filein):
    with open(filein, "r") as fo:
        args_dict = yaml.safe_load(fo)
    return args_dict


def args_parser_retrain():
    parser = argparse.ArgumentParser()
    parser.add_argument('-user')
    parser.add_argument('-pwd')
    parser.add_argument('-retrain')
    parser.add_argument('-infile')
    args = parser.parse_args()
    return args
