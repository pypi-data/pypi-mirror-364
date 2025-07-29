"""Read data from output files."""

import sys
from json import load
from pathlib import Path

import h5py
import numpy as np
import polars as pl
from loguru import logger

from ddpc.io.utils import (
    _format_float_columns_as_str_mapelements,
    _get_ao_spin,
    _inplace_update_data,
    _split_atomindex_orbital,
    absf,
    get_h5_str,
)


@logger.catch
def read_dos(
    p: str | Path,
    mode: int = 5,
    fmt: str = "8.3f",
) -> tuple[pl.DataFrame, float, bool]:
    """Read and process electronic density of states data from HDF5 or JSON files.

    This function provides a unified interface for reading density of states (DOS)
    data from DFT calculations, supporting both total and projected DOS with
    automatic format detection and data formatting.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the DOS data file. Supported formats are HDF5 (.h5) and
        JSON (.json) files from DFT calculations.
    mode : int, default 5
        Projection mode for projected density of states data. Only relevant
        when the file contains orbital-projected information. Different modes
        correspond to different orbital groupings (s, p, d, f, etc.).
    fmt : str, default "8.3f"
        Format string for floating-point number display in the output DataFrame.
        Controls decimal precision and field width for pretty printing.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing DOS data with energy points and DOS values
        - Fermi energy in eV
        - Boolean indicating whether the data contains orbital projections

    Raises
    ------
    TypeError
        If the input file is neither HDF5 nor JSON format.

    Notes
    -----
    The function automatically detects file format based on extension and
    processes the data accordingly. For projected DOS, the mode parameter
    determines which orbital contributions are included in the output.
    The DataFrame includes energy points and DOS values, with spin-polarized
    calculations having separate up/down columns.
    """
    absfile = str(absf(p))

    if absfile.endswith(".h5"):
        df, efermi, isproj = read_dos_h5(absfile, mode)
    elif absfile.endswith(".json"):
        df, efermi, isproj = read_dos_json(absfile, mode)
    else:
        raise TypeError(f"{absfile} must be h5 or json file!")

    df = _format_float_columns_as_str_mapelements(df, fmt)

    return df, efermi, isproj


@logger.catch
def read_dos_h5(absfile: str, mode: int) -> tuple[pl.DataFrame, float, bool]:
    """Read density of states data from HDF5 file format.

    Parameters
    ----------
    absfile : str
        Path to the HDF5 DOS file (typically with .h5 extension).
    mode : int
        Projection mode for orbital-projected DOS data. Mode 0 forces
        total DOS regardless of projection availability.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing processed DOS data
        - Fermi energy in eV extracted from the file
        - Boolean indicating presence of orbital projection data
    """
    with h5py.File(absfile, "r") as dos:
        dosinfo = dos["DosInfo"]
        if isinstance(dosinfo, h5py.Group):
            efermi_list = dosinfo["EFermi"]
            if isinstance(efermi_list, h5py.Dataset):
                efermi = efermi_list[0]
            else:
                logger.error("cannot read /BandInfo/EFermi")
                sys.exit(1)

            proj = dosinfo["Project"]
            if isinstance(proj, h5py.Dataset):
                iproj = proj[0]
            else:
                logger.error("cannot read /DosInfo/Project")
                sys.exit(1)
            if mode == 0:
                df = read_tdos(dos)
            elif iproj:
                df = read_pdos_h5(dos, mode)
            else:
                df = read_tdos(dos)
        else:
            raise TypeError("h5 file must contain 'DosInfo' group!")

    return df, efermi, bool(iproj)


@logger.catch
def read_dos_json(absfile: str, mode: int) -> tuple[pl.DataFrame, float, bool]:
    """Read density of states data from JSON file format.

    Parameters
    ----------
    absfile : str
        Path to the JSON DOS file (typically with .json extension).
    mode : int
        Projection mode for orbital-projected DOS data. Mode 0 forces
        total DOS regardless of projection availability.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing processed DOS data
        - Fermi energy in eV extracted from the file
        - Boolean indicating presence of orbital projection data
    """
    with open(absfile, encoding="utf-8") as fin:
        dos = load(fin)
        efermi = dos["DosInfo"]["EFermi"]
    iproj = dos["DosInfo"]["Project"]
    if mode == 0:
        df = read_tdos(dos, h5=False)
    elif iproj:
        df = read_pdos_json(dos, mode)
    else:
        df = read_tdos(dos, h5=False)

    return df, efermi, bool(iproj)


