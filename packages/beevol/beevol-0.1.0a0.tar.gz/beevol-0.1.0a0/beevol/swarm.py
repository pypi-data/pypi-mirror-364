# beevol/swarm.py
from __future__ import annotations

import importlib.resources
from typing import List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from scipy.signal import savgol_filter

import beevol.hive as hive
from beevol.cli import parse_args, load_config


def sting(
    data_source: str = hive.DEFAULT_CONFIG["data_source"],
    config: dict | None = None,
    config_path: str | None = None,
    output: str | List[str] = "all",
    return_figs: bool = False,
    **cli_overrides,
) -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
    | Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List]
):

# ------------------------------------------------------------------
# 1) Build config
# ------------------------------------------------------------------

    cfg = hive.DEFAULT_CONFIG.copy()

    if config_path:
        try:
            with open(config_path) as f:
                cfg.update(yaml.safe_load(f))
        except FileNotFoundError:
            with importlib.resources.open_text("beevol", "config.yml") as f:
                cfg.update(yaml.safe_load(f))

    if config:
        cfg.update(config)

    if data_source is not None:
        cfg["data_source"] = data_source

    for k, v in cli_overrides.items():
        if v is not None:
            cfg[k] = v

# ------------------------------------------------------------------
# 2) Load data into {name: Series}
# ------------------------------------------------------------------

    if str(cfg["data_source"]).upper() == "TEST":
        series_map = {"TEST": hive.generate_series(cfg)}
    else:
        df = pd.read_csv(cfg["data_source"], parse_dates=True, index_col=0)

        targets = cfg.get("target_columns", ["value"])
        if isinstance(targets, str):
            targets = [targets]

        missing = [c for c in targets if c not in df.columns]
        if missing:
            raise ValueError(f"missing columns: {missing}")

        series_map = {c: df[c].astype(float) for c in targets}

# ------------------------------------------------------------------
# 3) Output options & constants
# ------------------------------------------------------------------

    out_opts = [output] if isinstance(output, str) else (output or [])
    if "all" in out_opts:
        out_opts = ["plots", "extrema_accuracy", "dfs"]

    hurst_win_keys = {
        "H_RS": "hurst_window_h_rs",
        "H_DFA": "hurst_window_h_dfa",
        "H_VT": "hurst_window_h_vt",
        "H_SP": "hurst_window_h_sp",
    }

    # Parse Hurst specs once
    hurst_specs = [hive.parse_hurst_spec(s) for s in cfg.get("run_hurst", [])]
    hurst_bases = sorted({base for base, _ in hurst_specs})

    full_frames: List[pd.DataFrame] = []
    pe_frames: List[pd.DataFrame] = []
    he_frames: List[pd.DataFrame] = []
    figs: List = []

