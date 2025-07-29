"""Read band data from output files."""

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
def read_band(
    p: str | Path,
    mode: int = 5,
    fmt: str = "8.3f",
) -> tuple[pl.DataFrame, float, bool]:
    """Read and process electronic band structure data from HDF5 or JSON files.

    This function provides a unified interface for reading band structure data
    from DFT calculations, supporting both total and projected band structures
    with automatic format detection and data formatting.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the band structure data file. Supported formats are HDF5 (.h5)
        and JSON (.json) files from DFT calculations.
    mode : int, default 5
        Projection mode for projected band structure data. Only relevant when
        the file contains orbital-projected information. Different modes
        correspond to different orbital groupings (s, p, d, f, etc.).
    fmt : str, default "8.3f"
        Format string for floating-point number display in the output DataFrame.
        Controls decimal precision and field width for pretty printing.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing band structure data with k-points and energies
        - Fermi energy in eV
        - Boolean indicating whether the data contains orbital projections

    Raises
    ------
    TypeError
        If the input file is neither HDF5 nor JSON format.

    Notes
    -----
    The function automatically detects file format based on extension and
    processes the data accordingly. For projected band structures, the mode
    parameter determines which orbital contributions are included in the output.
    The DataFrame includes k-point coordinates, distances, and band energies,
    with spin-polarized calculations having separate up/down columns.
    """
    absfile = str(absf(p))

    if absfile.endswith(".h5"):
        df, efermi, isproj = read_band_h5(absfile, mode)
    elif absfile.endswith(".json"):
        df, efermi, isproj = read_band_json(absfile, mode)
    else:
        raise TypeError(f"{absfile} must be h5 or json file!")

    df = _format_float_columns_as_str_mapelements(df, fmt)

    return df, efermi, isproj


@logger.catch
def read_band_h5(absfile: str, mode: int) -> tuple[pl.DataFrame, float, bool]:
    """Read band structure data from HDF5 file format.

    This function processes HDF5 files containing electronic band structure
    data from DFT calculations, handling both total and projected band
    structures with proper metadata extraction.

    Parameters
    ----------
    absfile : str or pathlib.Path
        Path to the HDF5 band structure file (typically with .h5 extension).
    mode : int
        Projection mode for orbital-projected band structure data. Mode 0
        forces total band structure regardless of projection availability.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing processed band structure data
        - Fermi energy in eV extracted from the file
        - Boolean indicating presence of orbital projection data

    Raises
    ------
    TypeError
        If the HDF5 file doesn't contain the required 'BandInfo' group.
    SystemExit
        If critical metadata (Fermi energy or projection info) cannot be read.

    Notes
    -----
    The function expects HDF5 files with a specific structure containing:

    - /BandInfo/EFermi: Fermi energy value
    - /BandInfo/IsProject: Boolean indicating orbital projections
    - Band energy datasets organized by spin channels

    For projected data, the mode parameter determines which orbital
    contributions are included in the final DataFrame.
    """
    with h5py.File(absfile, "r") as band:
        bandinfo = band["BandInfo"]
        if isinstance(bandinfo, h5py.Group):
            efermi_list = bandinfo["EFermi"]
            if isinstance(efermi_list, h5py.Dataset):
                efermi = efermi_list[0]
            else:
                logger.error("cannot read /BandInfo/EFermi")
                sys.exit(1)

            proj = bandinfo["IsProject"]
            if isinstance(proj, h5py.Dataset):
                iproj = proj[0]
            else:
                logger.error("cannot read /BandInfo/IsProject")
                sys.exit(1)

            if mode == 0:
                df = read_tband(band)
            elif iproj:
                df = read_pband_h5(band, mode)
            else:
                df = read_tband(band)
        else:
            raise TypeError("h5 file must contain 'BandInfo' group!")

    return df, efermi, bool(iproj)


