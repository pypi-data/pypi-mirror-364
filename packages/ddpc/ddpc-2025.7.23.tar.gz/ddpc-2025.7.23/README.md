# DDPC - DFT Data Processing Core

[![PyPI version](https://badge.fury.io/py/ddpc.svg)](https://badge.fury.io/py/ddpc)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DDPC** aims to be a handy Python library for processing and analyzing density functional theory (DFT) calculation data. It provides a unified interface for reading, writing, and manipulating crystal structures, electronic band structures, and density of states data from various DFT codes, such as VASP, DS-PAW, and RESCU.

## 📢 Announcement

This package is in early stage with limited functions. Use at your own risk.

[API reference](https://ddpc.readthedocs.io/en/latest/index.html)

## ✨ Key Features

- **🔄 Universal Structure I/O**: Read and write crystal structures in multiple formats (VASP, DS-PAW, RESCU, CIF, etc.)
- **📊 Electronic Structure Analysis**: Process band structure and density of states data from HDF5 and JSON files
- **🧮 Structure Utilities**: Find primitive cells, create orthogonal supercells, and manipulate atomic positions
- **⚡ High Performance**: Built on modern Python libraries (Polars, NumPy) for efficient data processing
- **🎯 Type Safety**: Full type annotations for better development experience
- **📖 Comprehensive Documentation**: Detailed API documentation with examples

## 🚀 Quick Start

### Installation

```bash
pip install ddpc
```

### Basic Usage

#### Structure I/O

```python
from ddpc.io.structure import read_structure, write_structure

# Read crystal structure from various formats
atoms = read_structure("input.vasp")  # VASP POSCAR
atoms = read_structure("structure.as")  # DS-PAW format
atoms = read_structure("crystal.cif")   # CIF format

# Write to different formats
write_structure("output.vasp", atoms)
write_structure("structure.xyz", atoms)
```

#### Electronic Structure Analysis

Currently only support DS-PAW output hdf5/json format, will support others in the future.

```python
from ddpc.io.band import read_band
from ddpc.io.dos import read_dos

# Read band structure data
df_band, fermi_energy, has_projections = read_band("band.h5", mode=5)
print(f"Fermi energy: {fermi_energy:.3f} eV")

# Read density of states
df_dos, fermi_energy, has_projections = read_dos("dos.json", mode=1)
```

#### Structure Utilities

```python
from ddpc.util import find_prim, find_orth, scale_atom_pos

# Find primitive cell
find_prim("input.vasp", "primitive.vasp", fmt="vasp", symprec=1e-5)

# Create orthogonal supercell
find_orth("input.vasp", "ortho.vasp", fmt="vasp", mlen=20.0)

# Convert to fractional coordinates
scale_atom_pos("input.vasp", "scaled.vasp")
```

## 📚 Supported Formats

### Crystal Structures
- **VASP**: POSCAR/CONTCAR files
- **DS-PAW**: Custom .as format with constraints and magnetism
- **RESCU**: Extended .xyz format with magnetic moments
- **Standard formats**: CIF, XYZ, and other ASE-supported formats

### Electronic Structure Data
- **HDF5 files**: Band structure and DOS data from DFT calculations
- **JSON files**: Alternative format for smaller datasets
- **Projected data**: Orbital-resolved band structures and DOS

## 🛠️ Advanced Features

### Constraint Handling
DDPC preserves and processes atomic and lattice constraints from specialized DFT codes:

```python
# DS-PAW format with constraints
atoms = read_structure("constrained.as")
print(atoms.info)  # Shows constraint information
```

### Magnetic Systems
Support for both collinear and non-collinear magnetic systems:

```python
# Read magnetic structure
atoms = read_structure("magnetic.xyz")
print(atoms.get_initial_magnetic_moments())
```

### Data Processing Modes
Multiple projection modes for electronic structure analysis:

```python
# Different projection modes for band structure
df, ef, proj = read_band("band.h5", mode=1)  # Element-resolved
df, ef, proj = read_band("band.h5", mode=2)  # Orbital-resolved (s,p,d,f)
df, ef, proj = read_band("band.h5", mode=5)  # Detailed orbital projections
```

## 🔧 Requirements

- **Python**: 3.12 or higher
- **Core dependencies**:
  - `ase>=3.25` - Atomic Simulation Environment
  - `h5py>=3.14` - HDF5 file support
  - `polars>=1.31` - Fast data processing
  - `pymatgen>=2025.6.14` - Materials analysis
  - `spglib>=2.6` - Space group operations
  - `loguru>=0.7.3` - Logging

## 🤝 Contributing

We welcome contributions! Feel free to send any suggestion.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🗓️ Changelog

### v2025.7.23 - Initial Release

#### ✨ New Features
- Complete structure I/O system supporting VASP, DS-PAW, RESCU, and standard formats
- Electronic structure data processing for band structures and density of states
- Structure manipulation utilities (primitive cell finding, orthogonalization)
- Full type annotations and comprehensive documentation
- Support for magnetic systems and atomic constraints

#### 🔧 Technical Details
- Built on modern Python 3.12+ with full type safety
- Efficient data processing using Polars and NumPy
- Comprehensive test suite with high coverage
- Professional documentation with API reference

---

**Made with ❤️ for the computational materials science community**
