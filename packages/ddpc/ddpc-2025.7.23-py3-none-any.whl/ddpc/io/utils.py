"""Utility functions for read/write data."""

import os
import re
import sys
from pathlib import Path
from typing import cast

import numpy as np
import polars as pl
from h5py import File
from loguru import logger


@logger.catch
def absf(p: str | Path) -> Path:
    """Return absolute path of a file or directory.

    This function converts a relative or absolute path to an absolute path
    by resolving all symbolic links and relative path components.

    Parameters
    ----------
    p : str or pathlib.Path
        File or directory path to convert to absolute path.

    Returns
    -------
    pathlib.Path
        Absolute path object with all symbolic links resolved.
    """
    return Path(p).resolve()


@logger.catch
def get_h5_str(f: str | File, key: str) -> list:
    """Read string data from HDF5 file and return as list of elements.

    This function extracts string data from an HDF5 file at the specified key
    and returns it as a list of strings. It's commonly used to read element
    information from DFT calculation output files.

    Parameters
    ----------
    f : str or h5py.File
        HDF5 file path as string or already opened h5py.File object.
    key : str
        HDF5 dataset key/path to read from, e.g., "/AtomInfo/Elements".

    Returns
    -------
    list of str
        List of string elements extracted from the HDF5 dataset.

    Raises
    ------
    TypeError
        If the input file parameter is neither a string nor h5py.File object.

    Notes
    -----
    The function handles HDF5 string data that may be stored as bytes and
    automatically decodes it to strings. Multiple ion steps in MD simulations
    typically only save element information in the initial structure.
    """
    if isinstance(f, File):
        data = f
    elif isinstance(f, str):
        absh5 = os.path.abspath(f)
        data = File(absh5)
    else:
        raise TypeError(f)

    _bytes = np.asarray(data.get(key))
    tempdata = np.asarray([i.decode() for i in _bytes])
    tempdata_str: str = cast(str, "".join(tempdata))

    return tempdata_str.split(";")


@logger.catch
def remove_comments(p: str | Path, comment: str = "#") -> list:
    """Remove all comments from a text file and return non-empty lines.

    This function reads a text file, removes all comments (lines starting with
    or containing the comment character), and returns a list of non-empty lines
    with leading/trailing whitespace stripped.

    Parameters
    ----------
    p : str or pathlib.Path
        Path to the input text file to process.
    comment : str, default "#"
        Comment character or string. Everything from this character to the
        end of the line will be removed.

    Returns
    -------
    list of str
        List of non-empty lines with comments removed and whitespace stripped.

    Notes
    -----
    The function processes files line by line and:

    1. Removes everything from the comment character to the end of each line
    2. Strips leading and trailing whitespace
    3. Excludes empty lines from the result
    4. Uses UTF-8 encoding for file reading
    """
    lines = []
    with open(p, encoding="utf-8") as file:
        while True:
            line = file.readline()
            if line:
                line = re.sub(comment + r".*$", "", line)  # remove comment
                line = line.strip()
                if line:
                    lines.append(line)
            else:
                break

    return lines


@logger.catch
def _format_float_columns_as_str_mapelements(df: pl.DataFrame, fmt: str) -> pl.DataFrame:
    """Format numeric columns in DataFrame as strings for pretty printing.

    This internal function converts all numeric columns in a polars DataFrame
    to formatted string representations using the specified format string.
    It's primarily used for creating human-readable output of scientific data.

    Parameters
    ----------
    df : polars.DataFrame
        Input DataFrame containing numeric data to format.
    fmt : str
        Python format string for numeric values (e.g., '8.3f', '.2e').

    Returns
    -------
    polars.DataFrame
        DataFrame with numeric columns converted to formatted strings.
        Non-numeric columns remain unchanged.

    Notes
    -----
    This is an internal utility function for data presentation. The function:

    - Identifies all numeric columns automatically
    - Applies the format string to non-null values
    - Converts null values to empty strings
    - Preserves non-numeric columns unchanged
    - Handles formatting errors gracefully
    """
    if not isinstance(df, pl.DataFrame):
        logger.warning("Input is not a polars DataFrame. Returning as is.")
        return df
    if not isinstance(fmt, str):
        logger.warning(f"Format '{fmt}' is not a string. Skipping formatting.")
        return df

    # Get numeric columns
    numeric_cols = [col for col in df.columns if df[col].dtype.is_numeric()]

    if not numeric_cols:
        logger.info("No float/numeric columns found to format.")
        return df

    try:
        # Create expressions for formatting numeric columns
        format_exprs = []
        for col in numeric_cols:
            format_expr = (
                pl.when(pl.col(col).is_null())
                .then(pl.lit(""))
                .otherwise(pl.col(col).map_elements(lambda x: f"{x:{fmt}}", return_dtype=pl.String))
                .alias(col)
            )
            format_exprs.append(format_expr)

        # Keep non-numeric columns as they are
        non_numeric_cols = [col for col in df.columns if col not in numeric_cols]
        keep_exprs = [pl.col(col) for col in non_numeric_cols]

        return df.select(keep_exprs + format_exprs)
    except ValueError as e:
        logger.error(f"Error applying format '{fmt}': {e}. Skipping formatting.")
        return df
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}. Skipping formatting.")
        return df


