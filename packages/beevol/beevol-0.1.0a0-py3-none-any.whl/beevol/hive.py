# beevol/hive.py
from __future__ import annotations

from typing import Dict, Sequence, List, Tuple, Any
import itertools
import re

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, find_peaks
from scipy.stats import linregress

__all__ = [
    # config / parsing
    "DEFAULT_CONFIG", "parse_hurst_spec",
    # core utils
    "generate_series", "extract_extrema", "extrema_alignment_score", "divergence",
    "zscore_rolling", "persistence_transform",
    # estimators
    "permutation_entropy", "hurst_rs", "hurst_dfa", "hurst_vt", "hurst_spectral",
    # feature calc
    "compute_features",
]

# ======================================================================
# CONFIG
# ======================================================================
DEFAULT_CONFIG: Dict[str, Any] = {
    # Data
    "data_source": "TEST",
    "target_columns": ["value"],

    # Synthetic generator (ignored for CSV input)
    "N": 1000,
    "phi1": 0.3,
    "phi2": 0.9,
    "sigma1": 0.3,
    "sigma2": 1.5,
    "T": 200,
    "drift": 0.0,
    "scale": 1.0,
    "seed": 42,

    # Savitzky–Golay smoothing & extrema detection parameters
    # (SG is ALWAYS applied to the raw series before ANY feature computation;
    #  these params are still user-configurable)
    "sg_window": 7,
    "polyorder": 2,

    "prominence": 0.5,
    "tolerance": 5,

    # Rolling windows
    "entropy_window": 20,         
    "hurst_window_h_rs": 20,
    "hurst_window_h_dfa": 20,
    "hurst_window_h_vt": 20,
    "hurst_window_h_sp": 20,

    # Permutation entropy
    "m": 3,
    "delay": 1,
    "run_PE": True,

    # Hurst specs with modifiers
    "run_hurst": [
        "H_RS",
        "H_DFA",
        "H_VT",
        "H_SP",
    ],

    # default z window for .z() if omitted
    "hurst_z_window": 100,

    # misc
    "verbose": True,
    "output": [],
    "return_figs": False,
}

# ======================================================================
# PARSING OF HURST SPECS
# ======================================================================

_HURST_BASES = {"H_RS", "H_DFA", "H_VT", "H_SP"}

# .z() or .z(50)  -> group(1) holds the window if present
_Z_RE = re.compile(r"\.z(?:\((\d+)\))?\s*\(\)?")
# .perst()        -> boolean flag
_PERST_RE = re.compile(r"\.perst\(\)")

