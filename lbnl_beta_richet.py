
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║      Partition Function Ratio Calculator for Diatomic Isotopologues.       ║
║                        LBNL 2026 version 1.0                               ║
║                                                                            ║
║ Reference for the theory: Richet, Y. Bottinga, M. Javoy, A review of       ║
║ hydrogen, carbon, nitrogen, oxygen, sulphur, and chlorine stable isotope   ║
║ fractionation among gaseous molecules, Annual Review of Earth and          ║
║ Planetary Sciences 5 (1977) 65–110                                         ║
║ doi:10.1146/annurev.ea.05.050177.000433                                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║   Author:  Piotr Zarzycki                                                  ║
║   E-mail:  ppzarzycki@lbl.gov                                              ║
║   Private: zarzycki.piotrek@gmail.com                                      ║
║                                                                            ║
║   Lawrence Berkeley National Laboratory                                    ║
║   Earth & Environmental Sciences Area                                      ║
║   1 Cyclotron Road, MS 74-316R                                             ║
║   Berkeley, CA 94720                                                       ║
║                                                                            ║
║   March 2026                                                               ║
║   Cite:                                                                    ║
║                                                                            ║
║ Piotr Zarzycki, Simon  Andren, Amila Prasanna Rajapaksha Palle Gedara,     ║
║ Alexander Meshoulam, William Lawrence, David Dixon, James Rustad           ║
║ Equilibrium isotope fractionation for light-element diatomic molecules     ║
║ from first principles, Earth and Planetary Science Letters (2026)          ║
║ (in revision at the moment)                                                ║
║ also at ar  https://arxiv.org/                                             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║   LICENSE                                                                  ║
║   -------                                                                  ║
║                                                                            ║
║   Isotopologue Mass Generator by Piotr Zarzycki                            ║
║   is licensed under CC BY 4.0.                                             ║
║                                                                            ║
║   To view a copy of this license, visit:                                   ║
║   https://creativecommons.org/licenses/by/4.0/                             ║
║                                                                            ║
║   This is open-source software. You are free to use, modify, and           ║
║   distribute this code, provided that proper attribution is given          ║
║   to the original author. If you use this code in your work,               ║
║   please cite or credit Piotr Zarzycki accordingly.                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝



Physical constants for partition function ratio calculations.

The sources from 1973 - for consistence/reproduction of Richet et al. from 1977
Richet, Y. Bottinga, M. Javoy, A review of hydrogen, carbon, nitrogen, oxygen, sulphur, and chlorine stable isotope fractionation among gaseous molecules, Annual Review of Earth and Planetary Sciences 5 (1977) 65–110. doi:10.1146/annurev.ea.05.050177.000433.


