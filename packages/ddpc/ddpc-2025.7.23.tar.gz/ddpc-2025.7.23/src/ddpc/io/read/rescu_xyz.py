"""Read RESCU specified .xyz format file and its input to create an ASE atoms."""

from pathlib import Path

import numpy as np
from ase.atoms import Atoms
from loguru import logger

from ddpc.io.utils import absf, remove_comments


@logger.catch
def read(p: str | Path) -> Atoms:
    """Read RESCU XYZ format file and convert to ASE Atoms object.

    This function reads RESCU's extended XYZ format files which support
    magnetic moments and atomic position constraints. RESCU is a DFT code
    that uses a specialized XYZ format for structure input.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the RESCU XYZ format structure file.

    Returns
    -------
    ase.atoms.Atoms
        ASE Atoms object containing the crystal structure with:

        - Atomic positions in Cartesian coordinates
        - Magnetic moments (if specified)
        - Constraint information stored in the info dictionary

    Notes
    -----
    The RESCU XYZ format supports various line formats:

    - basic: element x/y/z
    - collinear magnetism: element x/y/z mag
    - non-collinear magnetism: element x/y/z mag_x/y/z
    - constraints: element x/y/z mag moveable_x/y/z
    - non-collinear mag + constraints: element x/y/z mag_x/y/z moveable_x/y/z

    Constraint information is preserved in the Atoms.info dictionary as
    'atom_fix' with shape (n_atoms, 3) indicating moveable directions.

    Examples
    --------
    >>> atoms = read("structure.xyz")
    >>> print(atoms.get_chemical_formula())
    'H2O'

    >>> atoms = read("magnetic_structure.xyz")
    >>> print(atoms.get_initial_magnetic_moments())
    [1.0, -1.0, 0.0]
    """
    absfile = absf(p)
    lines = remove_comments(absfile, "#")

    nele, elements, pos, mags, moveable_indices_x, moveable_indices_y, moveable_indices_z = (
        _read_prop(lines)
    )
    # check
    if not (nele == len(pos) == len(elements)):
        logger.error(f"{nele=},{len(pos)=},{elements=}")
    if mags and nele != len(mags):
        logger.error(f"{nele=},{len(mags)=}")
    if moveable_indices_x and nele != len(moveable_indices_x):
        logger.error(f"{nele=},{len(moveable_indices_x)=}")

    # ASE won't write atom fix per atom even if we set constraint,
    # we have to store it in `info` dict and handle it manually
    fix_info = {
        "atom_fix": np.array([moveable_indices_x, moveable_indices_y, moveable_indices_z]).T
    }
    return Atoms(symbols=elements, positions=pos, magmoms=mags, pbc=True, info=fix_info)


@logger.catch
def _read_prop(
    lines: list[str],
):
    """Parse atomic properties from RESCU XYZ format file lines.

    This internal function processes the lines of a RESCU XYZ file and extracts
    atomic information including positions, magnetic moments, and constraints.

    Parameters
    ----------
    lines : list of str
        Preprocessed lines from the XYZ file with comments removed.

    Returns
    -------
    tuple
        Seven-element tuple containing:

        - nele (int): Number of elements
        - elements (list of str): Element symbols
        - pos (list of list): Atomic positions as [[x,y,z], ...]
        - mags (list): Magnetic moments (collinear or non-collinear)
        - moveable_indices_x (list of int): X-direction mobility flags
        - moveable_indices_y (list of int): Y-direction mobility flags
        - moveable_indices_z (list of int): Z-direction mobility flags

    Notes
    -----
    Supports multiple line formats in RESCU XYZ files:

    - 4 items: element x y z
    - 5 items: element x y z mag
    - 7 items: element x y z mag_x mag_y mag_z
    - 8 items: element x y z mag moveable_x moveable_y moveable_z
    - 10 items: element x y z mag_x mag_y mag_z moveable_x moveable_y moveable_z
    """
    nele = 0
    elements = []
    pos = []  # Nx3
    mags: list[float | list[float]] = []  # collinear
    moveable_indices_x = []
    moveable_indices_y = []
    moveable_indices_z = []
    for i, _line in enumerate(lines):
        line = _line.strip()
        # remove comment starts with # or %
        if "#" in line:
            line = line[: line.index("#")]
        if "%" in line:
            line = line[: line.index("%")]

        # parse data
        if i == 0:
            nele = int(line)
        elif i > 1 and line:
            # ele, x, y, z, (m (mx, my, mz), fx, fy, fz)
            split_items = line.split()
            if len(split_items) == 4:  # normal
                ele, x, y, z = split_items
                elements.append(ele)
                pos.append([float(x), float(y), float(z)])
            elif len(split_items) == 5:  # collinear spin
                ele, x, y, z, m = split_items
                elements.append(ele)
                pos.append([float(x), float(y), float(z)])
                mags.append(float(m))
            elif len(split_items) == 7:  # non-collinear spin
                ele, x, y, z, mag_x, mag_y, mag_z = split_items
                elements.append(ele)
                pos.append([float(x), float(y), float(z)])
                mags.append([float(mag_x), float(mag_y), float(mag_z)])
            elif len(split_items) == 8:  # collinear spin + fix
                ele, x, y, z, mag, moveable_x, moveable_y, moveable_z = split_items
                elements.append(ele)
                pos.append([float(x), float(y), float(z)])
                mags.append(float(mag))
                moveable_indices_x.append(int(moveable_x))
                moveable_indices_y.append(int(moveable_y))
                moveable_indices_z.append(int(moveable_z))
            elif len(split_items) == 10:  # fixed collinear spin
                (
                    ele,
                    x,
                    y,
                    z,
                    mag_x,
                    mag_y,
                    mag_z,
                    moveable_x,
                    moveable_y,
                    moveable_z,
                ) = split_items
                elements.append(ele)
                pos.append([float(x), float(y), float(z)])
                mags.append([float(mag_x), float(mag_y), float(mag_z)])
                moveable_indices_x.append(int(moveable_x))
                moveable_indices_y.append(int(moveable_y))
                moveable_indices_z.append(int(moveable_z))
            else:
                logger.error(f"Invalid {line=}")

    return (
        nele,
        elements,
        pos,
        mags,
        moveable_indices_x,
        moveable_indices_y,
        moveable_indices_z,
    )