def parse_hurst_spec(spec: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parse strings like:
        "H_RS"
        "H_RS.perst()"
        "H_DFA.perst().z()"
        "H_VT.z(50)"
    Returns: (base, {"perst": bool, "z": bool, "z_window": Optional[int]})
    """
    original = spec.strip()
    base = original.split(".", 1)[0]
    if base not in _HURST_BASES:
        raise ValueError(f"Unknown Hurst base '{base}' in spec '{spec}'.")

    perst = bool(_PERST_RE.search(original))
    z_match = _Z_RE.search(original)

    z_flag = False
    z_window = None
    if z_match:
        z_flag = True
        if z_match.group(1) is not None:
            z_window = int(z_match.group(1))

    return base, {"perst": perst, "z": z_flag, "z_window": z_window}

# ======================================================================
# CORE UTILITIES
# ======================================================================

def generate_series(cfg: Dict[str, Any]) -> pd.Series:
    np.random.seed(cfg["seed"])
    x = np.zeros(cfg["N"], dtype=float)
    for t in range(1, cfg["N"]):
        regime = (t // cfg["T"]) % 2
        phi = cfg["phi1"] if regime == 0 else cfg["phi2"]
        sigma = cfg["sigma1"] if regime == 0 else cfg["sigma2"]
        x[t] = cfg["drift"] + phi * x[t - 1] + np.random.normal(scale=sigma)
    return pd.Series(x * cfg["scale"])


def extract_extrema(series: pd.Series, prominence: float):
    pks, _ = find_peaks(series.values, prominence=prominence)
    trs, _ = find_peaks(-series.values, prominence=prominence)
    return pks, trs


def extrema_alignment_score(orig_idxs, sm_idxs, tol: int) -> float:
    if len(orig_idxs) == 0:
        return np.nan
    matched = sum(any(abs(o - s) <= tol for s in sm_idxs) for o in orig_idxs)
    return matched / len(orig_idxs)


def divergence(max_series: pd.Series, min_series: pd.Series) -> pd.Series:
    return max_series - min_series


def zscore_rolling(arr: np.ndarray, window: int) -> np.ndarray:
    """Rolling z-score on a 1D array. Falls back to global z if window >= len(arr)."""
    arr = np.asarray(arr, float)
    win = max(1, int(window))
    if win >= len(arr):
        mu = arr.mean()
        sd = arr.std() or 1.0
        return (arr - mu) / sd
    s = pd.Series(arr)
    mean = s.rolling(win, min_periods=1).mean()
    std = s.rolling(win, min_periods=1).std().replace(0, 1.0)
    return ((s - mean) / std).to_numpy()


def persistence_transform(h_values: np.ndarray | float) -> np.ndarray | float:
    """
    Transform H (0..1) into "persistence intensity": |2H - 1|.
    Accepts scalar or array; preserves NaNs.
    """
    hv = np.asarray(h_values, dtype=float)
    out = np.abs(2 * hv - 1)
    out[np.isnan(hv)] = np.nan
    # return scalar if input was scalar
    return out.item() if np.isscalar(h_values) else out

# ======================================================================
# ESTIMATORS
# ======================================================================

def permutation_entropy(series: Sequence[float], m: int = 3, delay: int = 1) -> float:
    x = np.asarray(series, float)
    n = len(x)
    if n < m * delay:
        return np.nan
    perms = np.array(list(itertools.permutations(range(m))))
    counts = np.zeros(len(perms), dtype=int)
    for i in range(n - delay * (m - 1)):
        sub = x[i:(i + delay * m):delay]
        rank = np.argsort(sub)
        # faster than looping perms, but we'll keep simple for clarity
        for j, p in enumerate(perms):
            if np.array_equal(rank, p):
                counts[j] += 1
                break
    p = counts[counts > 0] / counts.sum() if counts.sum() else np.array([1.0])
    return -np.sum(p * np.log(p))


def hurst_rs(series: Sequence[float]) -> float:
    x = np.asarray(series, float)
    if len(x) < 20:
        return np.nan
    x = x - x.mean()
    Y = np.cumsum(x)
    R = Y.max() - Y.min()
    S = x.std()
    return np.log(R / S) / np.log(len(x)) if S > 0 else np.nan


def hurst_dfa(series: Sequence[float]) -> float:
    x = np.asarray(series, float)
    N = len(x)
    if N < 20:
        return np.nan
    profile = np.cumsum(x - np.mean(x))
    max_scale = N // 4
    scales = np.unique(np.floor(np.logspace(np.log10(4), np.log10(max_scale), num=20)).astype(int))
    Fs, valid = [], []
    for s in scales:
        nseg = N // s
        if nseg < 2:
            continue
        rms_vals = []
        for v in range(nseg):
            seg = profile[v * s:(v + 1) * s]
            t = np.arange(s)
            coeffs = np.polyfit(t, seg, 1)
            trend = np.polyval(coeffs, t)
            rms_vals.append(np.sqrt(np.mean((seg - trend) ** 2)))
        mean_rms = np.mean(rms_vals)
        if mean_rms > 0:
            Fs.append(mean_rms)
            valid.append(s)
    if len(valid) < 2:
        return np.nan
    slope, *_ = linregress(np.log(valid), np.log(Fs))
    return slope


def hurst_vt(series: Sequence[float]) -> float:
    x = np.asarray(series, float)
    N = len(x)
    if N < 20:
        return np.nan
    max_scale = N // 4
    scales = np.unique(np.floor(np.logspace(np.log10(2), np.log10(max_scale), num=20)).astype(int))
    Vs, valid = [], []
    for s in scales:
        nseg = N // s
        if nseg < 2:
            continue
        block_means = [np.mean(x[i * s:(i + 1) * s]) for i in range(nseg)]
        v = np.var(block_means)
        if v > 0:
            Vs.append(v)
            valid.append(s)
    if len(valid) < 2:
        return np.nan
    slope, *_ = linregress(np.log(valid), np.log(Vs))
    return (slope + 2) / 2.0


def hurst_spectral(series: Sequence[float]) -> float:
    x = np.asarray(series, float)
    N = len(x)
    if N < 20:
        return np.nan
    f = np.fft.rfftfreq(N)
    P = np.abs(np.fft.rfft(x)) ** 2
    mask = f > 0
    if mask.sum() < 2:
        return np.nan
    coeffs = np.polyfit(np.log(f[mask]), np.log(P[mask]), 1)
    return (1 - coeffs[0]) / 2.0


_HURST_FUNCS = {
    "H_RS": hurst_rs,
    "H_DFA": hurst_dfa,
    "H_VT": hurst_vt,
    "H_SP": hurst_spectral,
}

# ======================================================================
# FEATURE COMPUTATION
# ======================================================================

def compute_features(
    raw_series: pd.Series,
    idxs: Sequence[int],
    pe_window: int,
    hurst_specs: List[Tuple[str, Dict[str, Any]]],
    hurst_windows: Dict[str, int],
    cfg: Dict[str, Any],
) -> pd.DataFrame:

    """
      1. Savitzky–Golay smoothing is applied to raw_series once.
      2. For each Hurst spec:
         a. Optionally apply rolling z-score to the *smoothed* series (if .z()).
         b. Compute the Hurst value on that segment.
         c. Optionally apply persistence transform (if .perst()) to the Hurst result.

    Parameters
    ----------
    raw_series : pd.Series
        ORIGINAL raw series (not smoothed). This function will SG-smooth internally.
    idxs : sequence[int]
        Positions (integer indices) at which to compute features (extrema).
    pe_window : int
        Rolling window for PE segments.
    hurst_specs : list[(base, opts dict)]
        Output of parse_hurst_spec for each method string.
    hurst_windows : dict[str, int]
        Window lengths per base method.
    cfg : dict
        Global config.
    """

    # --- 1) SG smooth ---
    sg_window = int(cfg["sg_window"])
    polyorder = int(cfg["polyorder"])
    if sg_window % 2 == 0:
        sg_window += 1  # savgol_filter requires odd window

    smoothed_series = pd.Series(
        savgol_filter(raw_series.values, sg_window, polyorder),
        index=raw_series.index
    )

    # debug assert
    if cfg.get("verbose", False):
        print("[compute_features] SG smoothing applied before PE/Hurst.")

    rows: List[Dict[str, Any]] = []

    # cache z-scored variants: key=(id(smoothed_series), z_win) -> ndarray
    z_cache: Dict[Tuple[int, int], np.ndarray] = {}

    for i in idxs:
        row: Dict[str, Any] = {"idx": i, "value": smoothed_series.iat[i]}

        # --- PE (on smoothed data) ---
        if cfg.get("run_PE", True):
            start_pe = max(0, i - pe_window + 1)
            seg_pe = smoothed_series.iloc[start_pe:i + 1].values
            row["PE"] = permutation_entropy(seg_pe, m=cfg["m"], delay=cfg["delay"])
            row["pe_roll"] = row["PE"]
        else:
            row["PE"] = np.nan
            row["pe_roll"] = np.nan

        # --- Hursts ---
        for base, opts in hurst_specs:
            func = _HURST_FUNCS.get(base)
            if func is None:
                continue

            win = hurst_windows.get(base, 20)
            seg_start = max(0, i - win + 1)

            # choose array (SG only vs SG+Z)
            if opts.get("z", False):
                z_win = opts.get("z_window") or cfg.get("hurst_z_window", 100)
                key = (id(smoothed_series), int(z_win))
                if key not in z_cache:
                    z_cache[key] = zscore_rolling(smoothed_series.values, int(z_win))
                arr = z_cache[key]
            else:
                arr = smoothed_series.values

            seg = arr[seg_start:i + 1]
            h_val = func(seg)

            if opts.get("perst", False):
                h_val = persistence_transform(h_val)

            row[base] = h_val

        rows.append(row)

    return pd.DataFrame(rows)
