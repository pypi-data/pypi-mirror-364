"""Read DS-PAW specified .as format file to ASE atoms."""

import re
from pathlib import Path
from typing import Any

import numpy as np
from ase.atoms import Atoms
from loguru import logger

from ddpc.io.utils import absf, remove_comments


@logger.catch
def read(p: Path | str = "structure.as") -> Atoms:
    """Read DS-PAW atomic structure format file and convert to ASE Atoms object.

    This function reads DS-PAW's custom .as format files which support advanced
    features like lattice constraints, atomic position constraints, and magnetic
    moments. The format is used by the DS-PAW DFT code for structure input.

    Parameters
    ----------
    p : pathlib.Path or str, default "structure.as"
        Path to the DS-PAW .as format structure file.

    Returns
    -------
    ase.atoms.Atoms
        ASE Atoms object containing the crystal structure with:

        - Atomic positions (Cartesian or fractional coordinates)
        - Unit cell lattice vectors
        - Magnetic moments (if specified)
        - Constraint information stored in the info dictionary

    Notes
    -----
    The DS-PAW .as format supports:

    - Lattice vector constraints (Fix_x, Fix_y, Fix_z per vector)
    - Atomic position constraints (Fix, Fix_x, Fix_y, Fix_z per atom)
    - Magnetic moments (collinear: Mag, non-collinear: Mag_x, Mag_y, Mag_z)
    - Both Cartesian and Direct (fractional) coordinate systems

    Constraint information is preserved in the Atoms.info dictionary for
    later use in calculations or file writing.

    Examples
    --------
    >>> atoms = read("input.as")
    >>> print(atoms.get_chemical_formula())
    'Si2'

    >>> atoms = read(Path("structures/crystal.as"))
    >>> print(atoms.info.keys())  # Shows constraint information
    dict_keys(['Fix_x', 'Fix_y', 'Fix_z'])
    """
    absfile = absf(p)
    lines = remove_comments(absfile, "#")

    natom = int(lines[1])  # number of atoms
    lattice = _get_lat(lines)
    lat_fixs = _get_latfixs(lines)
    elements, coords = _get_ele_pos(lines, natom)
    atom_fix, mag = _get_mag_fix(lines, natom)
    if "Mag" in mag:
        magmoms = mag.pop("Mag")
    elif "Mag_x" in mag and "Mag_y" in mag and "Mag_z" in mag:
        magmoms = np.array([mag.pop("Mag_x"), mag.pop("Mag_y"), mag.pop("Mag_z")]).T.tolist()
    else:
        magmoms = None

    # lat & atom fix info are stored in info property
    freedom = {"lat": lat_fixs} | atom_fix if any(lat_fixs) else atom_fix
    atoms = Atoms(symbols=elements, cell=lattice, info=freedom, magmoms=magmoms, pbc=True)
    cd = lines[6].strip().split()[0]  # Cartesian/Direct
    _set_poses(atoms, cd, coords)

    return atoms


@logger.catch
def _set_poses(atoms: Atoms, cd: str, coords: np.ndarray) -> None:
    """Set atomic positions in ASE Atoms object based on coordinate type.

    Parameters
    ----------
    atoms : ase.atoms.Atoms
        ASE Atoms object to modify.
    cd : str
        Coordinate type: "Direct" for fractional or "Cartesian" for absolute.
    coords : numpy.ndarray
        Array of atomic coordinates with shape (n_atoms, 3).

    Raises
    ------
    ValueError
        If coordinate type is neither "Direct" nor "Cartesian".
    """
    # 'Cartesian/Direct Mag Fix_x ...'
    if cd == "Direct":
        atoms.set_scaled_positions(coords)
    elif cd == "Cartesian":
        atoms.set_positions(coords)
    else:
        raise ValueError("Structure file format error!")


@logger.catch
def _get_latfixs(lines: list[str]) -> list[bool]:
    """Extract lattice constraint information from DS-PAW .as file lines.

    Parameters
    ----------
    lines : list of str
        Preprocessed lines from the .as file with comments removed.

    Returns
    -------
    list of bool
        List of 9 boolean values representing lattice vector constraints:
        [a_x, a_y, a_z, b_x, b_y, b_z, c_x, c_y, c_z]
        True means the component is constrained (fixed).

    Raises
    ------
    ValueError
        If lattice constraint format is not recognized.
    """
    lat_fixs: list[bool] = []
    if lines[2].strip() != "Lattice":  # fix lattice
        lattice_fix_info = lines[2].strip().split()[1:]
        if lattice_fix_info == ["Fix_x", "Fix_y", "Fix_z"]:
            # ONLY support xyz fix in sequence, yzx will cause error
            for line in lines[3:6]:
                lfs = line.strip().split()[3:6]
                for lf in lfs:
                    if lf.startswith("T"):
                        lat_fixs.append(True)
                    elif lf.startswith("F"):
                        lat_fixs.append(False)
        elif lattice_fix_info == ["Fix"]:
            for line in lines[3:6]:
                lf = line.strip().split()[3]
                if lf.startswith("T"):
                    lat_fixs.extend([True, True, True])
                elif lf.startswith("F"):
                    lat_fixs.extend([False, False, False])
        else:
            raise ValueError("Lattice fix info error!")

    return lat_fixs


