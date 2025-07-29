# adnus (AdNuS):  Advanced Number Systems.


---

<p align="left">
    <table>
        <tr>
            <td style="text-align: center;">PyPI</td>
            <td style="text-align: center;">
                <a href="https://pypi.org/project/adnus/">
                    <img src="https://badge.fury.io/py/adnus.svg" alt="PyPI version" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">Conda</td>
            <td style="text-align: center;">
                <a href="https://anaconda.org/bilgi/adnus">
                    <img src="https://anaconda.org/bilgi/adnus/badges/version.svg" alt="conda-forge version" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">DOI</td>
            <td style="text-align: center;">
                <a href="https://doi.org/10.5281/zenodo.15874178">
                    <img src="https://zenodo.org/badge/DOI/-.svg" alt="DOI" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">License: MIT</td>
            <td style="text-align: center;">
                <a href="https://opensource.org/licenses/MIT">
                    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" height="18"/>
                </a>
            </td>
        </tr>
    </table>
</p>

---


adnus (AdNuS):  Advanced Number Systems.

---
# AdNuS: Advanced Number Systems

`adnus` is a Python library that provides an implementation of various advanced number systems. This library is designed for mathematicians, researchers, and developers who need to work with number systems beyond the standard real and complex numbers.

## Features

- **Harmonic and Oresme Sequences**: Functions to generate harmonic numbers and Oresme sequences.
- **Bicomplex Numbers**: A class for bicomplex numbers with full arithmetic support.
- **Neutrosophic Numbers**: Classes for neutrosophic numbers, including their complex and bicomplex extensions.
- **Hyperreal Numbers**: A conceptual implementation of hyperreal numbers.
- **Extensible Design**: Built with an abstract base class to easily extend and add new number systems.
- **Fully Typed**: The library is fully type-hinted for better code quality and maintainability.

## Installation

To install the library, clone the repository and use Poetry:

```bash
git clone https://github.com/WhiteSymmetry/adnus.git
cd adnus
poetry install
```

## Usage

Here's a quick overview of how to use the different number systems available in `adnus`.

### Bicomplex Numbers

```python
from adnus.main import BicomplexNumber

z1 = BicomplexNumber(1 + 2j, 3 + 4j)
z2 = BicomplexNumber(5 + 6j, 7 + 8j)

print(f"Addition: {z1 + z2}")
print(f"Multiplication: {z1 * z2}")
```

### Neutrosophic Numbers

```python
from adnus.main import NeutrosophicNumber

n1 = NeutrosophicNumber(1.5, 2.5)
n2 = NeutrosophicNumber(3.0, 4.0)

print(f"Addition: {n1 + n2}")
print(f"Multiplication: {n1 * n2}")
```

## Running Tests

To ensure everything is working correctly, you can run the included tests using `pytest`:

```bash
poetry run pytest
```

---

## Kurulum (Türkçe) / Installation (English)

### Python ile Kurulum / Install with pip, conda, mamba
```bash
pip install adnus -U
python -m pip install -U adnus
conda install bilgi::adnus -y
mamba install bilgi::adnus -y
```

```diff
- pip uninstall adnus -y
+ pip install -U adnus
+ python -m pip install -U adnus
```

[PyPI](https://pypi.org/project/adnus/)

### Test Kurulumu / Test Installation

```bash
pip install -i https://test.pypi.org/simple/ adnus -U
```

### Github Master Kurulumu / GitHub Master Installation

**Terminal:**

```bash
pip install git+https://github.com/WhiteSymmetry/adnus.git
```

**Jupyter Lab, Notebook, Visual Studio Code:**

```python
!pip install git+https://github.com/WhiteSymmetry/adnus.git
# or
%pip install git+https://github.com/WhiteSymmetry/adnus.git
```

---

## Kullanım (Türkçe) / Usage (English)

```python

```

```python
import adnus
adnus.__version__
```

```python

```

```python

```
---

### Development
```bash
# Clone the repository
git clone https://github.com/WhiteSymmetry/adnus.git
cd adnus

# Install in development mode
python -m pip install -ve . # Install package in development mode

# Run tests
pytest

Notebook, Jupyterlab, Colab, Visual Studio Code
!python -m pip install git+https://github.com/WhiteSymmetry/adnus.git
```
---

## Citation

If this library was useful to you in your research, please cite us. Following the [GitHub citation standards](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-citation-files), here is the recommended citation.

### BibTeX


### APA

```

Keçeci, M. (2025). adnus [Data set]. ResearchGate. https://doi.org/

Keçeci, M. (2025). adnus [Data set]. figshare. https://doi.org/

Keçeci, M. (2025). adnus [Data set]. WorkflowHub. https://doi.org/

Keçeci, M. (2025). adnus. Open Science Articles (OSAs), Zenodo. https://doi.org/

### Chicago

```


Keçeci, Mehmet. adnus [Data set]. ResearchGate, 2025. https://doi.org/

Keçeci, Mehmet (2025). adnus [Data set]. figshare, 2025. https://doi.org/

Keçeci, Mehmet. adnus [Data set]. WorkflowHub, 2025. https://doi.org/

Keçeci, Mehmet. adnus. Open Science Articles (OSAs), Zenodo, 2025. https://doi.org/

```


### Lisans (Türkçe) / License (English)

```
This project is licensed under the MIT License.
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.