@logger.catch
def read_band_json(absfile: str, mode: int) -> tuple[pl.DataFrame, float, bool]:
    """Read band structure data from JSON file format.

    This function processes JSON files containing electronic band structure
    data from DFT calculations, providing an alternative to HDF5 format
    with the same functionality for band structure analysis.

    Parameters
    ----------
    absfile : str or pathlib.Path
        Path to the JSON band structure file (typically with .json extension).
    mode : int
        Projection mode for orbital-projected band structure data. Mode 0
        forces total band structure regardless of projection availability.

    Returns
    -------
    tuple of (polars.DataFrame, float, bool)

        - DataFrame containing processed band structure data
        - Fermi energy in eV extracted from the file
        - Boolean indicating presence of orbital projection data

    Notes
    -----
    The function expects JSON files with the same logical structure as HDF5
    files but in JSON format. The data organization includes:

    - BandInfo/EFermi: Fermi energy value
    - BandInfo/IsProject: Boolean indicating orbital projections
    - Band energy arrays organized by spin channels

    JSON format may be preferred for smaller datasets or when HDF5 is not
    available, though it's generally less efficient for large band structures.
    """
    with open(absfile, encoding="utf-8") as fin:
        band = load(fin)
        efermi = band["BandInfo"]["EFermi"]

    iproj = band["BandInfo"]["IsProject"]
    if mode == 0:
        df = read_tband(band, h5=False)
    elif iproj:
        df = read_pband_json(band, mode)
    else:
        df = read_tband(band, h5=False)

    return df, efermi, bool(iproj)


@logger.catch
def read_tband(band: h5py.File | dict, h5: bool = True) -> pl.DataFrame:
    """Read total (non-projected) band structure data from file.

    This function extracts and processes total electronic band structure data
    without orbital projections, handling both spin-polarized and non-spin-
    polarized calculations from HDF5 or JSON sources.

    Parameters
    ----------
    band : h5py.File or dict
        Band structure data container, either an opened HDF5 file object
        or a dictionary loaded from JSON.
    h5 : bool, default True
        Flag indicating the data source format. True for HDF5, False for JSON.

    Returns
    -------
    polars.DataFrame
        DataFrame containing band structure with columns:

        - label: High-symmetry k-point labels
        - kx, ky, kz: k-point coordinates
        - dist: Cumulative distance along k-path
        - band1, band2, ...: Band energies (with -up/-down suffix for spin-polarized)

    Notes
    -----
    The function handles different data layouts between HDF5 and JSON formats,
    automatically detecting spin polarization and organizing band energies
    accordingly. For collinear spin calculations, separate up and down spin
    channels are included with appropriate column naming.

    K-point distances are calculated as cumulative path lengths between
    consecutive k-points, useful for band structure plotting.
    """
    kc: list[float] = band["BandInfo"]["CoordinatesOfKPoints"]
    nok: int = band["BandInfo"]["NumberOfKpoints"]
    if isinstance(nok, int):
        nkpt = nok
    else:
        nkpt = nok[0]

    nob = band["BandInfo"]["NumberOfBand"]
    if isinstance(nob, int):
        nband = nob
    else:
        nband = nob[0]
    kcoord = np.array(kc).reshape(nkpt, 3)
    kx = kcoord[:, 0]
    ky = kcoord[:, 1]
    kz = kcoord[:, 2]
    # distance should be sum of diff
    diff = np.diff(kcoord, axis=0)  # n-1
    dist = [0.0]
    dist.extend(np.cumsum(np.linalg.norm(diff, axis=1)).tolist())

    if h5:
        collinear = band["BandInfo"]["SpinType"] == "collinear"
        sk: list[str] = get_h5_str(band, "/BandInfo/SymmetryKPoints")
        # h5py bands is a nband*nkpt 2d array with C order, have to flatten and reshape it
        bands = (
            np.asarray(band["BandInfo"]["Spin1"]["BandEnergies"])
            .flatten()
            .reshape(nband, nkpt, order="F")
        )
    else:
        collinear = band["BandInfo"]["IsProject"] == "collinear"
        sk = band["BandInfo"]["SymmetryKPoints"]
        bands = np.asarray(band["BandInfo"]["Spin1"]["BandEnergies"]).reshape(
            nband, nkpt, order="F"
        )
    ski = band["BandInfo"]["SymmetryKPointsIndex"]
    sk_column = [""] * nkpt
    for i, symbol in zip(ski, sk, strict=True):
        sk_column[i - 1] = symbol
    data = {
        "label": sk_column,
        "kx": kx,
        "ky": ky,
        "kz": kz,
        "dist": dist,
    }

    # only collinear system has Spin2
    if collinear:
        for i in range(bands.shape[0]):
            data[f"band{i + 1}-up"] = bands[i, :]
        bands = np.asarray(band["BandInfo"]["Spin2"]["BandEnergies"]).reshape(
            nband, nkpt, order="F"
        )
        for i in range(bands.shape[0]):
            data[f"band{i + 1}-down"] = bands[i, :]
    else:
        for i in range(bands.shape[0]):
            data[f"band{i + 1}"] = bands[i, :]

    return pl.DataFrame(data)