@logger.catch
def _get_lat(lines: list[str]) -> np.ndarray:
    """Parse lattice vectors from DS-PAW .as file lines.

    Parameters
    ----------
    lines : list of str
        Preprocessed lines from the .as file with comments removed.

    Returns
    -------
    numpy.ndarray
        3x3 array containing lattice vectors as rows:
        [[a_x, a_y, a_z],
         [b_x, b_y, b_z],
         [c_x, c_y, c_z]]
    """
    lattice = []  # lattice matrix
    for line in lines[3:6]:
        vector = line.split()
        lattice.extend([float(vector[0]), float(vector[1]), float(vector[2])])
    return np.asarray(lattice).reshape(3, 3)


@logger.catch
def _get_ele_pos(lines: list[str], natom: int) -> tuple[list[str], np.ndarray]:
    """Extract element symbols and atomic positions from DS-PAW .as file lines.

    Parameters
    ----------
    lines : list of str
        Preprocessed lines from the .as file with comments removed.
    natom : int
        Number of atoms in the structure.

    Returns
    -------
    tuple of (list of str, numpy.ndarray)
        - elements: List of element symbols with underscores removed
        - coords: Array of atomic coordinates with shape (natom, 3)
    """
    elements = []
    positions = []
    for i in range(natom):
        atom_data = lines[i + 7].strip().split()
        elements.append(atom_data[0])
        positions.extend([float(atom_data[1]), float(atom_data[2]), float(atom_data[3])])
    coords = np.asarray(positions).reshape(-1, 3)
    elements = [re.sub(r"_", "", e) for e in elements]

    return elements, coords


@logger.catch
def _get_mag_fix(lines: list[str], natom: int) -> tuple[dict, dict]:
    """Extract magnetic moments and atomic constraints from DS-PAW .as file lines.

    Parameters
    ----------
    lines : list of str
        Preprocessed lines from the .as file with comments removed.
    natom : int
        Number of atoms in the structure.

    Returns
    -------
    tuple of (dict, dict)
        - atom_fix: Dictionary with constraint information for each atom
        - mag: Dictionary with magnetic moment information for each atom

    Notes
    -----
    Supported constraint types:
    - "Fix": 3D constraint (x, y, z components)
    - "Fix_x", "Fix_y", "Fix_z": Individual component constraints

    Supported magnetic moment types:
    - "Mag": Collinear magnetic moments
    - "Mag_x", "Mag_y", "Mag_z": Non-collinear magnetic moment components
    """
    l6 = lines[6].strip()
    mf_info = l6.split()[1:]
    for item in mf_info:
        assert item in [
            "Mag",
            "Mag_x",
            "Mag_y",
            "Mag_z",
            "Fix",
            "Fix_x",
            "Fix_y",
            "Fix_z",
        ]

    def handle_fix_value(val_str):
        return val_str.startswith("T")

    mag_fix_dict: dict[str, list] = {}  # may be empty
    for mf_index, item in enumerate(mf_info):
        values: list[Any] = []
        for i in range(natom):
            atom_data = lines[i + 7].strip().split()
            mf_data = atom_data[4:]

            if item == "Fix":
                # Handle "Fix" which is a list of three "Fix_" values
                values.append(
                    [
                        handle_fix_value(mf_data[mf_index]),
                        handle_fix_value(mf_data[mf_index + 1]),
                        handle_fix_value(mf_data[mf_index + 2]),
                    ]
                )
            elif item.startswith("Fix_"):
                # Handle "Fix_x", "Fix_y", "Fix_z"
                values.append(handle_fix_value(mf_data[mf_index]))
            else:  # Mag, Mag_x, Mag_y, Mag_z
                values.append(float(mf_data[mf_index]))

        mag_fix_dict[item] = values

    # split into atom_fix and mag dicts
    atom_fix = {k: v for k, v in mag_fix_dict.items() if k.startswith("Fix")}
    mag = {k: v for k, v in mag_fix_dict.items() if k.startswith("Mag")}

    return atom_fix, mag
