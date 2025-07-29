"""Common utilities for DDPC."""

from pathlib import Path

from ase.atoms import Atoms
from loguru import logger
from pymatgen.core import Structure
from pymatgen.transformations.advanced_transformations import CubicSupercellTransformation
from spglib.spglib import find_primitive

from ddpc.io.structure import read_single_structure, read_structure, write_structure


@logger.catch
def find_prim(p: str | Path, op: str | Path, fmt: str | None, symprec: float) -> None:
    """Find primitive cell of a crystal structure.

    This function reads a crystal structure file, finds its primitive cell using
    spglib, and writes the result to an output file.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the input structure file.
    op : str or pathlib.Path
        Path to the output file for the primitive structure.
    fmt : str or None
        Output file format. If None, format is determined from file extension.
    symprec : float
        Symmetry precision for spglib primitive cell finding.

    Raises
    ------
    ValueError
        If the input structure has no cell information or if spglib fails
        to find the primitive cell.
    """
    # 1. read to Atoms
    s = read_structure(p)
    if isinstance(s, Atoms):
        pass
    else:
        logger.warning("got multiple Atoms, will use the 1st one.")
        s = s[0]
    if not s.cell.array.any():
        raise ValueError(
            "The input structure has no cell information, "
            "please provide a structure with cell info."
        )

    # 2. find primitive Atoms
    lat = tuple(s.cell.array)
    spo = tuple(s.get_scaled_positions())
    num = tuple(s.numbers)
    res = find_primitive(cell=(lat, spo, num), symprec=symprec, angle_tolerance=-1)
    if res and len(res) == 3:
        lattice, scaled_positions, numbers = res
    else:
        raise ValueError("spglib failed to find primitive cell.")
    prim = Atoms(
        numbers=numbers,
        cell=lattice,
        scaled_positions=scaled_positions,
    )

    # 3. write out
    Path(op).parent.mkdir(parents=True, exist_ok=True)
    write_structure(op, prim, fmt)

    # 4. print info and visualization hint
    logger.info(f"original: {s}")
    logger.info(f"primitive: {prim}")
    logger.info("Hint: you may drag the output file into Vesta/OVITO,")
    logger.info(f" or run 'ase gui {op}' to check")


@logger.catch
def orthogonalize_cell(atoms: Atoms, mlen: float) -> Atoms:
    """Search for an orthogonalized supercell of the input structure.

    This function uses pymatgen's CubicSupercellTransformation to find a
    supercell with orthogonal lattice vectors (a ⊥ b ⊥ c). The transformation
    searches for the minimal supercell that satisfies the orthogonality
    constraints within the specified maximum length.

    Parameters
    ----------
    atoms : ase.atoms.Atoms
        Input crystal structure as an ASE Atoms object.
    mlen : float
        Maximum allowed lattice vector length for the orthogonalized cell.
        The search will fail if no orthogonal supercell can be found within
        this constraint.

    Returns
    -------
    ase.atoms.Atoms
        Orthogonalized supercell as an ASE Atoms object with perpendicular
        lattice vectors.

    Raises
    ------
    Exception
        If pymatgen fails to find an orthogonal supercell within the maximum
        length constraint, or if the transformation fails for any other reason.

    Notes
    -----
    The function uses the following transformation parameters:

    - min_length: 3.0 Å (minimum lattice vector length)
    - max_length: mlen (user-specified maximum)
    - allow_orthorhombic: True (allows orthorhombic cells)
    - angle_tolerance: 1e-3 (tolerance for 90° angles)
    - step_size: 0.1 (search step size)
    """
    logger.debug("Searching minimal orthogonalized cell, this may take a while...")
    pmg_stru = Structure.from_ase_atoms(atoms)
    logger.debug(f"{pmg_stru=}")

    orthed_s = CubicSupercellTransformation(
        min_atoms=None,
        max_atoms=None,
        min_length=3.0,
        max_length=mlen,
        force_diagonal=False,
        force_90_degrees=False,
        allow_orthorhombic=True,
        angle_tolerance=1e-3,
        step_size=0.1,
    ).apply_transformation(pmg_stru)
    logger.debug(f"{orthed_s=}")

    ret = orthed_s.to_ase_atoms()
    logger.debug(f"{ret=}")

    return ret


@logger.catch
def find_orth(p: str | Path, op: str | Path, fmt: str | None, mlen: float) -> None:
    """Create an orthogonalized supercell with perpendicular lattice vectors.

    This function reads a crystal structure, finds an orthogonalized supercell
    where all lattice vectors are perpendicular (a ⊥ b ⊥ c), and writes the
    result to an output file.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the input structure file.
    op : str or pathlib.Path
        Path to the output file for the orthogonalized structure.
    fmt : str or None
        Output file format. If None, format is determined from file extension.
    mlen : float
        Maximum allowed lattice vector length for the orthogonalized cell.

    Raises
    ------
    ValueError
        If the input structure has no cell information.
    Exception
        If the orthogonalization process fails or no suitable supercell
        can be found within the maximum length constraint.
    """
    # 1. read to Atoms
    s = read_structure(p)
    if isinstance(s, Atoms):
        pass
    else:
        logger.warning("got multiple Atoms, will use the 1st one.")
        s = s[0]
    if not s.cell.array.any():
        raise ValueError(
            "The input structure has no cell information, "
            "please provide a structure with cell info."
        )

    # 2. ortho
    ortho_atoms = orthogonalize_cell(s, mlen)

    # 3. write to file
    write_structure(op, ortho_atoms, fmt)


@logger.catch
def scale_atom_pos(p: str | Path, op: str | Path) -> None:
    """Convert structure file to POSCAR format with scaled (fractional) positions.

    This function reads a crystal structure from any supported format and writes
    it as a VASP POSCAR file with atomic positions expressed in fractional
    coordinates (Direct format).

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the input structure file.
    op : str or pathlib.Path
        Path to the output POSCAR file.

    Raises
    ------
    ValueError
        If the input structure has no cell information (lattice vectors).
    """
    # 1. read to Atoms
    s = read_single_structure(p)
    if not s.cell.array.any():
        raise ValueError(
            "The input structure has no cell information, "
            "please provide a structure with cell info."
        )

    # 2. write out POSCAR with scaled positions
    write_structure(op, s, "vasp", direct=True)
    logger.info(f"written {op} with scaled positions.")