@logger.catch
def read_pband_h5(band: h5py.File, mode: int) -> pl.DataFrame:
    """Read orbital-projected band structure data from HDF5 file.

    This function extracts and processes orbital-projected electronic band
    structure data, providing detailed information about atomic orbital
    contributions to each band at every k-point.

    Parameters
    ----------
    band : h5py.File
        Opened HDF5 file object containing projected band structure data.
    mode : int
        Projection mode determining which orbital contributions to include.
        Different modes correspond to different orbital groupings and
        processing schemes for the projection data.

    Returns
    -------
    polars.DataFrame
        DataFrame containing projected band structure with columns:

        - label: High-symmetry k-point labels
        - kx, ky, kz: k-point coordinates
        - dist: Cumulative distance along k-path
        - Orbital projection columns:
            - "{atom_index}{orbital}-{spin}" for spin-polarized
            - "{atom_index}{orbital}" for non-spin-polarized

    Notes
    -----
    The function processes orbital projection data organized by atom indices
    and orbital types (s, p, d, f, etc.). For spin-polarized calculations,
    separate up and down spin projections are included.

    The projection data represents the weight of each atomic orbital in
    the electronic wavefunctions, useful for analyzing chemical bonding
    and orbital character of electronic states.
    """
    kc = band["/BandInfo/CoordinatesOfKPoints"]
    nkpt: int = band["/BandInfo/NumberOfKpoints"][0]
    nband: int = band["/BandInfo/NumberOfBand"][0]
    sk: list[str] = get_h5_str(band, "/BandInfo/SymmetryKPoints")
    ski: list[int] = band["BandInfo/SymmetryKPointsIndex"]

    sk_column = [""] * nkpt
    for i, symbol in zip(ski, sk, strict=True):
        sk_column[i - 1] = symbol

    kcoord = np.array(kc).reshape(nkpt, 3)
    kx = kcoord[:, 0]
    ky = kcoord[:, 1]
    kz = kcoord[:, 2]
    # distance should be sum of diff
    diff = np.diff(kcoord, axis=0)  # n-1
    dist = [0.0]
    dist.extend(np.cumsum(np.linalg.norm(diff, axis=1)).tolist())

    data = {
        "label": sk_column,
        "kx": kx,
        "ky": ky,
        "kz": kz,
        "dist": dist,
    }
    orbitals: list[str] = get_h5_str(band, "/BandInfo/Orbit")
    atom_index = band["/BandInfo/Spin1/ProjectBand/AtomIndex"][0]
    orb_index = band["/BandInfo/Spin1/ProjectBand/OrbitIndexs"][0]

    # only collinear system has Spin2
    if band["/BandInfo/SpinType"] == "collinear":
        for ai in range(atom_index):
            for oi in range(orb_index):
                data.update(
                    {
                        f"{ai + 1}{orbitals[oi]}-up": np.asarray(
                            band[f"/BandInfo/Spin1/ProjectBand/{ai + 1}/{oi + 1}"]
                        ).flatten()
                    }
                )
                data.update(
                    {
                        f"{ai + 1}{orbitals[oi]}-down": np.asarray(
                            band[f"/BandInfo/Spin2/ProjectBand/{ai + 1}/{oi + 1}"]
                        ).flatten()
                    }
                )
    else:
        for ai in range(atom_index):
            for oi in range(orb_index):
                data.update(
                    {
                        f"{ai + 1}{orbitals[oi]}": np.asarray(
                            band[f"/BandInfo/Spin1/ProjectBand/1/{ai + 1}/{oi + 1}"]
                        ).flatten()
                    }
                )

    elements: list[str] = get_h5_str(band, "/AtomInfo/Elements")
    _data = _refactor_band(data, nkpt, nband, elements, mode)

    return pl.DataFrame(_data)


