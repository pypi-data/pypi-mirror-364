"""Contains a class with strategy to fill a grid with H-bond properties."""

# pylint: disable=duplicate-code
# THERE IS NO DUPLICATE CODE, THESE ARE IMPORT PYLINT!!!

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = [
    "diego.barqueromorera@studenti.unitn.it",
    "lucas.rouaud@gmail.com",
]
__copyright__ = "MIT License"

import MDAnalysis as md

# [N]
import numpy as np

# [C]
from .class_property import StrategyProperty

# [G]
from ..class_stamp import Stamp

# [K]
from ..kernel import BivariateGaussianKernel

from ...utils.hbond_triplet import HBondTriplet


# pylint: enable=duplicate-code


class StrategyHBond(StrategyProperty):
    """A class for defining strategies to fill a grid with H-bond
    properties.

    Inheritance
    -----------
    This class is the child of `StrategyProperty`. Check this one for other
    **attributes** and **methods** definitions.

    Attributes
    ----------
    self.__key : `str`
        The key to switch between acceptor or donnor mode.

    self.__all_atoms : `md.AtomGroup`
        The atoms of the molecule to analyze, with or without hydrogens.

    self.__res_atoms : `md.AtomGroup`
        The atoms of the current residue being analyzed.

    self.__processed_interactors : `set`
        A set to keep track of processed interactors to avoid double counting.
        Relevant for HBDonors.
    """

    def __init__(self, name: str, atom_constant: object, key: str):
        """Define the strategy for H-bond properties computation.

        Parameters
        ----------
        name : `str`
            Name of the property.

        atom_constant : `AtomConstant`
            An object containing constant linked to atoms.

        key : `str`
            Which analyze to use between acceptor and donor. Respectively,
            gives the key "h_b_acceptor" or "h_b_donor" to this parameter to
            specify the wanted method.

        Raises
        ------
        ValueError
            Throw an error when the given key is not "h_b_acceptor" or
            "h_b_donor".
        """
        super().__init__(name, atom_constant)

        if key not in ["h_b_acceptor", "h_b_donor"]:
            raise ValueError(
                f'[Err##] Key "{key}" not accepted. List of '
                'accepted keys are "["h_b_acceptor", '
                '"h_b_donor"]".'
            )

        self.__key: str = key
        self.__all_atoms: md.AtomGroup
        self.__res_atoms: md.AtomGroup
        self.__processed_interactors: set = set()


    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Populate a grid following H-bond properties.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        v_mu_free: np.ndarray
        v_sigma_free: np.ndarray
        v_mu_fixed: np.ndarray | None
        v_sigma_fixed: np.ndarray | None

        find_tail_head_positions: callable

        h_bond_kernel_free: BivariateGaussianKernel
        stamp_free: Stamp
        h_bond_kernel_fixed: BivariateGaussianKernel | None = None
        stamp_fixed: Stamp | None = None


        if self.__key == "h_b_acceptor":
            v_mu_free = grid_object.yaml["function_h_bond_acceptor_mu"]
            v_sigma_free = grid_object.yaml["function_h_bond_acceptor_sigma"]
            v_mu_fixed = None
            v_sigma_fixed = None
            find_tail_head_positions = self.__find_tail_head_positions_hba

        elif self.__key == "h_b_donor":
            v_mu_free = grid_object.yaml["function_h_bond_donor_free_mu"]
            v_sigma_free = grid_object.yaml["function_h_bond_donor_free_sigma"]
            v_mu_fixed = grid_object.yaml["function_h_bond_donor_fixed_mu"]
            v_sigma_fixed = grid_object.yaml["function_h_bond_donor_fixed_sigma"]
            find_tail_head_positions = self.__find_tail_head_positions_hbd


        h_bond_kernel_free = BivariateGaussianKernel(
            radius=(
                v_mu_free[1] + v_sigma_free[1][1] ** (1 / 2)
                * grid_object.yaml["other_gaussian_kernel_scalar"]
            ),
            delta=grid_object.delta,
            v_mu=v_mu_free,
            v_sigma=np.linalg.inv(v_sigma_free), # Pre-inversing the matrix.
            is_stacking=False,
        )
        stamp_free = Stamp(
            grid=grid,
            grid_origin=grid_object.coord[0],
            delta=grid_object.delta,
            kernel=h_bond_kernel_free,
        )

        if self.__key == "h_b_donor":
            h_bond_kernel_fixed = BivariateGaussianKernel(
                radius=(
                    v_mu_fixed[1] + v_sigma_fixed[1][1] ** (1 / 2)
                    * grid_object.yaml["other_gaussian_kernel_scalar"]
                ),
                delta=grid_object.delta,
                v_mu=v_mu_fixed,
                v_sigma=np.linalg.inv(v_sigma_fixed), # Pre-inversing the matrix.
                is_stacking=False,
            )
            stamp_fixed = Stamp(
                grid=grid,
                grid_origin=grid_object.coord[0],
                delta=grid_object.delta,
                kernel=h_bond_kernel_fixed,
            )

        for triplet in self.__iter_triplets(grid_object):
            find_tail_head_positions(triplet, grid_object)
            vec_direction = triplet.get_direction_vector()

            if (triplet.pos_interactor is None) or (vec_direction is None):
                continue

            if self.__key == "h_b_donor" and triplet.hbond_fixed:
                h_bond_kernel_fixed.refresh_orientation(coordinate=vec_direction)
                stamp_fixed.refresh_orientation(kernel=h_bond_kernel_fixed.kernel())
                stamp_fixed.stamp_kernel(center=triplet.pos_interactor)
            else:
                h_bond_kernel_free.refresh_orientation(coordinate=vec_direction)
                stamp_free.refresh_orientation(kernel=h_bond_kernel_free.kernel())
                stamp_free.stamp_kernel(center=triplet.pos_interactor)


    def __iter_triplets(self, grid_object):
        """Iterate over the triplets of H-bond acceptors or donors."""
        table_hbond: dict = self._atom_constant[self.__key]

        self.__all_atoms = grid_object.molecule_with_h \
            if grid_object.use_structure_hydrogens \
            else grid_object.molecule

        for res in self.__all_atoms.residues:
            hbond_tuples = table_hbond.get(res.resname)
            if hbond_tuples is None: continue # skip weird residues

            self.__processed_interactors.clear()

            for hbond_tuple in hbond_tuples:
                if not hbond_tuple: continue  # skip residues without HBond pairs

                triplet = HBondTriplet(res, *hbond_tuple)

                if triplet.interactor in self.__processed_interactors:
                    continue

                self.__res_atoms = self.__all_atoms.select_atoms(triplet.str_this_res)
                triplet.set_pos_interactor(self.__res_atoms)

                if self.__key == "h_b_donor" and grid_object.use_structure_hydrogens:
                    for hydrogen in triplet.get_interactor_bonded_hydrogens(self.__res_atoms):
                        triplet.pos_tail = triplet.pos_interactor
                        triplet.pos_head = hydrogen.position
                        triplet.hbond_fixed = True
                        self.__processed_interactors.add(triplet.interactor)
                        yield triplet

                if triplet.pos_head is None: # use_structure_hydrogens falls back to "no-hydrogen" model if no hydrogens found
                    yield triplet


    def __find_tail_head_positions_hba(self, triplet: HBondTriplet, grid_object) -> None:
        """Infer the correct positions of the "tail" and "head" points of a H-bond acceptor.

        Parameters
        ----------
        triplet : `HBondTriplet`
            The triplet object with details about the H-bond acceptor atom names.

        grid_object : `Grid`
            The grid object to access all attributes.
        """

        triplet.set_pos_head(self.__res_atoms)

        ############################### TAIL POSITION
        ### special cases for RNA
        if grid_object.yaml["other_macromolecule"] == "nucleic":
            if triplet.interactor == "O3'": # tail points are in different residues
                triplet.set_pos_tail_custom(
                    atoms = self.__all_atoms,
                    query_t0 = triplet.str_this_res,
                    query_t1 = triplet.str_next_res
                )
                return

        triplet.set_pos_tail(self.__res_atoms)


    def __find_tail_head_positions_hbd(self, triplet: HBondTriplet, grid_object) -> None:
        """Infer the correct positions of the "tail" and "head" points of a H-bond donor.

        Parameters
        ----------
        triplet : `HBondTriplet`
            The triplet object with details about the H-bond donor atom names.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        def _has_prev_res(atoms, triplet: HBondTriplet) -> bool:
            return len(atoms.select_atoms(triplet.str_prev_res)) > 0

        def _has_next_res(atoms, triplet: HBondTriplet) -> bool:
            return len(atoms.select_atoms(triplet.str_next_res)) > 0

        # head position is already set for succesful use_structure_hydrogens iterations
        if triplet.pos_head is not None:
            return

        triplet.set_pos_head(self.__res_atoms)

        ############################### TAIL POSITION
        ### special cases for protein
        if grid_object.yaml["other_macromolecule"] == "protein":
            if triplet.resname == "PRO": # donor only if there is no previous residue
                if _has_prev_res(self.__all_atoms, triplet): return

            elif triplet.interactor == "N": # tail points are in different residues
                if _has_prev_res(self.__all_atoms, triplet):
                    triplet.set_pos_tail_custom( # N of peptide bond
                        atoms = self.__all_atoms,
                        query_t0 = triplet.str_prev_res,
                        query_t1 = triplet.str_this_res
                    )
                    triplet.hbond_fixed = True
                    return

                triplet.set_pos_tail_custom( # N of N-terminus
                    atoms = self.__all_atoms,
                    query_t0 = f"{triplet.str_this_res} and name CA",
                    query_t1 = f"{triplet.str_this_res} and name CA"
                )
                triplet.hbond_fixed = False
                return


        ### special cases for RNA
        if grid_object.yaml["other_macromolecule"] == "nucleic":
            if triplet.interactor == "O3'": # donor only if there is no next residue
                if _has_next_res(self.__all_atoms, triplet): return

            elif triplet.interactor == "O5'": # donor only if there is no previous residue
                if _has_prev_res(self.__all_atoms, triplet): return

        triplet.set_pos_tail(self.__res_atoms)
