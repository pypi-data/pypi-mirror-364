"""Contains a class in order to parse a `.yaml` parameter file."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


class AtomConstant:
    """Define atoms constants.

    Attributes
    ----------
    self.__STACKING : `dict`
        A dictionary mapping atoms implied in planar groups, for given residue.

    self.__WW_SCALE : `dict`
        A dictionary with the different residue WW values.

    self.__BACKBONE_PHOSPHATE : `list`
        List of nucleic acid phosphate atoms.

    self.__BACKBONE_SUGAR : `list`
        List of nucleic acid sugar atoms.

    self.__NUCLEIC_BASES : `dict`
        List of nucleic acid bases atoms.

    self.__HPHIL_RNA_SUGAR : `float`
        Hydrophilic value for nucleic acid sugar atoms.

    self.__HPHIL_RNA_PHOSPHATE : `float`
        Hydrophilic value for nucleic acid phosphate atoms.

    self.__H_B_ACCEPTOR : `dict`
        A dictionary mapping atoms implied in hydrogen bond acceptor, for given
        residue.

    self.__H_B_DONOR : `dict`
        A dictionary mapping atoms implied in hydrogen bond donor, for given
        residue.

    self.__KEY : `list`
        A list of available keys.

    self.__VALUE : `list`
        A list containing all available dictionnaries.
    """

    # List of atoms implied in cycle, taking in consideration residues
    # and RNA bases.
    __STACKING: dict = {
        "ARG": "CZ NE NH1 NH2",
        "HIS": "CD2 CE1 CG ND1 NE2",
        "PHE": "CD1 CD2 CE1 CE2 CG CZ",
        "TRP": "CD1 CD2 CE2 CE3 CG CH2 CZ2 CZ3 NE1",
        "TYR": "CD1 CD2 CE1 CE2 CG CZ",
        "U": "N1 C2 N3 C4 C5 C6",
        "C": "N1 C2 N3 C4 C5 C6",
        "A": "N1 C2 N3 C4 C5 C6 N7 C8 N9",
        "G": "N1 C2 N3 C4 C5 C6 N7 C8 N9",
    }

    # List of side chain hydrophobicity scores, from Wimley and White Scale.
    # Values for RNA bases are taken from analogous protein residues.
    __WW_SCALE: dict = {
        "ALA" : -0.17,
        "ARG" : -0.81,
        "ASN" : -0.42,
        "ASP" : -1.23,
        "CYS" :  0.24,
        "GLN" : -0.58,
        "GLU" : -2.02,
        "GLY" : -0.01,
        "HIS" : -0.96,
        "ILE" :  0.31,
        "LEU" :  0.56,
        "LYS" : -0.99,
        "MET" :  0.23,
        "PHE" :  1.13,
        "PRO" : -0.45,
        "SER" : -0.13,
        "THR" : -0.14,
        "TRP" :  1.85,
        "TYR" :  0.94,
        "VAL" : -0.07,
        "U"   :  1.13,
        "C"   :  1.13,
        "A"   :  1.85,
        "G"   :  1.85,
    }

    __BACKBONE_PHOSPHATE = ["O5'", "P", "OP1", "OP2", "O3'"]

    __BACKBONE_SUGAR = ["C1'", "C2'", "C3'", "C4'", "C5'", "O2'", "O4'"]

    __NUCLEIC_BASES = {
        "U" : ["N1", "C2", "N3", "C4", "C5", "C6", "O2", "O4"],
        "C" : ["N1", "C2", "N3", "C4", "C5", "C6", "O2", "N4"],
        "A" : ["N1", "C2", "N3", "C4", "C5", "C6", "N7", "C8", "N9", "N6"],
        "G" : ["N1", "C2", "N3", "C4", "C5", "C6", "N7", "C8", "N9", "N2", "O6"],
    }

    __HPHIL_RNA_SUGAR = -0.13

    __HPHIL_RNA_PHOSPHATE = -2.02

    # List of atoms implied in hydrogen bond acceptor, taking in consideration
    # residues and RNA bases.
    # tuple format: (acceptor, tail_0, tail_1, head, hbond_fixed),
    #   - "tail_0" and "tail_1" are points whose middle-point is the "tail" position
    #   - the vector going from "tail" to "head" is the "direction" vector, which is used as pivot to calculate
    #     the angle of the bivariate gaussian. The direction vector is centered at the "acceptor" position for this purpose
    #   - "hbond_fixed" is a boolean that indicates if the fixed hbond model should be used
    __H_B_ACCEPTOR: dict = {
        "ALA" : [
            ("O","C","","O",False),
        ],
        "ARG" : [
            ("O","C","","O",False),
        ],
        "ASN" : [
            ("O","C","","O",False),
            ("OD1","CG","","OD1",False),
        ],
        "ASP" : [
            ("O","C","","O",False),
            ("OD1","CG","","OD1",False),
            ("OD2","CG","","OD2",False),
        ],
        "CYS" : [
            ("O","C","","O",False),
            ("SG","CB","","SG",False),
        ],
        "GLU" : [
            ("O","C","","O",False),
            ("OE1","CD","","OE1",False),
            ("OE2","CD","","OE2",False),
        ],
        "GLN" : [
            ("O","C","","O",False),
            ("OE1","CD","","OE1",False),
        ],
        "GLY" : [
            ("O","C","","O",False),
        ],
        "HIS" : [
            ("O","C","","O",False),
            ("ND1","CE1","CG","ND1",False),
        ],
        "ILE" : [
            ("O","C","","O",False),
        ],
        "LEU" : [
            ("O","C","","O",False),
        ],
        "LYS" : [
            ("O","C","","O",False),
        ],
        "MET" : [
            ("O","C","","O",False),
            ("SD","CG","","SD",False),
        ],
        "PHE" : [
            ("O","C","","O",False),
        ],
        "PRO" : [
            ("O","C","","O",False),
        ],
        "SER" : [
            ("O","C","","O",False),
            ("OG","CB","","OG",False),
        ],
        "THR" : [
            ("O","C","","O",False),
            ("OG1","CB","","OG1",False),
        ],
        "TRP" : [
            ("O","C","","O",False),
        ],
        "TYR" : [
            ("O","C","","O",False),
            ("OH","CZ","","OH",False),
        ],
        "VAL" : [
            ("O","C","","O",False),
        ],
        "U" : [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","P","O3'",False),
            ("O4'","C1'","C4'","O4'",False),
            ("O5'","C5'","P","O5'",False),
            ("OP1","P","","OP1",False),
            ("OP2","P","","OP2",False),
            ("O2","C2","","O2",False),
            ("O4","C4","","O4",False),
        ],
        "C" : [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","P","O3'",False),
            ("O4'","C1'","C4'","O4'",False),
            ("O5'","C5'","P","O5'",False),
            ("OP1","P","","OP1",False),
            ("OP2","P","","OP2",False),
            ("O2","C2","","O2",False),
            ("N3","C2","C4","N3",False),
        ],
        "A" : [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","P","O3'",False),
            ("O4'","C1'","C4'","O4'",False),
            ("O5'","C5'","P","O5'",False),
            ("OP1","P","","OP1",False),
            ("OP2","P","","OP2",False),
            ("N1","C2","C6","N1",False),
            ("N3","C2","C4","N3",False),
            ("N7","C5","C8","N7",False),
        ],
        "G" : [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","P","O3'",False),
            ("O4'","C1'","C4'","O4'",False),
            ("O5'","C5'","P","O5'",False),
            ("OP1","P","","OP1",False),
            ("OP2","P","","OP2",False),
            ("N3","C2","C4","N3",False),
            ("N7","C5","C8","N7",False),
            ("O6","C6","","O6",False),
        ],
    }

    # List of atoms implied in hydrogen bond donor, taking in consideration
    # residues and RNA bases.
    # tuple format: (donor, tail_0, tail_1, head, hbond_fixed),
    #   - "tail_0" and "tail_1" are points whose middle-point is the "tail" position
    #   - the vector going from "tail" to "head" is the "direction" vector, which is used as pivot to calculate
    #     the angle of the bivariate gaussian. The direction vector is centered at the "donor" position for this purpose
    #   - "hbond_fixed" is a boolean that indicates if the fixed hbond model should be used
    __H_B_DONOR: dict = { # note: in peptide bonds N is hbdonors_fixed, that's handled internally in the code
        "ALA": [
            ("N","C","CA","N",False),
        ],
        "ARG": [
            ("N","C","CA","N",False),
            ("NE","CD","CZ","NE",True),
            ("NH1","NH2","","CZ",True),
            ("NH1","NE","","CZ",True),
            ("NH2","NH1","","CZ",True),
            ("NH2","NE","","CZ",True),
        ],
        "ASN": [
            ("N","C","CA","N",False),
            ("ND2","OD1","","CG",True),
            ("ND2","CB","","CG",True),
        ],
        "ASP": [
            ("N","C","CA","N",False),
        ],
        "CYS": [
            ("N","C","CA","N",False),
            ("SG","CB","","SG",False),
        ],
        "GLU": [
            ("N","C","CA","N",False),
        ],
        "GLN": [
            ("N","C","CA","N",False),
            ("NE2","OE1","","CD",True),
            ("NE2","CG","","CD",True),
        ],
        "GLY": [
            ("N","C","CA","N",False),
        ],
        "HIS": [
            ("N","C","CA","N",False),
            ("NE2","CD2","CE1","NE2",True),
        ],
        "ILE": [
            ("N","C","CA","N",False),
        ],
        "LEU": [
            ("N","C","CA","N",False),
        ],
        "LYS": [
            ("N","C","CA","N",False),
            ("NZ","CE","","NZ",False),
        ],
        "MET": [
            ("N","C","CA","N",False),
        ],
        "PHE": [
            ("N","C","CA","N",False),
        ],
        "PRO": [
            ("N","CA","CD","N",True),
        ],
        "SER": [
            ("N","C","CA","N",False),
            ("OG","CB","","OG",False),
        ],
        "THR": [
            ("N","C","CA","N",False),
            ("OG1","CB","","OG1",False),
        ],
        "TRP": [
            ("N","C","CA","N",False),
            ("NE1","CD1","CE2","NE1",True),
        ],
        "TYR": [
            ("N","C","CA","N",False),
            ("OH","CZ","","OH",False),
        ],
        "VAL": [
            ("N","C","CA","N",False),
        ],
        "U": [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","","O3'",False),
            ("O5'","C5'","","O5'",False),
            ("N3","C6","","N3",True),
        ],
        "C": [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","","O3'",False),
            ("O5'","C5'","","O5'",False),
            ("N4","C5","","C4",True),
            ("N4","N3","","C4",True),
        ],
        "A": [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","","O3'",False),
            ("O5'","C5'","","O5'",False),
            ("N6","C5","","C6",True),
            ("N6","N1","","C6",True),
        ],
        "G": [
            ("O2'","C2'","","O2'",False),
            ("O3'","C3'","","O3'",False),
            ("O5'","C5'","","O5'",False),
            ("N1","C4","","N1",True),
            ("N2","N1","","C2",True),
            ("N2","N3","","C2",True),
        ],
    }

    __KEY: list = [
        "aromatic", "ww_scale", "backbone_phosphate", "backbone_sugar",
        "nucleic_bases", "hphil_rna_sugar", "hphil_rna_phosphate",
        "h_b_acceptor", "h_b_donor"
    ]
    __VALUE: list = [
        __STACKING, __WW_SCALE, __BACKBONE_PHOSPHATE, __BACKBONE_SUGAR,
        __NUCLEIC_BASES, __HPHIL_RNA_SUGAR, __HPHIL_RNA_PHOSPHATE,
        __H_B_ACCEPTOR, __H_B_DONOR
    ]

    def __setitem__(self, key: str, dictionary: dict):
        """Throws an exception if an setting is tried.

        Parameters
        ----------
        key : `str`
            The key to assign a parameter.

        dictionary : `dict`
            The dictionary to asign.

        Raises
        ------
        TypeError
            Throw when this method is called. Because it has to be not used.
        """
        raise TypeError(
            "[Err##] You cannot modify any attributes in this class!"
        )

    def __getitem__(self, key: str) -> dict:
        """Return a dictionary value corresponding to a given key.

        Parameters
        ----------
        key : `str`
            The key to fetch a dictionary.

        Returns
        -------
        `dict`
            The fetched dictionary.
        """
        if key not in self.__KEY:
            raise ValueError(
                f'[Err##] Key "{key}" not accepted. List of '
                f'accepted keys are "{self.__KEY}".'
            )

        return self.__VALUE[self.__KEY.index(key)]

    def keys(self) -> list:
        """Return keys linked to this object.

        Returns
        -------
        `list`
            The keys.
        """
        return self.__KEY

    def values(self) -> list:
        """Return dictionaries linked to this object.

        Returns
        -------
        `list`
            The values.
        """
        return self.__VALUE

    def items(self) -> zip:
        """Return keys, paired to their dictionaries, linked to this object.

        Returns
        -------
        `zip`
            The pairs key/value.
        """
        return zip(self.__KEY, self.__VALUE)

    def __str__(self) -> str:
        """Redefine the print() function for this object.

        Returns
        -------
        `str`
            The string representation of this object.
        """
        to_print: str = f"Available properties are: {self.__KEY}."

        return to_print


if __name__ == "__main__":
    atom_constant = AtomConstant()

    print(f"atom_constant[aromatic] return:\n {atom_constant['aromatic']}\n")
    print(atom_constant)
