# @file atom3D.py
#  Defines atom3D class and contains useful manipulation/retrieval routines.
#
#  Written by Kulik Group
#
#  Department of Chemical Engineering, MIT

import numpy as np
from typing import List, Optional
from molSimplify.Classes.globalvars import globalvars


class atom3D:
    """
    atom3D class. Base class in molSimplify for representing an element.

    Parameters
    ----------
        Sym : str, optional
            Symbol for atom3D instantiation. Element symbol. Default is 'C'.
        xyz : list, optional
            List of coordinates for new atom. Default is [0.0, 0.0, 0.0].
            Units of angstroms.
        name : str, optional
            Unique identifier for atom 3D instantiation. Default is False.
        partialcharge : int, optional
            Charge assigned to atom when added to mol. Default is None.
    """

    def __init__(self,
                 Sym: str = 'C',
                 xyz: Optional[List[float]] = None,
                 name: Optional[str] = None,
                 partialcharge: Optional[float] = None,
                 Tfactor=0,
                 greek='',
                 occup=1.00,
                 loc='',
                 line=""):

        # Element symbol
        self.sym = Sym
        self.partialcharge = partialcharge
        globs = globalvars()
        amass = globs.amass()
        if Sym not in amass:  # Assign default values if not in dictionary.
            print(f"We didn't find the atomic mass of {Sym} in the dictionary. Assigning default value of 12!\n")
            # Atomic mass
            self.mass = 12.0  # default atomic mass
            # Atomic number
            self.atno = 6  # default atomic number
            # Covalent radius
            self.rad = 0.75  # default atomic radius
        else:
            self.mass = amass[Sym][0]
            self.atno = amass[Sym][1]
            self.rad = amass[Sym][2]
        # Flag for freezing in optimization
        self.frozen = False
        # Flag for atom name
        # NOTE: does not compare to None because empty string would not be valid and
        # some parts of molSimplify still instantiate atom3D with name=False
        if name:
            self.name = name
        else:
            self.name = Sym

        # Coordinates
        if xyz is None:
            xyz = [0.0, 0.0, 0.0]
        elif not isinstance(xyz, (list, np.ndarray)) or len(xyz) != 3:
            raise ValueError('xyz should be a list of length 3.')
        try:
            np.array(xyz, dtype=np.float64)
        except ValueError:
            raise ValueError('List xyz should consist of numbers.')
        self.__xyz = list(xyz)

        # Temperature factor (only useful for proteins)
        self.Tfactor = Tfactor

        # Greek letter (e.g. alpha carbon - only useful for proteins)
        if greek == '':
            self.greek = Sym
        else:
            self.greek = greek

        # Occupancy (only useful for proteins)
        self.occup = occup

        # EDIA score (only useful for proteins)
        self.EDIA = 0

        # Conformation (only useful for proteins)
        self.loc = ""

        # PDB line (only useful for proteins)
        self.line = line

    def __repr__(self):
        return f"atom3D(Sym={self.sym}, xyz={self.__xyz})"

    # TODO: uncomment this once protein3D has a better implementation than
    # hashing of a mutable object!
    # def __eq__(self, other):
    #     if isinstance(other, self.__class__):
    #         return self.__dict__ == other.__dict__
    #     else:
    #         return False

    def coords(self):
        """
        Get coordinates of a given atom.

        Returns
        -------
            coords : list
                List of coordinates in X, Y, Z format.
                Units of angstroms.
        """

        coords = self.__xyz.copy()
        return coords

    def distance(self, atom2):
        """
        Get distance from one atom3D class to another.

        Parameters
        ----------
            atom2 : atom3D
                atom3D class of the atom to measure distance from.

        Returns
        -------
            dist : float
                Distance in angstroms.
        """

        xyz = self.coords()
        point = atom2.coords()
        dist = np.linalg.norm(np.array(xyz)-np.array(point))
        return dist

    def distancev(self, atom2):
        """
        Get distance vector from one atom3D class to another.

        Parameters
        ----------
            atom2 : atom3D
                atom3D class of the atom to measure distance from.

        Returns
        -------
            dist_list : list
                List of distances in vector form: [dx, dy, dz] with units of angstroms.
        """

        xyz = self.coords()
        point = atom2.coords()
        dist_list = list(np.array(xyz)-np.array(point))
        return dist_list

    def ismetal(self, transition_metals_only=True, include_X=False) -> bool:
        """
        Identify whether an atom is a metal.

        Parameters
        ----------
            transition_metals_only : bool, optional
                Identify only transition metals.
                Default is True.
            include_X : bool, optional
                Whether "X" atoms are considered metals.
                Default is False.

        Returns
        -------
            metal : bool
                Bool for whether or not an atom is a metal.
        """

        return self.sym in globalvars().metalslist(transition_metals_only=transition_metals_only,
            include_X=include_X)

    def setcoords(self, xyz):
        """
        Set coordinates of an atom3D class to a new location.

        Parameters
        ----------
            xyz : list
                List of coordinates, has length 3: [X, Y, Z]
                Units of angstroms.
        """

        if not isinstance(xyz, (list, np.ndarray)) or len(xyz) != 3:
            raise ValueError('xyz should be a list of length 3.')
        try:
            np.array(xyz, dtype=np.float64)
        except ValueError:
            raise ValueError('List xyz should consist of numbers.')

        self.__xyz = list(xyz)

    def symbol(self) -> str:
        """
        Return symbol of atom3D.

        Returns
        -------
            symbol : str
                Element symbol for atom3D class.
        """

        return self.sym

    def mutate(self, newType='C'):
        """
        Mutate an element to another element in the atom3D.

        Parameters
        ----------
            newType : str, optional
                Element name for new element. Default is 'C'.
        """

        globs = globalvars()
        amass = globs.amass()
        if newType not in list(amass.keys()):
            print(f'Error, unknown atom type transformation to {newType}.')
            print('No changes made.')
        else:
            self.mass = amass[newType][0]
            self.atno = amass[newType][1]
            self.rad = amass[newType][2]
            self.name = newType
            self.sym = newType

    def translate(self, dxyz):
        """
        Move the atom3D by a displacement vector.

        Parameters
        ----------
            dxyz : list
                Displacement vector of length 3: [dx, dy, dz].
                Units of angstroms.
        """

        self.__xyz = list(np.array(self.__xyz)+np.array(dxyz))

    def setEDIA(self, score):
        """
        Sets the EDIA score of an individual atom3D.

        Parameters
        ----------
            score : float
                Desired EDIA score of atom
        """

        self.EDIA = score