@logger.catch
def read_pband_json(band: dict, mode: int) -> pl.DataFrame:
    """Read orbital-projected band structure data from JSON file.

    This function extracts and processes orbital-projected electronic band
    structure data from JSON format files, providing the same functionality
    as the HDF5 reader but for JSON-based data storage.

    Parameters
    ----------
    band : dict
        Dictionary containing projected band structure data loaded from JSON.
    mode : int
        Projection mode determining which orbital contributions to include
        and how they are processed and grouped in the output.

    Returns
    -------
    polars.DataFrame
        DataFrame containing projected band structure with columns:

        - label: High-symmetry k-point labels
        - kx, ky, kz: k-point coordinates
        - dist: Cumulative distance along k-path
        - Processed orbital projections based on the specified mode

    Notes
    -----
    The function processes JSON-formatted orbital projection data with the
    same logical structure as HDF5 files. The mode parameter determines
    the level of detail and grouping for orbital contributions.
    """
    kc: list[float] = band["BandInfo"]["CoordinatesOfKPoints"]
    nkpt: int = band["BandInfo"]["NumberOfKpoints"]
    nband: int = band["BandInfo"]["NumberOfBand"]

    sk: list[str] = band["BandInfo"]["SymmetryKPoints"]
    ski: list[int] = band["BandInfo"]["SymmetryKPointsIndex"]
    sk_column = [""] * nkpt
    for i, symbol in zip(ski, sk, strict=True):
        sk_column[i - 1] = symbol

    kcoord = np.array(kc).reshape(nkpt, 3)
    kx = kcoord[:, 0]
    ky = kcoord[:, 1]
    kz = kcoord[:, 2]
    # distance should be sum of diff
    diff = np.diff(kcoord, axis=0)  # n-1
    dist = [0.0]
    dist.extend(np.cumsum(np.linalg.norm(diff, axis=1)).tolist())

    data = {
        "label": sk_column,
        "kx": kx,
        "ky": ky,
        "kz": kz,
        "dist": dist,
    }
    orbitals: list[str] = band["BandInfo"]["Orbit"]
    if band["BandInfo"]["SpinType"] == "collinear":
        project1 = band["BandInfo"]["Spin1"]["ProjectBand"]
        project2 = band["BandInfo"]["Spin2"]["ProjectBand"]
        for p in project1:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}-up": contrib})
        for p in project2:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}-down": contrib})
    else:
        project = band["BandInfo"]["Spin1"]["ProjectBand"]
        for p in project:
            atom_index = p["AtomIndex"]
            orb_index = p["OrbitIndex"] - 1
            contrib = p["Contribution"]
            data.update({f"{atom_index}{orbitals[orb_index]}": contrib})

    elements: list[str] = [atom["Element"] for atom in band["AtomInfo"]["Atoms"]]
    _data = _refactor_band(data, nkpt, nband, elements, mode)

    return pl.DataFrame(_data)


