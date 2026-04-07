# LBNL_DIATOMICS

**LBNL_DIATOMICS** is a software package developed by P. Zarzycki
([Lawrence Berkeley National Laboratory](https://www.lbl.gov/)) for
computing isotopic effects in diatomic molecules using mass-dependent
spectroscopic parameters obtained experimentally or from first principles.

The package provides a streamlined pipeline from the potential energy
surface to the equilibrium constant of an isotopic exchange reaction.

## Features

- **Spectroscopic parameters from PES** — several methods of varying
  complexity, including polynomial fits, full Dunham analysis, and a
  numerical solver for the one-dimensional Schrödinger equation.
- **Reduced partition function ratios** — computation of β-factors for
  isotopologue pairs.
- **Equilibrium constants** — evaluation of equilibrium constants for
  isotopic exchange reactions between diatomic molecules.
- **Polynomial fitting** — fitting of 1000 ln β as a function of
  reciprocal temperature.

## Installation

```bash
git clone https://github.com/username/lbnl_diatomics.git
cd lbnl_diatomics
```


## Usage

```bash
# Basic usage
python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 1273.15 --temp-step 100

# Specify temperature step and fundamental constants year
python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 1273.15 --temp-step 50 --constants 1973

# Single temperature point
python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 273.15 --temp-step 1 --constants 2022
```

### Command-line arguments
| Argument       | Description                              |
|----------------|------------------------------------------|
| `input.txt`    | Path to the input file                   |
| `--temp-start` | Starting temperature (K)                 |
| `--temp-stop`  | Final temperature (K)                    |
| `--temp-step`  | Temperature step (K)                     |
| `--constants`  | Year of fundamental constants (optional) |


## Input file format
```
# label  omega  omega_xe  B0  mass1  mass2  symmetry  alpha
H2    4401.118  121.284  59.3251  1.00782503223  1.0080   2  3.0258
HD    3812.293   90.908  44.6613  1.0080         2.01410  1  2.0034
```

### Column definitions 
| Column     | Description                                      |
|------------|--------------------------------------------------|
| `label`    | Isotopologue name                                |
| `omega`    | Harmonic frequency ω_e (cm⁻¹)                   |
| `omega_xe` | Anharmonicity constant ω_e x_e (cm⁻¹)           |
| `B0`       | Rotational constant B_e (cm⁻¹)                  |
| `mass1`    | Atomic mass of atom 1 (amu)                      |
| `mass2`    | Atomic mass of atom 2 (amu)                      |
| `symmetry` | Symmetry number σ                                |
| `alpha`    | Vibration–rotation coupling constant α_e (cm⁻¹) |







