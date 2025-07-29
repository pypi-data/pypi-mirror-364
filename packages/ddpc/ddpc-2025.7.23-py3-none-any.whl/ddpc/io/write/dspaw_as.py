"""Module to write structure to ds-paw as format file."""

import numpy as np
from ase.atoms import Atoms
from loguru import logger

from ddpc.io.utils import absf


@logger.catch
def write(p: str, atoms: Atoms) -> str:
    r"""Write ASE Atoms object to DS-PAW .as format file.

    This function converts an ASE Atoms object to DS-PAW's custom .as format,
    preserving lattice constraints, atomic position constraints, and magnetic
    moments that are stored in the Atoms.info dictionary.

    Parameters
    ----------
    p : str
        Output file path. Use "-" to return string without writing to file.
    atoms : ase.atoms.Atoms
        ASE Atoms object containing the crystal structure to write.

    Returns
    -------
    str
        String representation of the DS-PAW .as format file content.

    Notes
    -----
    The function preserves constraint and magnetic information from the
    Atoms.info dictionary:

    - Lattice constraints: 'lat' key with 9 boolean values
    - Atomic constraints: 'Fix', 'Fix_x', 'Fix_y', 'Fix_z' keys
    - Magnetic moments: Retrieved from atoms.get_initial_magnetic_moments()

    The output format supports both collinear and non-collinear magnetism,
    and various constraint types as supported by DS-PAW.

    Examples
    --------
    >>> content = write("output.as", atoms)
    >>> print(content[:50])  # First 50 characters
    'Total number of atoms\\n8\\nLattice\\n...'

    >>> # Write to file
    >>> write("structure.as", atoms)
    """
    lines = "Total number of atoms\n"
    lines += "%d\n" % len(atoms)

    freedom = atoms.info
    lines = _add_lat_lines(freedom, lines, atoms)
    lines = _add_atom_lines(freedom, lines, atoms)
    lines = _write_to_file(p, lines)

    return lines


@logger.catch
def _add_lat_lines(freedom: dict, lines: str, atoms: Atoms) -> str:
    """Add lattice vector lines to DS-PAW .as format string.

    This internal function formats lattice vectors and their constraints
    for the DS-PAW .as file format.

    Parameters
    ----------
    freedom : dict
        Dictionary containing constraint information from atoms.info.
    lines : str
        Existing file content string to append to.
    atoms : ase.atoms.Atoms
        ASE Atoms object containing lattice vectors.

    Returns
    -------
    str
        Updated file content string with lattice information added.

    Notes
    -----
    If lattice constraints are present in the freedom dictionary ('lat' key),
    they are formatted as Fix_x Fix_y Fix_z columns. Otherwise, only the
    lattice vectors are written without constraint information.
    """
    if "lat" in freedom:
        lat_fix = freedom.pop("lat")
        lines += "Lattice Fix_x Fix_y Fix_z\n"
        formatted_fts = []
        for ft in lat_fix:
            ft_formatted = "T" if ft else "F"
            formatted_fts.append(ft_formatted)
        fix_str1 = " ".join(formatted_fts[:3])
        fix_str2 = " ".join(formatted_fts[3:6])
        fix_str3 = " ".join(formatted_fts[6:9])
        fix_strs = [fix_str1, fix_str2, fix_str3]
        for v, fs in zip(atoms.cell.array, fix_strs, strict=True):
            lines += f"{v[0]: 10.4f} {v[1]: 10.4f} {v[2]: 10.4f} {fs}\n"

    else:
        lines += "Lattice\n"
        for v in atoms.cell.array:
            lines += f"{v[0]: 10.4f} {v[1]: 10.4f} {v[2]: 10.4f}\n"

    return lines


@logger.catch
def _add_atom_lines(freedom, lines, atoms):
    """Add atomic information lines to DS-PAW .as format string.

    This internal function formats atomic positions, constraints, and magnetic
    moments for the DS-PAW .as file format.

    Parameters
    ----------
    freedom : dict
        Dictionary containing atomic constraint information from atoms.info.
    lines : str
        Existing file content string to append to.
    atoms : ase.atoms.Atoms
        ASE Atoms object containing atomic information.

    Returns
    -------
    str
        Updated file content string with atomic information added.

    Notes
    -----
    The function handles both collinear and non-collinear magnetic moments,
    and formats atomic constraints as T/F flags. Positions are written in
    Cartesian coordinates with appropriate precision formatting.
    """
    key_str = " ".join(freedom.keys())
    magmoms = atoms.get_initial_magnetic_moments()  # n,1; n,3; [0.0] * n
    init_mag = True
    if len(magmoms.shape) == 1:
        if not any(magmoms):
            init_mag = False
        else:
            key_str += " Mag"
    else:
        key_str += " Mag_x Mag_y Mag_z"
    lines += f"Cartesian {key_str}\n"
    elements = atoms.symbols
    positions = atoms.positions
    atom_fix = []
    for i in range(len(atoms.symbols)):
        raw = ""
        for val_column in freedom.values():
            if val_column[i]:
                raw += "T "
            else:
                raw += "F "
        atom_fix.append(raw.strip())

    for ele, pos, af, magmom in zip(elements, positions, atom_fix, magmoms, strict=True):
        if isinstance(magmom, np.ndarray):
            init_magmom = np.array2string(
                magmom,
                formatter={"float_kind": lambda x: f"{x:7.3f}"},
            ).strip("[]")
        elif magmom:
            init_magmom = f"{float(magmom): 7.3f}"
        else:
            init_magmom = "  0.000" if init_mag else ""
        lines += f"{ele:<2} {pos[0]: 10.4f} {pos[1]: 10.4f} {pos[2]: 10.4f} {af} {init_magmom}\n"

    return lines


@logger.catch
def _write_to_file(filename, lines) -> str:
    """Write formatted content to file or return as string.

    This internal function handles the actual file writing operation for
    DS-PAW .as format files.

    Parameters
    ----------
    filename : str
        Output file path. Use "-" or empty string to skip file writing.
    lines : str
        Formatted file content to write.

    Returns
    -------
    str
        The input lines string (unchanged).

    Notes
    -----
    The function creates parent directories if they don't exist and uses
    UTF-8 encoding for file writing. If filename is "-" or empty, no file
    is written but the content string is still returned.
    """
    if not filename:
        return lines

    if filename == "-":
        pass
    else:
        absfile = absf(filename)
        absfile.parent.mkdir(parents=True, exist_ok=True)

        with open(absfile, "w", encoding="utf-8") as file:
            file.write(lines)

    return lines