@logger.catch
def _band_ele(data: dict, nkpt: int, nband: int, elements: list[str], _data: dict) -> None:
    for k, v in data.items():
        if k.startswith(("k", "label", "dist")):
            _data[k] = v
        else:
            cont = np.asarray(v).reshape(nband, nkpt, order="F")
            ao, updown = _get_ao_spin(k)
            a, _ = _split_atomindex_orbital(ao)
            for b in range(nband):
                if updown:
                    key = f"band{b + 1}-{elements[a - 1]}-{updown}"
                else:
                    key = f"band{b + 1}-{elements[a - 1]}"
                _inplace_update_data(_data, key, cont[b])


@logger.catch
def _band_elespdf(data: dict, nkpt: int, nband: int, elements: list[str], _data: dict) -> None:
    for k, v in data.items():
        if k.startswith(("k", "label", "dist")):
            _data[k] = v
        else:
            cont = np.asarray(v).reshape(nband, nkpt, order="F")
            ao, updown = _get_ao_spin(k)
            a, o = _split_atomindex_orbital(ao)
            for b in range(nband):
                if updown:
                    key = f"band{b + 1}-{elements[a - 1]}-{o[0]}-{updown}"
                else:
                    key = f"band{b + 1}-{elements[a - 1]}-{o[0]}"
                _inplace_update_data(_data, key, cont[b])


@logger.catch
def _band_elepxpy(data: dict, nkpt: int, nband: int, elements: list[str], _data: dict) -> None:
    for k, v in data.items():
        if k.startswith(("k", "label", "dist")):
            _data[k] = v
        else:
            cont = np.asarray(v).reshape(nband, nkpt, order="F")
            ao, updown = _get_ao_spin(k)
            a, o = _split_atomindex_orbital(ao)
            for b in range(nband):
                if updown:
                    key = f"band{b + 1}-{elements[a - 1]}-{o}-{updown}"
                else:
                    key = f"band{b + 1}-{elements[a - 1]}-{o}"
                _inplace_update_data(_data, key, cont[b])


@logger.catch
def _band_atomspdf(data: dict, nkpt: int, nband: int, _data: dict) -> None:
    for k, v in data.items():
        if k.startswith(("k", "label", "dist")):
            _data[k] = v
        else:
            cont = np.asarray(v).reshape(nband, nkpt, order="F")
            ao, updown = _get_ao_spin(k)
            a, o = _split_atomindex_orbital(ao)
            for b in range(nband):
                if updown:
                    key = f"band{b + 1}-{a}-{o[0]}-{updown}"
                else:
                    key = f"band{b + 1}-{a}-{o[0]}"
                _inplace_update_data(_data, key, cont[b])


@logger.catch
def _band_atompxpy(data: dict, nkpt: int, nband: int, _data: dict) -> None:
    for k, v in data.items():
        if k.startswith(("k", "label", "dist")):
            _data[k] = v
        else:
            cont = np.asarray(v).reshape(nband, nkpt, order="F")
            ao, updown = _get_ao_spin(k)
            a, o = _split_atomindex_orbital(ao)
            for b in range(nband):
                if updown:
                    key = f"band{b + 1}-{a}-{o}-{updown}"
                else:
                    key = f"band{b + 1}-{a}-{o}"
                _inplace_update_data(_data, key, cont[b])


@logger.catch
def _refactor_band(data: dict, nkpt: int, nband: int, elements: list[str], mode: int) -> dict:
    _data: dict = {}
    if mode == 1:
        _band_ele(data, nkpt, nband, elements, _data)
    elif mode == 2:
        _band_elespdf(data, nkpt, nband, elements, _data)
    elif mode == 3:
        _band_elepxpy(data, nkpt, nband, elements, _data)
    elif mode == 4:
        _band_atomspdf(data, nkpt, nband, _data)
    elif mode == 5:
        _band_atompxpy(data, nkpt, nband, _data)
    else:
        print(f"{mode=} not supported yet")
        raise RuntimeError(f"Unsupported mode: {mode}")

    return _data
