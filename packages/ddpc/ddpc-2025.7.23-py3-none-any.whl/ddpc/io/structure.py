"""Wrapper for structure data loading."""

from pathlib import Path

from ase.atoms import Atoms
from ase.io import read, write
from loguru import logger

from ddpc.io.read import dspaw_as as rda
from ddpc.io.read import rescu_xyz as rrx
from ddpc.io.write import dspaw_as as wda
from ddpc.io.write import rescu_xyz as wrx


@logger.catch
def read_structure(p: str | Path):
    """Read crystal structure from various file formats.

    This function provides a unified interface for reading crystal structures
    from different file formats. It automatically detects the format based on
    file extension and uses the appropriate reader.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the structure file. Supported formats include:

        - .as : DS-PAW atomic structure format
        - .xyz : RESCU XYZ format
        - Other formats supported by ASE (POSCAR, CIF, etc.)

    Returns
    -------
    ase.atoms.Atoms or list of ase.atoms.Atoms
        Crystal structure(s) as ASE Atoms object(s). Some formats may return
        multiple structures (e.g., trajectory files).

    Notes
    -----
    The function uses format-specific readers for:

    - DS-PAW .as files: Custom reader supporting lattice/atom constraints and magnetism
    - RESCU .xyz files: Custom reader supporting magnetic moments and constraints
    - Other formats: ASE's built-in readers
    """
    fn = str(p)
    if fn.endswith(".as"):
        return rda.read(fn)
    if fn.endswith(".xyz"):
        return rrx.read(fn)
    return read(fn)


@logger.catch
def read_single_structure(p: str | Path):
    """Read the first structure from a file containing one or more structures.

    This function reads crystal structures from various file formats and ensures
    that only a single Atoms object is returned. If the file contains multiple
    structures (e.g., trajectory files), only the first one is returned.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the structure file. Supported formats include:

        - .as : DS-PAW atomic structure format
        - .xyz : RESCU XYZ format
        - Other formats supported by ASE (POSCAR, CIF, etc.)

    Returns
    -------
    ase.atoms.Atoms
        Single crystal structure as an ASE Atoms object. If the input file
        contains multiple structures, only the first one is returned.

    Notes
    -----
    This function is particularly useful when working with trajectory files
    or formats that can contain multiple structures, but you only need the
    first structure for analysis.
    """
    fn = str(p)
    if fn.endswith(".as"):
        return rda.read(fn)
    if fn.endswith(".xyz"):
        return rrx.read(fn)
    res = read(fn)
    if isinstance(res, Atoms):
        return res
    logger.warning("got multiple Atoms, will use the 1st one.")
    return res[0]


@logger.catch
def write_structure(
    p: str | Path, atoms: Atoms | list[Atoms], file_format: str | None = None, **kwargs
) -> str:
    """Write crystal structure(s) to file in various formats.

    This function provides a unified interface for writing crystal structures
    to different file formats. It automatically detects the format based on
    file extension or uses the explicitly specified format.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the output file. The file extension determines the format
        if file_format is not specified.
    atoms : ase.atoms.Atoms or list of ase.atoms.Atoms
        Crystal structure(s) to write. Some formats support multiple structures.
    file_format : str, optional
        Explicit file format specification. If None, format is determined
        from file extension. Supported formats include:

        - 'as' : DS-PAW atomic structure format
        - 'xyz' : RESCU XYZ format
        - Other formats supported by ASE ('vasp', 'cif', etc.)
    **kwargs
        Additional keyword arguments passed to the format-specific writer.

    Returns
    -------
    str
        String representation of the written structure file content.

    Raises
    ------
    ValueError
        If trying to write multiple structures to a format that only supports
        single structures (.as or .xyz formats).

    Notes
    -----
    Format-specific behaviors:

    - DS-PAW .as format: Only supports single Atoms objects, preserves constraints
    - RESCU .xyz format: Only supports single Atoms objects, preserves magnetism
    - Other formats: Use ASE's built-in writers with full feature support

    Examples
    --------
    >>> content = write_structure("output.vasp", atoms, file_format="vasp")
    >>> content = write_structure("structure.as", atoms)
    >>> content = write_structure("trajectory.xyz", atoms_list)
    """
    fn = str(p)
    if file_format == "as" or fn.endswith(".as"):
        if isinstance(atoms, Atoms):
            return wda.write(fn, atoms)
        raise ValueError("as format only support single Atoms object")
    if file_format == "xyz" or fn.endswith(".xyz"):
        if isinstance(atoms, Atoms):
            return wrx.write(fn, atoms)
        raise ValueError("xyz format only support single Atoms object")
    write(fn, atoms, format=file_format, **kwargs)  # type: ignore
    with open(fn, "r", encoding="utf-8") as f:
        return f.read()