# ------------------------------------------------------------------
# 4) Loop per target column
# ------------------------------------------------------------------

    for name, series in series_map.items():
    # (a) SG smooth for extrema detection (EXTREMA use SG’d stream)
        sg_window = int(cfg["sg_window"])
        polyorder = int(cfg["polyorder"])
        if sg_window % 2 == 0:
            sg_window += 1
        sm = pd.Series(
            savgol_filter(series.values, sg_window, polyorder),
            index=series.index,
        )

    # (b) Extrema detection on smoothed + alignment with raw
        pks_sm, trs_sm = hive.extract_extrema(sm, cfg["prominence"])
        pks_org, trs_org = hive.extract_extrema(series, cfg["prominence"])

        acc_p = hive.extrema_alignment_score(pks_org, pks_sm, cfg["tolerance"])
        acc_t = hive.extrema_alignment_score(trs_org, trs_sm, cfg["tolerance"])
        if cfg["verbose"] and ("extrema_accuracy" in out_opts or "plots" in out_opts or "dfs" in out_opts):
            print(f"[{name}] Peaks align {acc_p:.1%}, Troughs align {acc_t:.1%}")

    # (c) Hurst windows
        hurst_windows = {base: cfg[hurst_win_keys[base]] for base in hurst_bases}

    # (d) Feature tables at extrema
        # compute_features will SG-smooth internally (enforced pipeline)
        df_pks = hive.compute_features(
            raw_series=series,
            idxs=pks_sm,
            pe_window=cfg["entropy_window"],
            hurst_specs=hurst_specs,
            hurst_windows=hurst_windows,
            cfg=cfg,
        )
        df_trs = hive.compute_features(
            raw_series=series,
            idxs=trs_sm,
            pe_window=cfg["entropy_window"],
            hurst_specs=hurst_specs,
            hurst_windows=hurst_windows,
            cfg=cfg,
        )

        df_pks["target"] = name
        df_trs["target"] = name

        # -------- Fallback so each target is represented --------
        if df_pks.empty and df_trs.empty:
            base_cols = ["idx", "value", "PE", "pe_roll"] + [b for b, _ in hurst_specs]
            placeholder = {c: pd.NA for c in base_cols}
            placeholder["target"] = name
            df_pks = pd.DataFrame([placeholder])
            df_trs = pd.DataFrame([placeholder])
        # --------------------------------------------------------


    # (e) Build wide table for this target
        prefix = f"{name}__"
        full = pd.DataFrame(index=series.index)

        # Allocate PE columns
        full[f"{prefix}max_PE"] = pd.NA
        full[f"{prefix}min_PE"] = pd.NA

        # Allocate Hurst columns
        for base in hurst_bases:
            full[f"{prefix}max_{base}"] = pd.NA
            full[f"{prefix}min_{base}"] = pd.NA

        # Safe assign helper 
        def _put(df_src: pd.DataFrame, col_name: str, pos_idxs, dest_col: str):
            """Safely write df_src[col_name] into full[dest_col] at positional indices."""
            if col_name not in df_src.columns or df_src.empty or len(pos_idxs) == 0:
                return
            vals = df_src[col_name].to_numpy()
            n = min(len(vals), len(pos_idxs))
            if n == 0:
                return
            labels = series.index[pos_idxs[:n]]
            full.loc[labels, dest_col] = vals[:n]

        # Assign PE
        if cfg.get("run_PE", True):
            _put(df_pks, "pe_roll", pks_sm, f"{prefix}max_PE")
            _put(df_trs, "pe_roll", trs_sm, f"{prefix}min_PE")

        # Assign Hurst bases
        for base in hurst_bases:
            _put(df_pks, base, pks_sm, f"{prefix}max_{base}")
            _put(df_trs, base, trs_sm, f"{prefix}min_{base}")

    # (f) Interpolate & rolling mean
        interp = full.apply(pd.to_numeric, errors="coerce").interpolate()

        rolled = pd.DataFrame(index=series.index)
        if cfg.get("run_PE", True):
            rolled[f"{prefix}max_PE"] = interp[f"{prefix}max_PE"].rolling(
                cfg["entropy_window"], min_periods=1
            ).mean()
            rolled[f"{prefix}min_PE"] = interp[f"{prefix}min_PE"].rolling(
                cfg["entropy_window"], min_periods=1
            ).mean()

        for base in hurst_bases:
            win = hurst_windows[base]
            rolled[f"{prefix}max_{base}"] = interp[f"{prefix}max_{base}"].rolling(
                win, min_periods=1
            ).mean()
            rolled[f"{prefix}min_{base}"] = interp[f"{prefix}min_{base}"].rolling(
                win, min_periods=1
            ).mean()

        full_frames.append(rolled)
        pe_frames.append(df_pks)
        he_frames.append(df_trs)

    # (g) Optional plots
        if "plots" in out_opts or cfg["verbose"]:
            if cfg.get("run_PE", True):
                fig, ax = plt.subplots()
                ax.plot(rolled[f"{prefix}max_PE"], label="PE up")
                ax.plot(rolled[f"{prefix}min_PE"], label="PE down")
                ax.plot(
                    hive.divergence(rolled[f"{prefix}max_PE"], rolled[f"{prefix}min_PE"]),
                    "k:",
                    label="ΔPE",
                )
                ax.axhline(0, color="grey", lw=0.5)
                ax.set_title(f"{name} — Permutation Entropy")
                ax.legend()
                fig.tight_layout()
                fig.show()
                figs.append(fig)

            for base in hurst_bases:
                fig, ax = plt.subplots()
                ax.plot(rolled[f"{prefix}max_{base}"], label="up")
                ax.plot(rolled[f"{prefix}min_{base}"], label="down")
                ax.plot(
                    hive.divergence(
                        rolled[f"{prefix}max_{base}"], rolled[f"{prefix}min_{base}"]
                    ),
                    "k:",
                    label=f"Δ{base}",
                )
                ax.axhline(0, color="grey", lw=0.5)
                ax.set_title(f"{name} — Hurst {base}")
                ax.legend()
                fig.tight_layout()
                fig.show()
                figs.append(fig)

# ------------------------------------------------------------------
# 5) Concatenate outputs
# ------------------------------------------------------------------

    # 5) Concatenate outputs
    full_wide = pd.concat(full_frames, axis=1)

    # Filter out empties to avoid FutureWarning
    pe_frames_clean = [f for f in pe_frames if not f.empty]
    he_frames_clean = [f for f in he_frames if not f.empty]

    pe_long = (pd.concat(pe_frames_clean, axis=0).reset_index(drop=True)
            if pe_frames_clean else pd.DataFrame())
    he_long = (pd.concat(he_frames_clean, axis=0).reset_index(drop=True)
            if he_frames_clean else pd.DataFrame())


    if return_figs:
        return full_wide, pe_long, he_long, figs
    return full_wide, pe_long, he_long


def main() -> None:
    args = parse_args()
    cfg = load_config(args)
    sting(**cfg)


if __name__ == "__main__":
    main()