Sources:
    2022: CODATA 2022 (https://physics.nist.gov/cuu/Constants/)
    1973: E. R. Cohen and B. N. Taylor, J. Phys. Chem. Ref. Data 2(4) 663-734 (1973)
"""

CONST_2022 = {
    'h':  6.62607015E-34,   # Planck constant (exact)
    'Na': 6.02214076E23,    # Avogadro constant (exact)
    'R':  8.3144626,        # Gas constant (exact)
    'c':  299792458,        # Speed of light in vacuum (exact)
    'label': '2022',
}

CONST_1973 = {
    'h':  6.62617636E-34,   # TABLE 34.2 page 724
    'Na': 6.02204531E23,    # TABLE 34.2 page 724
    'R':  8.3144126,        # TABLE 33.1 page 719
    'c':  299792458,        # TABLE 33.1 page 717
    'label': '1973',
}


def get_constants(label: str) -> dict:
    """Return the constants set for the given label ('1973' or '2022')."""
    if label == '1973':
        return CONST_1973
    elif label == '2022':
        return CONST_2022
    else:
        raise ValueError(f"Unknown constants set: '{label}'. Use '1973' or '2022'.")


def format_constants_comparison(constants_set: dict) -> str:
    """Format the constants being used, with comparison to 2022 values if using 1973."""
    label = constants_set.get('label', '2022')
    lines = []

    if label == '1973':
        lines.append("Using 1973 CODATA constants (to match Richet 1977)")
        lines.append(f" {'Const':<6s}  {'Value (2022)':>22s}  {'Value (1973)':>22s}"
                     f"  {'Diff (2022-1973)':>22s}")
        lines.append("-" * 80)
        for key, name in [('h', 'h'), ('Na', 'Na'), ('R', 'R'), ('c', 'c')]:
            v2022 = CONST_2022[key]
            v1973 = constants_set[key]
            lines.append(f" {name:<6s}  {v2022:22.10e}  {v1973:22.10e}"
                         f"  {v2022 - v1973:22.10e}")
    else:
        lines.append("Using 2022 CODATA constants")
        lines.append(f" {'Const':<6s}  {'Value':>22s}")
        lines.append("-" * 35)
        for key, name in [('h', 'h'), ('Na', 'Na'), ('R', 'R'), ('c', 'c')]:
            lines.append(f" {name:<6s}  {constants_set[key]:22.10e}")

    lines.append("")
    return "\n".join(lines)




"""
Isotopologue data class and input file parser.

Input file format (whitespace separated, # comments, blank lines skipped):
    # label  omega  omega_xe  B0  mass1  mass2  symmetry  alpha
    H2    4401.118  121.284  59.3251  1.00782503223  1.0080   2  3.0258
    HD    3812.293   90.908  44.6613  1.0080         2.01410  1  2.0034

First data line = light isotopologue, second = heavy isotopologue.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Isotopologue:
    """
    Diatomic isotopologue spectroscopic data.

    Attributes
    ----------
    name : str
        Label for the isotopologue (e.g., 'H2', 'HD', '12C16O').
    omega : float
        Harmonic vibrational frequency omega_e (cm-1).
    omega_xe : float
        First anharmonicity constant omega_e*x_e (cm-1).
    B0 : float
        Rotational constant B0 (cm-1).
    mass1 : float
        Mass of atom 1 (amu).
    mass2 : float
        Mass of atom 2 (amu).
    s : int
        Symmetry number (1 for heteronuclear, 2 for homonuclear).
    alpha : float
        Rotation-vibration interaction constant alpha_e (cm-1).
    """
    name: str
    omega: float
    omega_xe: float
    B0: float
    mass1: float
    mass2: float
    s: int = 1
    alpha: float = 0.0

    @property
    def M(self) -> float:
        """Total molecular mass (amu)."""
        return self.mass1 + self.mass2

    @property
    def Be(self) -> float:
        """Equilibrium rotational constant Be = B0 + alpha_e/2 (cm-1)."""
        return self.B0 + self.alpha * 0.5

    def __str__(self) -> str:
        return (f"{self.name:>8s}  "
                f"\u03c9e={self.omega:10.3f}  "
                f"\u03c9exe={self.omega_xe:9.4f}  "
                f"B0={self.B0:10.6f}  "
                f"M={self.M:10.5f}  s={self.s}  "
                f"Be={self.Be:10.6f}  "
                f"\u03b1e={self.alpha:.6f}")


def parse_input_file(filepath: str) -> Tuple[Isotopologue, Isotopologue]:
    """
    Parse input file with two isotopologue lines (light first, heavy second).
    Piotr: this is at the moment assumed (order of isotopologues) nothing happend if you 
    switch order 

    Parameters
    ----------
    filepath : str
        Path to input text file.

    Returns
    -------
    (light, heavy) : tuple of Isotopologue

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file does not contain exactly two data lines or fields are missing.
    """
    data_lines = []
    with open(filepath, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            data_lines.append(line)

    if len(data_lines) < 2:
        raise ValueError(
            f"Input file must contain at least 2 data lines (light and heavy). "
            f"Found {len(data_lines)}."
        )
    if len(data_lines) > 2:
        print(f"Warning: input file has {len(data_lines)} data lines; "
              f"using only the first two.")

    isotopologues = []
    labels = ["light (line 1)", "heavy (line 2)"]
    for i, line in enumerate(data_lines[:2]):
        tokens = line.split()
        if len(tokens) < 8:
            raise ValueError(
                f"{labels[i]}: found {len(tokens)} fields, expected 8:\n"
                f"  label  omega  omega_xe  B0  mass1  mass2  symmetry  alpha\n"
                f"  Line: {line}"
            )
        try:
            iso = Isotopologue(
                name=tokens[0],
                omega=float(tokens[1]),
                omega_xe=float(tokens[2]),
                B0=float(tokens[3]),
                mass1=float(tokens[4]),
                mass2=float(tokens[5]),
                s=int(tokens[6]),
                alpha=float(tokens[7]),
            )
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Error parsing {labels[i]}:\n  {line}\n  {e}"
            ) from e
        isotopologues.append(iso)

    light = isotopologues[0]
    heavy = isotopologues[1]
    return light, heavy


"""
Core partition function ratio calculation.

Follows the methodology of:
    P. Richet (1977), "Pressure effect on the isotopic fractionation at high
    temperature", J. Chem. Phys. 67, 1007.

specifically I implemented equations from from :
    Richet, Y. Bottinga, M. Javoy, A review of hydrogen, carbon, nitrogen, oxygen, sulphur, and chlorine stable isotope fractionation among gaseous molecules, Annual Review of Earth and Planetary Sciences 5 (1977) 65–110. doi:10.1146/annurev.ea.05.050177.000433.

Equation numbers in comments refer to that paper Richet 1977 Annual Review ... .
"""

import numpy as np
from typing import NamedTuple


class PartitionResult(NamedTuple):
    """All components of the partition function ratio Q'/Q (heavy/light)."""
    T: float                  # temperature (K)
    QRatio_tran: float        # (M'/M)^(3/2)                         eq. 34
    QRatio_G0: float          # exp[-(G0'-G0)hc/kT]                  eq. 35
    QRatio_ZVPE_harm: float   # exp[-1/2(u'-u)]                      eq. 35
    QRatio_ZVPE_anh: float    # exp[1/4(x'u'-xu)]                    eq. 35
    QRatio_0: float           # product of G0, ZVPE_harm, ZVPE_anh   eq. 35
    QRatio_Vibration: float   # harmonic vibrational ratio            eq. 36
    QRatio_anh: float         # anharmonic vibrational correction     eq. 37
    ss_ratio: float           # (s*sigma_light)/(s'*sigma_heavy)      eq. 38
    QRatio_rot_38: float      # rotational ratio, power series        eq. 38
    QRatio_rot: float         # rotational ratio, direct summation    eq. 28
    QRatio_rotVib: float      # rotation-vibration interaction        eq. 39
    QRatio_total: float       # total partition function ratio        eq. 32
    beta_1000ln: float        # 1000 * ln(Q'/Q)
    # auxiliary quantities for diagnostics
    delta_light: float
    delta_heavy: float
    sigma_light: float
    sigma_heavy: float
    u_light: float
    u_heavy: float
    ux_light: float
    ux_heavy: float
    j_max_used: int
    hc_over_RT: float


def _calc_G0(Be: float, alpha: float, u: float, ux: float) -> float:
    """
    Calculate G0 * hc/kT (eq. 35 of Richet 1977).

    All inputs must already be in dimensionless units (multiplied by hc/kT).

    G0 = Be/4 + alpha*u/(12*Be) + [alpha*u/(12*Be)]^2 / Be - ux/4
    """
    term1 = Be / 4.0
    aub = alpha * u / (12.0 * Be)
    term2 = aub
    term3 = aub * aub / Be
    term4 = -ux / 4.0
    return term1 + term2 + term3 + term4


def _rot_series(sigma: float) -> float:
    """
    Power series expansion for rotational partition function (eq. 38).

    Q_rot ~ (1/sigma) * [1 + sigma/3 + sigma^2/15 + 4*sigma^3/315]
    Returns the bracketed factor.
    """
    return 1.0 + sigma / 3.0 + sigma**2 / 15.0 + 4.0 * sigma**3 / 315.0


def partition_function_ratio(
    heavy: Isotopologue,
    light: Isotopologue,
    T: float,
    constants_set: dict,
    use_variable_j: bool = True,
    j_convergence_thresh: float = 9e-5,
    use_Be_in_rotation: bool = True,
    max_J: int = 1000,
) -> PartitionResult:
    """
    Calculate the partition function ratio Q'/Q (heavy/light).

    Does NOT mutate the input Isotopologue objects.

    Parameters
    ----------
    heavy : Isotopologue
        The heavier isotopologue (primed quantities, ').
    light : Isotopologue
        The lighter isotopologue.
    T : float
        Temperature in Kelvin.
    constants_set : dict
        Physical constants with keys 'h', 'Na', 'R', 'c'.
    use_variable_j : bool
        If True, determine J_max from convergence criterion.
    j_convergence_thresh : float
        Threshold for convergence of the rotational sum ratio.
    use_Be_in_rotation : bool
        If True, use Be in eq. 28 summation; otherwise use B0.
    max_J : int
        Maximum J for rotational summation.

    Returns
    -------
    PartitionResult
        Named tuple with all ratio components and diagnostics.
    """
    h = constants_set['h']
    Na = constants_set['Na']
    R = constants_set['R']
    c = constants_set['c']

    # conversion factor: cm-1 -> dimensionless  (hcNa/RT)
    # 100 converts cm-1 to m-1
    CM_TO_M = 100.0
    factor = CM_TO_M * c * h * Na
    RT = T * R
    hc_over_RT = factor / RT

    # ---- convert spectroscopic constants to dimensionless ----
    u_light = light.omega * hc_over_RT
    u_heavy = heavy.omega * hc_over_RT
    ux_light = light.omega_xe * hc_over_RT
    ux_heavy = heavy.omega_xe * hc_over_RT
    sigma_light = light.B0 * hc_over_RT
    sigma_heavy = heavy.B0 * hc_over_RT
    Be_light = light.Be * hc_over_RT
    Be_heavy = heavy.Be * hc_over_RT
    alpha_light = light.alpha * hc_over_RT
    alpha_heavy = heavy.alpha * hc_over_RT

    # ---- translation (eq. 34) ----
    QRatio_tran = np.power(heavy.M / light.M, 1.5)

    # ---- G0 correction (eq. 35) ----
    G0_light = _calc_G0(Be_light, alpha_light, u_light, ux_light)
    G0_heavy = _calc_G0(Be_heavy, alpha_heavy, u_heavy, ux_heavy)
    QRatio_G0 = np.exp(-(G0_heavy - G0_light))

    # ---- ZVPE harmonic (eq. 35) ----
    QRatio_ZVPE_harm = np.exp(-(u_heavy - u_light) / 2.0)

    # ---- ZVPE anharmonic (eq. 35) ----
    QRatio_ZVPE_anh = np.exp((ux_heavy - ux_light) / 4.0)

    # ---- combined (Q'/Q)_0 ----
    QRatio_0 = QRatio_G0 * QRatio_ZVPE_harm * QRatio_ZVPE_anh

    # ---- vibrational harmonic (eq. 36) ----
    QRatio_Vibration = (1.0 - np.exp(-u_light)) / (1.0 - np.exp(-u_heavy))

    # ---- vibrational anharmonic (eq. 37) ----
    exp_uh = np.exp(-u_heavy)
    exp_ul = np.exp(-u_light)
    QRatio_anh_top = 1.0 - 2.0 * ux_heavy * exp_uh / ((1.0 - exp_uh) ** 2)
    QRatio_anh_bot = 1.0 - 2.0 * ux_light * exp_ul / ((1.0 - exp_ul) ** 2)
    QRatio_anh = QRatio_anh_top / QRatio_anh_bot

    # ---- rotation: power series (eq. 38) ----
    QRatio_rot_38_top = light.s * sigma_light * _rot_series(sigma_heavy)
    QRatio_rot_38_bot = heavy.s * sigma_heavy * _rot_series(sigma_light)
    QRatio_rot_38 = QRatio_rot_38_top / QRatio_rot_38_bot

    # ---- rotation: direct summation (eq. 28) ----
    sig_rot_light = Be_light if use_Be_in_rotation else sigma_light
    sig_rot_heavy = Be_heavy if use_Be_in_rotation else sigma_heavy

    # fixed summation
    J_arr = np.arange(0, max_J + 1, dtype=np.float64)
    Qrot_light_fixed = np.sum(
        (2.0 * J_arr + 1.0) * np.exp(-sig_rot_light * J_arr * (J_arr + 1.0))
    )
    Qrot_heavy_fixed = np.sum(
        (2.0 * J_arr + 1.0) * np.exp(-sig_rot_heavy * J_arr * (J_arr + 1.0))
    )
    QRatio_rot_fixed = (light.s / heavy.s) * Qrot_heavy_fixed / Qrot_light_fixed

    # variable J with convergence check
    variable_j_max = max_J
    QRatio_rot_var = QRatio_rot_fixed
    if use_variable_j:
        Qrot_l_accum = 0.0
        Qrot_h_accum = 0.0
        ratio_old = 0.0
        for jj in range(max_J + 1):
            weight = 2.0 * jj + 1.0
            Qrot_l_accum += weight * np.exp(-sig_rot_light * jj * (jj + 1))
            Qrot_h_accum += weight * np.exp(-sig_rot_heavy * jj * (jj + 1))
            ratio_new = (light.s / heavy.s) * Qrot_h_accum / Qrot_l_accum
            if jj > 0 and abs(ratio_new - ratio_old) < j_convergence_thresh:
                variable_j_max = jj
                QRatio_rot_var = ratio_new
                break
            ratio_old = ratio_new
        else:
            QRatio_rot_var = ratio_old
            variable_j_max = max_J

    QRatio_rot = QRatio_rot_var if use_variable_j else QRatio_rot_fixed
    j_max_used = variable_j_max if use_variable_j else max_J

    # ---- symmetry ratio ----
    ss_ratio = (light.s * sigma_light) / (heavy.s * sigma_heavy)

    # ---- rotation-vibration interaction (eq. 39) ----
    # delta = alpha / sigma (using B0-based sigma)
    delta_light = alpha_light / sigma_light if sigma_light != 0 else 0.0
    delta_heavy = alpha_heavy / sigma_heavy if sigma_heavy != 0 else 0.0

    # Bose-Einstein factor: (exp(u) - 1), NOT exp(u - 1)
    if alpha_light == 0.0 and alpha_heavy == 0.0:
        QRatio_rotVib = 1.0
    else:
        QRatio_rotVib = ((1.0 + delta_heavy / (np.exp(u_heavy) - 1.0)) /
                         (1.0 + delta_light / (np.exp(u_light) - 1.0)))

    # ---- total (eq. 32) ----
    QRatio_total = (QRatio_tran *
                    QRatio_G0 *
                    QRatio_ZVPE_harm *
                    QRatio_ZVPE_anh *
                    QRatio_Vibration *
                    QRatio_anh *
                    QRatio_rot *
                    QRatio_rotVib)

    beta_1000ln = 1000.0 * np.log(QRatio_total)

    return PartitionResult(
        T=T,
        QRatio_tran=QRatio_tran,
        QRatio_G0=QRatio_G0,
        QRatio_ZVPE_harm=QRatio_ZVPE_harm,
        QRatio_ZVPE_anh=QRatio_ZVPE_anh,
        QRatio_0=QRatio_0,
        QRatio_Vibration=QRatio_Vibration,
        QRatio_anh=QRatio_anh,
        ss_ratio=ss_ratio,
        QRatio_rot_38=QRatio_rot_38,
        QRatio_rot=QRatio_rot,
        QRatio_rotVib=QRatio_rotVib,
        QRatio_total=QRatio_total,
        beta_1000ln=beta_1000ln,
        delta_light=delta_light,
        delta_heavy=delta_heavy,
        sigma_light=sigma_light,
        sigma_heavy=sigma_heavy,
        u_light=u_light,
        u_heavy=u_heavy,
        ux_light=ux_light,
        ux_heavy=ux_heavy,
        j_max_used=j_max_used,
        hc_over_RT=hc_over_RT,
    )


"""
Output formatting and file writing for partition function ratio results.
"""

import datetime
from typing import List


def format_table(
    result: PartitionResult,
    heavy: Isotopologue,
    light: Isotopologue,
    use_variable_j: bool,
) -> str:
    """
    Format the detailed contribution table for a single temperature.

    Reproduces Table 4 of Richet (1977) with all individual contributions
    to the partition function ratio.

    This is for benchmarking and testing, first part of this project was to reproduce exacty 
    values from Richet et al., which was possible only if we use 
    exact physical constants from 1973 and exact atomic mass from 1973 

    """
    r = result
    T_C = r.T - 273.15
    sep = "-" * 78

    lines = []
    lines.append("")
    lines.append("=" * 78)
    lines.append(f" T = {r.T:10.2f} K  ({T_C:8.2f} \u00b0C)")
    lines.append(f" hc/RT = {r.hc_over_RT:.10f}")
    lines.append("")
    lines.append(" Table 4. Contributions to the partition function ratio")
    lines.append(f"                          Eq.       {heavy.name}/{light.name}"
                 f"     at T = {T_C:.1f}\u00b0C    {r.T} K")
    lines.append(sep)

    lines.append(f"  1   (M'/M)^3/2           34    {r.QRatio_tran:13.7f}"
                 f"   (Q'/Q) translation")
    lines.append(f"  2   exp-(G'-G)hc/kT      35    {r.QRatio_G0:13.7f}"
                 f"   (Q'/Q) G0 correction")
    lines.append(f"  3   exp-1/2(u'-u)        35    {r.QRatio_ZVPE_harm:13.7f}"
                 f"   (Q'/Q) ZVPE harmonic")
    lines.append(f"  4   exp 1/4(x'u'-xu)     35    {r.QRatio_ZVPE_anh:13.7f}"
                 f"   (Q'/Q) ZVPE anharmonic")
    lines.append(f"  5   (Q'/Q)0              35    {r.QRatio_0:13.7f}"
                 f"   product of 2,3,4")
    lines.append(f"  6   (Q'/Q)vib            36    {r.QRatio_Vibration:13.7f}"
                 f"   (Q'/Q) vib. harmonic")
    lines.append(f"  7   (Q'/Q)anh            37    {r.QRatio_anh:13.7f}"
                 f"   (Q'/Q) vib. anharmonic")
    lines.append(f"  8   (s'\u03c3'/s\u03c3)            38    {r.ss_ratio:13.7f}"
                 f"   symmetry ratio")

    lines.append(f"  9   (Q'/Q)rot            38    {r.QRatio_rot_38:13.7f}"
                 f"   (Q'/Q) rot. power series")

    if use_variable_j:
        j_label = f"var J=0..{r.j_max_used}"
    else:
        j_label = f"fix J=0..1000"
    lines.append(f" 10   (Q'/Q)rot            28    {r.QRatio_rot:13.7f}"
                 f"   (Q'/Q) rot. summation ({j_label})")

    lines.append(f" 11   (Q'/Q)rot-vib        39    {r.QRatio_rotVib:13.7f}"
                 f"   (Q'/Q) rot-vib interaction")
    lines.append(sep)
    lines.append(f" 12   (Q'/Q)tot            32    {r.QRatio_total:13.7f}"
                 f"   total = 1*5*6*7*10*11")
    lines.append(f"      1000*ln(Q'/Q)              {r.beta_1000ln:13.6f}")
    lines.append(sep)

    lines.append(f" \u03b4   = {r.delta_light:13.6e}"
                 f"    \u03b4'  = {r.delta_heavy:13.6e}")
    lines.append(f" \u03c3   = {r.sigma_light:13.6e}"
                 f"    \u03c3'  = {r.sigma_heavy:13.6e}")
    lines.append(f" u   = {r.u_light:13.6e}"
                 f"    u'  = {r.u_heavy:13.6e}")
    lines.append(f" ux  = {r.ux_light:13.6e}"
                 f"    u'x'= {r.ux_heavy:13.6e}")
    lines.append(sep)

    return "\n".join(lines)







# PPPZ


def build_log_header(
    input_file: str,
    light: Isotopologue,
    heavy: Isotopologue,
    constants_set: dict,
    temp_start: float,
    temp_stop: float,
    temp_step: float,
    n_temps: int,
    use_variable_j: bool,
    j_thresh: float,
    use_Be_in_rotation: bool,
    max_J: int,
) -> str:
    """Build the header block for the log file."""

    pbanner = '''
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║      Partition Function Ratio Calculator for Diatomic Isotopologues.       ║
║                        LBNL 2026 version 1.0                               ║
║                                                                            ║
║ Reference for the theory: Richet, Y. Bottinga, M. Javoy, A review of       ║
║ hydrogen, carbon, nitrogen, oxygen, sulphur, and chlorine stable isotope   ║
║ fractionation among gaseous molecules, Annual Review of Earth and          ║
║ Planetary Sciences 5 (1977) 65–110                                         ║
║ doi:10.1146/annurev.ea.05.050177.000433                                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║   Author:  Piotr Zarzycki                                                  ║
║   E-mail:  ppzarzycki@lbl.gov                                              ║
║   Private: zarzycki.piotrek@gmail.com                                      ║
║                                                                            ║
║   Lawrence Berkeley National Laboratory                                    ║
║   Earth & Environmental Sciences Area                                      ║
║   1 Cyclotron Road, MS 74-316R                                             ║
║   Berkeley, CA 94720                                                       ║
║                                                                            ║
║   March 2026                                                               ║
║   Cite:                                                                    ║
║                                                                            ║
║ Piotr Zarzycki, Simon  Andren, Amila Prasanna Rajapaksha Palle Gedara,     ║
║ Alexander Meshoulam, William Lawrence, David Dixon, James Rustad           ║
║ Equilibrium isotope fractionation for light-element diatomic molecules     ║
║ from first principles, Earth and Planetary Science Letters (2026)          ║
║                                                                            ║
║ also at ar  https://arxiv.org/                                             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
'''



    banner = pbanner +'\n'
    banner += ("=" * 78)
    lines = []
    lines.append(banner)
    lines.append(" Partition Function Ratio Calculator")
    lines.append(" Methodology: Richet (1977), J. Chem. Phys. 67, 1007")
    lines.append(f" Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f" Input file: {input_file}")
    lines.append(banner)
    lines.append("")
    lines.append(format_constants_comparison(constants_set))
    lines.append(f" Light isotopologue: {light}")
    lines.append(f" Heavy isotopologue: {heavy}")
    lines.append("")
    lines.append(f" Temperature range: {temp_start:.2f} to {temp_stop:.2f} K,"
                 f" step {temp_step:.2f} K")
    lines.append(f" Number of temperatures: {n_temps}")
    lines.append(f" Variable J convergence: {use_variable_j}"
                 f" (threshold = {j_thresh:.1e})")
    lines.append(f" Use Be in eq. 28: {use_Be_in_rotation}")
    lines.append(f" Max J: {max_J}")
    lines.append(banner)
    return "\n".join(lines)


def format_summary_table(
    results: List[PartitionResult],
    heavy: Isotopologue,
    light: Isotopologue,
) -> str:
    """Format a compact summary table of results at all temperatures."""
    sep = "-" * 78
    lines = []
    lines.append("")
    lines.append("=" * 78)
    lines.append(f" Summary: {heavy.name} / {light.name}")
    lines.append(sep)
    lines.append(f" {'T(K)':>10s}  {'T(\u00b0C)':>10s}  {'Q\'/Q (total)':>14s}"
                 f"  {'1000*ln(Q\'/Q)':>14s}")
    lines.append(sep)
    for r in results:
        lines.append(f" {r.T:10.2f}  {r.T - 273.15:10.2f}"
                     f"  {r.QRatio_total:14.7f}  {r.beta_1000ln:14.6f}")
    lines.append(sep)
    return "\n".join(lines)


def write_log_file(
    filepath: str,
    header: str,
    tables: List[str],
    summary: str,
) -> None:
    """Write the full log file with header, detailed tables, and summary."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write("\n")
        for table in tables:
            f.write(table)
            f.write("\n")
        f.write(summary)
        f.write("\n")


def write_beta_file(
    filepath: str,
    results: List[PartitionResult],
    heavy: Isotopologue,
    light: Isotopologue,
) -> None:
    """
    Write the temperature vs beta value file.

    Columns: T(K)  T(C)  Q'/Q(total)  1000*ln(Q'/Q)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Partition function ratio: {heavy.name} / {light.name}\n")
        f.write(f"# Generated: "
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Methodology: Richet (1977), J. Chem. Phys. 67, 1007\n")
        f.write(f"#\n")
        f.write(f"# Light: {light}\n")
        f.write(f"# Heavy: {heavy}\n")
        f.write(f"#\n")
        f.write(f"# {'T(K)':>10s}  {'T(C)':>10s}"
                f"  {'beta=Q\'/Q':>14s}  {'1000*ln(beta)':>14s}\n")
        for r in results:
            f.write(f"  {r.T:10.2f}  {r.T - 273.15:10.2f}"
                    f"  {r.QRatio_total:14.7f}  {r.beta_1000ln:14.6f}\n")




#!/usr/bin/env python3
"""
Partition Function Ratio Calculator for Diatomic Isotopologues.


Calculates isotopologue partition function ratios following the methodology
of Richet (1977)

Usage examples:
    python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 1273.15 --temp-step 100
    python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 1273.15 --temp-step 50 --constants 1973
    python lbnl_beta_richet.py input.txt --temp-start 273.15 --temp-stop 273.15 --temp-step 1 --constants 2022

Input file format (see isotopologue.py or example_input.txt):
    # label  omega  omega_xe  B0  mass1  mass2  symmetry  alpha
    H2    4401.118  121.284  59.3251  1.00782503223  1.0080   2  3.0258
    HD    3812.293   90.908  44.6613  1.0080         2.01410  1  2.0034


"""

import argparse
import sys
import os
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Partition function ratio calculator for diatomic isotopologues. "
            "Piotr Zarzycki, Lawrence Berkeley National Laboratory"
            "Follows Richet (1977)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Input file format (whitespace separated, # = comment):\n"
            "  # label  omega  omega_xe  B0  mass1  mass2  symmetry  alpha\n"
            "  H2  4401.118  121.284  59.3251  1.00782503223  1.0080  2  3.0258\n"
            "  HD  3812.293   90.908  44.6613  1.0080  2.01410177812  1  2.0034\n"
            "\n"
            "First data line = light isotopologue\n"
            "Second data line = heavy isotopologue\n"
        ),
    )

    # required
    parser.add_argument(
        "input_file",
        help="Path to input text file with isotopologue data.",
    )
    parser.add_argument(
        "--temp-start", type=float, required=True,
        help="Start temperature in Kelvin.",
    )
    parser.add_argument(
        "--temp-stop", type=float, required=True,
        help="Stop temperature in Kelvin (inclusive).",
    )
    parser.add_argument(
        "--temp-step", type=float, required=True,
        help="Temperature step in Kelvin.",
    )

    # optional
    parser.add_argument(
        "--constants", choices=["1973", "2022"], default="2022",
        help="CODATA constants set to use (default: 2022).",
    )
    parser.add_argument(
        "--fixed-j", action="store_true", default=False,
        help="Use fixed J=0..1000 summation instead of variable convergence.",
    )
    parser.add_argument(
        "--j-thresh", type=float, default=1e-10,
        help="Convergence threshold for variable J (default: 9e-5).",
    )
    parser.add_argument(
        "--use-B0-in-rotation", action="store_true", default=False,
        help="Use B0 instead of Be in eq. 28 rotational summation.",
    )
    parser.add_argument(
        "--max-j", type=int, default=1000,
        help="Maximum J for rotational summation (default: 1000).",
    )
    parser.add_argument(
        "--output-prefix", type=str, default=None,
        help="Prefix for output files (default: heavy_light).",
    )

    return parser


def main():
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # ---- validate input file ----
    if not os.path.isfile(args.input_file):
        print(f"Error: input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # ---- parse input ----
    try:
        light, heavy = parse_input_file(args.input_file)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # ---- constants ----
    constants_set = get_constants(args.constants)

    # ---- temperature array ----
    # small epsilon to include endpoint
    epsilon = args.temp_step * 0.0001
    temperatures = np.arange(args.temp_start,
                             args.temp_stop + epsilon,
                             args.temp_step)

    if len(temperatures) == 0:
        print("Error: temperature range produced no points. "
              "Check --temp-start, --temp-stop, --temp-step.", file=sys.stderr)
        sys.exit(1)

    # ---- flags ----
    use_variable_j = not args.fixed_j
    use_Be_in_rotation = not args.use_B0_in_rotation
    j_thresh = args.j_thresh
    max_J = args.max_j

    # ---- output file names ----
    if args.output_prefix:
        prefix = args.output_prefix
    else:
        prefix = f"{heavy.name}_{light.name}"

    log_path = f"{prefix}.log"
    beta_path = f"{prefix}_beta.txt"
    ptable2_path = f"{prefix}_table2.txt"

    # ---- build log header ----
    header = build_log_header(
        input_file=args.input_file,
        light=light,
        heavy=heavy,
        constants_set=constants_set,
        temp_start=args.temp_start,
        temp_stop=args.temp_stop,
        temp_step=args.temp_step,
        n_temps=len(temperatures),
        use_variable_j=use_variable_j,
        j_thresh=j_thresh,
        use_Be_in_rotation=use_Be_in_rotation,
        max_J=max_J,
    )

    # ---- print header ----
    print(header)

    # ---- run calculations ----
    results = []
    tables = []

    for T in temperatures:
        result = partition_function_ratio(
            heavy=heavy,
            light=light,
            T=T,
            constants_set=constants_set,
            use_variable_j=use_variable_j,
            j_convergence_thresh=j_thresh,
            use_Be_in_rotation=use_Be_in_rotation,
            max_J=max_J,
        )
        results.append(result)

        table_str = format_table(result, heavy, light, use_variable_j)
        tables.append(table_str)

        # print each table to console as it is computed
        print(table_str)

    # ---- summary ----
    summary = format_summary_table(results, heavy, light)
    print(summary)

    # ---- write output files ----
    write_log_file(log_path, header, tables, summary)
    write_beta_file(beta_path, results, heavy, light)

    print(f"\n Log file written to:  {log_path}")
    print(f" Beta file written to: {beta_path}")


if __name__ == "__main__":
    main()