@logger.catch
def _split_atomindex_orbital(s: str) -> tuple[int, str]:
    """Split a string into atom index and orbital designation.

    This internal function parses strings that combine atom indices with
    orbital labels (e.g., "12s", "5px", "3dxy") and separates them into
    numeric atom index and orbital string components.

    Parameters
    ----------
    s : str
        Input string containing atom index followed by orbital designation.
        Examples: "12s", "5px", "3dxy", "1", "25f".

    Returns
    -------
    tuple of (int, str)
        Two-element tuple containing:

        - int: Atom index (numeric part)
        - str: Orbital designation (alphabetic part, empty if none)

    Notes
    -----
    This is an internal utility function for parsing projected band structure
    and density of states data where atomic orbitals are labeled with both
    atom indices and orbital types.

    The function assumes the string starts with digits (atom index) followed
    by letters (orbital designation). If no letters are found, the orbital
    part is returned as an empty string.
    """
    first_letter_index = -1
    for i, char in enumerate(s):
        if not char.isdigit():
            first_letter_index = i
            break

    if first_letter_index == -1:  # No letters found, assume the whole string is the atomIndex
        return int(s), ""
    atom_index_str = s[:first_letter_index]
    orbital_str = s[first_letter_index:]
    return int(atom_index_str), orbital_str


@logger.catch
def _get_ao_spin(k: str) -> tuple[str, str]:
    """Parse atomic orbital and spin information from formatted key strings.

    This internal function extracts atomic orbital and spin channel information
    from hyphen-separated key strings used in band structure and density of
    states data processing.

    Parameters
    ----------
    k : str
        Input key string in format "orbital" or "orbital-spin".
        Examples: "s", "px", "dxy", "s-up", "px-down".

    Returns
    -------
    tuple of (str, str)
        Two-element tuple containing:

        - str: Orbital designation (e.g., "s", "px", "dxy")
        - str: Spin channel ("up", "down", or empty string for non-spin-polarized)

    Raises
    ------
    SystemExit
        If the input string format is invalid (contains more than one hyphen).

    Notes
    -----
    This is an internal utility function for parsing projected electronic
    structure data where orbital contributions may be separated by spin channels.
    """
    ls = k.split("-")
    if len(ls) == 1:  # nospin
        return ls[0], ""
    if len(ls) == 2:  # spin-polarized
        return ls[0], ls[1]
    logger.error(f"get_ao_spin error: {k=}")
    sys.exit(1)


@logger.catch
def _inplace_update_data(_data: dict, key: str, v: np.ndarray | list) -> None:
    """Update data dictionary by adding values to existing keys or creating new ones.

    This internal function performs in-place updates of a data dictionary by
    either adding values to existing array entries or creating new entries.
    It's used for accumulating projected band structure and DOS data.

    Parameters
    ----------
    _data : dict
        Dictionary to update in-place. Values should be numpy arrays or
        array-like objects that support addition.
    key : str
        Dictionary key to update or create.
    v : array-like
        Values to add to existing data or set as new data.

    Notes
    -----
    This is an internal utility function for data accumulation during
    electronic structure data processing. The function:

    - Adds values to existing keys using numpy array addition
    - Creates new keys with numpy array values
    - Modifies the input dictionary in-place
    """
    if key in _data:
        _data[key] += np.asarray(v)
    else:
        _data[key] = np.asarray(v)
