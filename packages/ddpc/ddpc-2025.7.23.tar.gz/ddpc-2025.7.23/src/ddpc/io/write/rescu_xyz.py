"""Module to write structure to RESCU xyz format."""

from ase.atoms import Atoms
from loguru import logger

from ddpc.io.utils import absf


@logger.catch
def write(f: str, atoms: Atoms) -> str:
    """Write RESCU xyz format file with formatted strings.

    Parameters
    ----------
    f : str
        Output file path. Use "-" to return string without writing to file.
    atoms : ase.atoms.Atoms
        ASE Atoms object containing the crystal structure to write.

    Returns
    -------
    str
        String representation of the RESCU xyz format file content.

    Notes
    -----
    The function preserves constraint and magnetic information from the
    Atoms.info dictionary:

    - Atomic constraints: 'atom_fix' key with shape (n_atoms, 3)
    - Magnetic moments: Retrieved from atoms.get_initial_magnetic_moments()

    The output format supports both collinear and non-collinear magnetism,
    and various constraint types as supported by RESCU.
    """
    ret = f"{len(atoms)}\nAuto-generated xyz file\n"
    mags = atoms.get_initial_magnetic_moments()
    symbols = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    fix_info = atoms.info.get("atom_fix", None)
    ret = _add_atom_lines(symbols, positions, fix_info, mags, ret)

    if f == "-":
        pass
    else:
        absxyz = absf(f)
        absxyz.parent.mkdir(parents=True, exist_ok=True)

        with open(absxyz, "w", encoding="utf-8") as _f:
            logger.debug(f"write {absxyz}")
            _f.write(ret)

    return ret


@logger.catch
def _add_atom_lines(symbols, positions, fix_info, mags, ret) -> str:
    """Add atomic information lines to RESCU XYZ format string.

    This internal function formats atomic positions, magnetic moments, and
    constraints for the RESCU XYZ file format.

    Parameters
    ----------
    symbols : list of str
        Chemical symbols for each atom.
    positions : numpy.ndarray
        Atomic positions with shape (n_atoms, 3).
    fix_info : numpy.ndarray or None
        Constraint information with shape (n_atoms, 3) or None.
    mags : numpy.ndarray
        Magnetic moments array (collinear or non-collinear).
    ret : str
        Existing file content string to append to.

    Returns
    -------
    str
        Updated file content string with atomic information added.

    Notes
    -----
    The function handles different combinations of magnetic moments and
    constraints, choosing the appropriate RESCU XYZ format variant.
    """
    if mags.any():
        ret = _add_with_mag(symbols, positions, fix_info, mags, ret)
    elif fix_info is not None and fix_info.any():
        for symbol, pos, moveable_xyz in zip(symbols, positions, fix_info, strict=True):
            moveable = f"{moveable_xyz[0]} {moveable_xyz[1]} {moveable_xyz[2]}"
            ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f} 0 0 0 {moveable}\n"
    else:
        for symbol, pos in zip(symbols, positions, strict=True):
            ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n"

    return ret


@logger.catch
def _add_with_mag(symbols, positions, fix_info, mags, ret) -> str:
    """Add atomic lines with magnetic moments to RESCU XYZ format string.

    This internal function handles the formatting of atomic information when
    magnetic moments are present, supporting both collinear and non-collinear
    magnetism with optional position constraints.

    Parameters
    ----------
    symbols : list of str
        Chemical symbols for each atom.
    positions : numpy.ndarray
        Atomic positions with shape (n_atoms, 3).
    fix_info : numpy.ndarray or None
        Constraint information with shape (n_atoms, 3) or None.
    mags : numpy.ndarray
        Magnetic moments array, either (n_atoms,) for collinear or
        (n_atoms, 3) for non-collinear magnetism.
    ret : str
        Existing file content string to append to.

    Returns
    -------
    str
        Updated file content string with magnetic atomic information added.

    Notes
    -----
    The function automatically detects the magnetic moment format:

    - Shape (n_atoms, 3): Non-collinear magnetism (mx, my, mz)
    - Shape (n_atoms,): Collinear magnetism (single value)

    Position constraints are included if fix_info is provided and contains
    non-zero values.
    """
    if mags.shape == (len(symbols), 3):
        # Non-collinear magnetism
        if fix_info is not None and fix_info.any():
            for symbol, pos, mag, moveable_xyz in zip(
                symbols, positions, mags, fix_info, strict=True
            ):
                moveable = f"{moveable_xyz[0]} {moveable_xyz[1]} {moveable_xyz[2]}"
                _mag = f"{mag[0]:.2f} {mag[1]:.2f} {mag[2]:.2f}"
                ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f} {_mag} {moveable}\n"
        else:
            for symbol, pos, mag in zip(symbols, positions, mags, strict=True):
                _mag = f"{mag[0]:.2f} {mag[1]:.2f} {mag[2]:.2f}"
                ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f} {_mag}\n"
    elif mags.shape == (len(symbols),):
        # Collinear magnetism
        if fix_info is not None and fix_info.any():
            for symbol, pos, mag, moveable_xyz in zip(
                symbols, positions, mags, fix_info, strict=True
            ):
                moveable = f"{moveable_xyz[0]} {moveable_xyz[1]} {moveable_xyz[2]}"
                ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f} {mag:.2f} {moveable}\n"
        else:
            for symbol, pos, mag in zip(symbols, positions, mags, strict=True):
                ret += f"{symbol} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f} {mag:.2f}\n"
    else:
        logger.error(f"{mags=}")

    return ret
