"""Defines the Atom object"""

import numpy as np
from collections import Counter


class Atom(object):
    """
    Object representing an atom.

    Sometimes also used to represent point charges as atoms of element "point".
    Several functions are present like translate or find_centroid.

    Attributes
    ----------
    x,y,z : floats
        Cartesian coordinates
    q : float
        Partial atomic charge
    connectivity : frozenset of tuples
        The set is ((atom kind,connectivity order),amount) and is set via a
        function which takes the connectivity matrix as argument
    kind : tuple
        Tuple of (atom element,connectivity). This defines the kind of atom

    """

    def __init__(self, elemIn="H", xIn=0.0, yIn=0.0, zIn=0.0, qIn=0.0, num=1):
        self.elem = elemIn
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.q = 0.0
        self.num = 1
        self.connectivity = None
        self.kind = None

        # deal with some sneaky int that may be disguised as float
        try:
            self.x = float(xIn)
            self.y = float(yIn)
            self.z = float(zIn)
            self.q = float(qIn)

        except ValueError:
            print("Some coordinates or charges cannot be cast to float!")

        # to string methods to be used mainly for debugging and .qc file
    def __repr__(self):
        return "{:>6} {:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z, self.q)

    def __str__(self):
        return "{:>6} {:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z, self.q)

        # equality function
    def __eq__(self, other):
        return self.elem.lower() == other.elem.lower() and self.x == other.x and self.y == other.y and self.z == other.z and self.q == other.q

    def xyz_str(self):
        """Return a string of the atom in xyz format"""
        return "{:>6} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z)

    def dist(self, x1, y1, z1):
        """Return distance of the atom from a point"""
        r = np.sqrt((self.x - x1) ** 2 + (self.y - y1) ** 2 + (self.z - z1) ** 2)
        return r

    def dist_lat(self, x1, y1, z1, aVec, bVec, cVec):
        """
        Find the shortest distance to a point in a periodic system.

        Parameters
        ----------
        x1,y1,z1 : floats
            Cartesian coordinates of the target point
        aVec,bVec,cVec : 3x1 array-likes
            Unit cell vectors

        Returns
        -------
        rMin : float
            Minimal distance to the point
        x3,y3,z3 : floats
            Coordinates of the closest image to the point

        """
        # null vector
        nVec = (0, 0, 0)
        # negative vectors
        aVecN = [-i for i in aVec]
        bVecN = [-i for i in bVec]
        cVecN = [-i for i in cVec]

        # sets comprised of the lattice vector,
        # the null vector and the negative lattice vector
        aSet = [aVec, nVec, aVecN]
        bSet = [bVec, nVec, bVecN]
        cSet = [cVec, nVec, cVecN]

        # minimum r distance
        rMin = float("inf")

        # loop over all possible translations of the input point
        for trans1 in aSet:
            for trans2 in bSet:
                for trans3 in cSet:
                    x2 = x1 + trans1[0] + trans2[0] + trans3[0]
                    y2 = y1 + trans1[1] + trans2[1] + trans3[1]
                    z2 = z1 + trans1[2] + trans2[2] + trans3[2]
                    r = np.sqrt((self.x - x2) ** 2 + (self.y - y2)
                             ** 2 + (self.z - z2) ** 2)
                    # if this particular translation of the point is the closest
                    # to the atom so far
                    if r < rMin:
                        rMin = r
                        # image coordinates
                        x3 = x2
                        y3 = y2
                        z3 = z2
        return rMin, x3, y3, z3

    def translated(self, x1, y1, z1):
        "Return a new atom which is a translated copy."
        xout, yout, zout = self.x, self.y, self.z
        xout += x1
        yout += y1
        zout += z1
        outAtom = Atom(self.elem, xout, yout, zout, self.q)
        return outAtom

    def translate(self, x1, y1, z1):
        "Translate the atom by some vector."
        self.x += x1
        self.y += y1
        self.z += z1
        return

    def electrons(self):
        # FIND A MONKEY THAT CAN COMPLETE THIS METHOD
        # used for Bader
        total = 0
        valence = 0

        element = self.elem.lower()
        if element == "h":
            total = 1
            valence = 1
        elif element == "c":
            total = 6
            valence = 4
        elif element == "n":
            total = 7
            valence = 5
        elif element == "o":
            total = 8
            valence = 6

        return (valence, total)

    periodic = [("H",1),("C",6),("N",7),("O",8)]

    def num_to_elem(self,num):
        """
        Sets the element symbol according to input atomic number

        Parameters
        ----------
        num : int
            Atomic number of the element
        """
        periodic = [("H",1),("C",6),("N",7),("O",8)]
        for element in periodic:
            if num == element[1]:
                self.elem = element[0]
        return


    def set_connectivity(self, in_atoms, in_row):
        """
        Set the connectivity and the kind of the atom.

        This function needs a row of a connectivity matrix which can be obtained
        with functions from assign_charges.py

        Parameters
        ----------
        in_atoms : list of atoms
            Atoms in the system of which this atom is a part
        in_row : 1-d array-like
            The row of the connectivity matrix of in_atoms which corresponds to
            this atom

        """
        links = []
        for i, atom in enumerate(in_atoms):
            if in_row[i] != 0:
                links.append((in_atoms[i].elem, in_row[i]))
        self.connectivity = frozenset(Counter(links).most_common())
        self.kind = (self.elem, self.connectivity)
        return