@logger.catch
def read_tdos(dos: h5py.File | dict, h5: bool = True) -> pl.DataFrame:
    """Read total (non-projected) density of states data.

    Parameters
    ----------
    dos : h5py.File or dict
        DOS data container, either an opened HDF5 file object or
        a dictionary loaded from JSON.
    h5 : bool, default True
        Flag indicating the data source format. True for HDF5, False for JSON.

    Returns
    -------
    polars.DataFrame
        DataFrame containing total DOS with energy points and DOS values.
    """
    energies = np.asarray(dos["DosInfo"]["DosEnergy"])

    if h5:
        spin_type = dos["DosInfo"]["SpinType"][0]
    else:
        spin_type = dos["DosInfo"]["SpinType"]

    if spin_type == "collinear":
        densities = {
            "energy": energies,
            "up": np.asarray(dos["DosInfo"]["Spin1"]["Dos"]),
            "down": np.asarray(dos["DosInfo"]["Spin2"]["Dos"]),
        }
    else:
        densities = {
            "energy": energies,
            "dos": np.asarray(dos["DosInfo"]["Spin1"]["Dos"]),
        }
    return pl.DataFrame(data=densities)


@logger.catch
def read_pdos_h5(dos: h5py.File, mode: int) -> pl.DataFrame:
    """Read orbital-projected density of states data from HDF5 file.

    Parameters
    ----------
    dos : h5py.File
        Opened HDF5 file object containing projected DOS data.
    mode : int
        Projection mode determining which orbital contributions to include.

    Returns
    -------
    polars.DataFrame
        DataFrame containing projected DOS with orbital contributions.
    """
    energies: list[float] = dos["/DosInfo/DosEnergy"]
    data = {}
    orbitals: list[str] = dos["/DosInfo/Orbit"]

    atom_index: int = dos["/DosInfo/Spin1/ProjectDos/AtomIndexs"][0]  # 2
    orb_index: int = dos["/DosInfo/Spin1/ProjectDos/OrbitIndexs"][0]  # 9
    if dos["/DosInfo/SpinType"] == "collinear":
        data.update(
            {
                "tdos-up": np.asarray(dos["/DosInfo/Spin1/Dos"]),
                "tdos-down": np.asarray(dos["/DosInfo/Spin2/Dos"]),
            },
        )
        for ai in range(atom_index):
            for oi in range(orb_index):
                data.update(
                    {
                        f"{ai + 1}{orbitals[oi]}-up": dos[
                            f"/DosInfo/Spin1/ProjectDos{ai + 1}/{oi + 1}"
                        ]
                    }
                )
                data.update(
                    {
                        f"{ai + 1}{orbitals[oi]}-down": dos[
                            f"/DosInfo/Spin2/ProjectDos{ai + 1}/{oi + 1}"
                        ]
                    }
                )
    else:
        data.update(
            {"tdos": np.asarray(dos["/DosInfo/Spin1/Dos"])},
        )
        for ai in range(atom_index):
            for oi in range(orb_index):
                data.update(
                    {f"{ai + 1}{orbitals[oi]}": dos[f"/DosInfo/Spin1/ProjectDos{ai + 1}/{oi + 1}"]}
                )

    if mode == 3:
        elements: list[str] = get_h5_str(dos, "/AtomInfo/Elements")
    else:
        elements = []
    _data = _refactor_dos(energies, data, mode, elements)
    logger.info(f"{_data=}")

    return pl.DataFrame(_data)


@logger.catch
def read_pdos_json(dos: dict, mode: int) -> pl.DataFrame:
    """Read orbital-projected density of states data from JSON file.

    Parameters
    ----------
    dos : dict
        Dictionary containing projected DOS data loaded from JSON.
    mode : int
        Projection mode determining which orbital contributions to include.

    Returns
    -------
    polars.DataFrame
        DataFrame containing projected DOS with orbital contributions.
    """
    energies: list[float] = dos["DosInfo"]["DosEnergy"]
    data = {}
    orbitals: list[str] = dos["DosInfo"]["Orbit"]

    if dos["DosInfo"]["SpinType"] == "collinear":
        data.update(
            {
                "tdos-up": dos["DosInfo"]["Spin1"]["Dos"],
                "tdos-down": dos["DosInfo"]["Spin2"]["Dos"],
            },
        )
        project = dos["DosInfo"]["Spin1"]["ProjectDos"]
        for p in project:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}-up": contrib})
        project = dos["DosInfo"]["Spin2"]["ProjectDos"]
        for p in project:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}-down": contrib})

    else:
        data.update(
            {"tdos": dos["DosInfo"]["Spin1"]["Dos"]},
        )
        project = dos["DosInfo"]["Spin1"]["ProjectDos"]
        for p in project:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}": contrib})

    if mode == 3:
        elements: list[str] = [atom["Element"] for atom in dos["AtomInfo"]["Atoms"]]
    else:
        elements = []
    _data = _refactor_dos(energies, data, mode, elements)

    return pl.DataFrame(_data)


@logger.catch
def _dos_spdf(data: dict, energies: np.ndarray) -> dict:
    _data = {"energy": energies}
    for k, v in data.items():
        if k.startswith("tdos"):  # do not process total dos
            _data[k] = v
            continue
        ao, updown = _get_ao_spin(k)
        _, o = _split_atomindex_orbital(ao)
        if updown:
            key = f"{o[0]}-{updown}"
        else:
            key = f"{o[0]}"
        _inplace_update_data(_data, key, v)
    return _data


@logger.catch
def _dos_spxpy(data: dict, energies: np.ndarray) -> dict:
    _data = {"energy": energies}
    for k, v in data.items():
        if k.startswith("tdos"):  # do not process total dos
            _data[k] = v
            continue
        ao, updown = _get_ao_spin(k)
        _, o = _split_atomindex_orbital(ao)
        if updown:
            key = f"{o}-{updown}"
        else:
            key = f"{o}"
        _inplace_update_data(_data, key, v)
    return _data


@logger.catch
def _dos_element(data: dict, elements: list[str] | None, energies: np.ndarray) -> dict:
    if not elements:
        raise ValueError(f"{elements=}")
    _data = {"energy": energies}
    for k, v in data.items():
        if k.startswith("tdos"):  # do not process total dos
            _data[k] = v
            continue
        ao, updown = _get_ao_spin(k)
        a, _ = _split_atomindex_orbital(ao)
        if updown:
            key = f"{elements[a - 1]}-{updown}"
        else:
            key = f"{elements[a - 1]}"
        _inplace_update_data(_data, key, v)
    return _data


@logger.catch
def _dos_atomspdf(data: dict, energies: np.ndarray) -> dict:
    _data = {"energy": energies}
    for k, v in data.items():
        if k.startswith("tdos"):  # do not process total dos
            _data[k] = v
            continue
        ao, updown = _get_ao_spin(k)
        a, o = _split_atomindex_orbital(ao)
        if updown:
            key = f"{a}{o[0]}-{updown}"
        else:
            key = f"{a}{o[0]}"
        _inplace_update_data(_data, key, v)
    return _data


@logger.catch
def _dos_atomt2geg(data: dict, energies: np.ndarray) -> dict:
    _data = {"energy": energies}
    for k, v in data.items():
        if k.startswith("tdos"):  # do not process total dos
            _data[k] = v
            continue
        ao, updown = _get_ao_spin(k)
        a, o = _split_atomindex_orbital(ao)
        if o in ["dxy", "dxz", "dyz"]:
            if updown:
                key = f"{a}t2g-{updown}"
            else:
                key = f"{a}t2g"
            _inplace_update_data(_data, key, v)
        elif o in ["dz2", "dx2y2"]:
            if updown:
                key = f"{a}eg-{updown}"
            else:
                key = f"{a}eg"
            _inplace_update_data(_data, key, v)

    return _data


@logger.catch
def _refactor_dos(
    energies: list | np.ndarray, data: dict, mode: int, elements: list[str] | None = None
) -> dict:
    energies = np.asarray(energies)
    if mode == 1:  # spdf
        _data = _dos_spdf(data, energies)

    elif mode == 2:  # spxpy...
        _data = _dos_spxpy(data, energies)

    elif mode == 3:  # element
        _data = _dos_element(data, elements, energies)

    elif mode == 4:  # atom+spdf
        _data = _dos_atomspdf(data, energies)

    elif mode == 5:  # atom+spxpy...
        _data = {key: dataset[:] for key, dataset in data.items()}
    elif mode == 6:  # atom+t2g/eg
        _data = _dos_atomt2geg(data, energies)

    else:
        print(f"{mode=} not supported yet")
        raise RuntimeError(f"Unsupported mode: {mode}")

    return _data
